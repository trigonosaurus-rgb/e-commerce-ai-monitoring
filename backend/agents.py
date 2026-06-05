import os
import asyncio
from typing import TypedDict, Annotated, Sequence, Optional, List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults
from backend.scraper import scrape_site

# Ensure API key is loaded
from dotenv import load_dotenv
load_dotenv()

# State definitions
class CompetitorData(TypedDict):
    url: str
    name: str
    pricing_info: str

class AgentState(TypedDict):
    url: str
    my_site_text: str
    niche_summary: str
    search_query: str
    competitor_urls: List[str]
    competitors_data: List[CompetitorData]
    final_recommendation: str
    logs: List[str]

# Pydantic schemas for structured LLM outputs
class NicheAnalysisOutput(BaseModel):
    niche_summary: str = Field(description="A brief description of what this e-commerce site sells and who the target audience is.")
    search_query: str = Field(description="A highly optimized search query to find direct competitors. E.g., 'buy wireless headphones online store'")

class CompetitorExtractionOutput(BaseModel):
    name: str = Field(description="The name of the competitor store.")
    pricing_info: str = Field(description="A summary of the products and pricing found on the page.")

class FinalReportOutput(BaseModel):
    strategy: str = Field(description="General pricing/marketing strategy recommendation based on competitors.")
    actionable_steps: str = Field(description="Bullet points of concrete actions the user should take, referencing competitor URLs.")

# Nodes
async def analyze_niche_node(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(NicheAnalysisOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert e-commerce analyst. Look at the scraped text of the user's website and determine their niche. Generate a search query to find their competitors."),
        ("user", "User's Website URL: {url}\n\nWebsite Content:\n{text}")
    ])
    
    chain = prompt | structured_llm
    
    # Text length limit to avoid token limits for very large pages
    text_content = state["my_site_text"][:20000]
    result = await chain.ainvoke({"url": state["url"], "text": text_content})
    
    logs = state.get("logs", [])
    logs.append(f"Analyzed niche. Summary: {result.niche_summary}")
    logs.append(f"Generated search query: '{result.search_query}'")
    
    return {
        "niche_summary": result.niche_summary,
        "search_query": result.search_query,
        "logs": logs
    }

async def search_competitors_node(state: AgentState):
    query = state["search_query"]
    logs = state.get("logs", [])
    logs.append(f"Executing Tavily web search for: '{query}'")
    
    try:
        tavily = TavilySearchResults(max_results=3)
        results = await tavily.ainvoke({"query": query})
        competitor_urls = [r["url"] for r in results if "url" in r]
    except Exception as e:
        logs.append(f"Tavily search failed (check API key): {str(e)}")
        competitor_urls = []
        
    logs.append(f"Found {len(competitor_urls)} potential competitor URLs via Tavily.")
    
    return {
        "competitor_urls": competitor_urls,
        "logs": logs
    }

async def scrape_competitors_node(state: AgentState):
    urls = state["competitor_urls"]
    logs = state.get("logs", [])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(CompetitorExtractionOutput)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract the store name and summarize the product offerings and pricing from the competitor's website content."),
        ("user", "URL: {url}\n\nContent:\n{text}")
    ])
    chain = prompt | structured_llm
    
    competitors_data = []
    
    for url in urls:
        logs.append(f"Scraping competitor: {url}")
        # Not yielding here because this is inside the node execution. 
        # For true streaming of internal loops, we rely on LangGraph's streaming of state updates between nodes.
        text = await scrape_site(url)
        if text:
            logs.append(f"Successfully scraped {url}. Analyzing content...")
            try:
                res = await chain.ainvoke({"url": url, "text": text})
                competitors_data.append({
                    "url": url,
                    "name": res.name,
                    "pricing_info": res.pricing_info
                })
            except Exception as e:
                logs.append(f"Failed to analyze {url}: {e}")
        else:
            logs.append(f"Failed to scrape {url} or site is empty.")
            
    return {"competitors_data": competitors_data, "logs": logs}

async def generate_recommendations_node(state: AgentState):
    logs = state.get("logs", [])
    logs.append("Generating final recommendations based on competitor data...")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(FinalReportOutput)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an elite e-commerce strategist. Compare the user's niche with the competitors we found. Provide a concrete strategy and actionable steps. You MUST reference the competitor URLs in your steps to prove your points."),
        ("user", """
        User's Niche: {niche}
        
        Competitors Data:
        {competitors}
        
        Provide the strategy and steps.
        """)
    ])
    
    chain = prompt | structured_llm
    comps_str = "\n".join([f"Name: {c['name']}\nURL: {c['url']}\nInfo: {c['pricing_info']}\n" for c in state["competitors_data"]])
    
    try:
        result = await chain.ainvoke({
            "niche": state["niche_summary"],
            "competitors": comps_str
        })
        final_rec = f"**Strategy:**\n{result.strategy}\n\n**Actionable Steps:**\n{result.actionable_steps}"
        logs.append("Report generation complete.")
    except Exception as e:
        final_rec = f"Error generating report: {e}"
        logs.append(final_rec)
        
    return {"final_recommendation": final_rec, "logs": logs}

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("analyze_niche", analyze_niche_node)
workflow.add_node("search_competitors", search_competitors_node)
workflow.add_node("scrape_competitors", scrape_competitors_node)
workflow.add_node("generate_recommendations", generate_recommendations_node)

workflow.add_edge(START, "analyze_niche")
workflow.add_edge("analyze_niche", "search_competitors")
workflow.add_edge("search_competitors", "scrape_competitors")
workflow.add_edge("scrape_competitors", "generate_recommendations")
workflow.add_edge("generate_recommendations", END)

research_app = workflow.compile()
