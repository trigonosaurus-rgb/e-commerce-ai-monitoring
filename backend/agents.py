import os
from typing import TypedDict, Annotated, Sequence, Optional
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Ensure API key is loaded
from dotenv import load_dotenv
load_dotenv()

# Data structures
class ExtractedProductData(BaseModel):
    competitor_name: str = Field(description="Name of the competitor store")
    name: str = Field(description="Product name")
    price: float = Field(description="Current selling price as a float")
    discount_price: Optional[float] = Field(None, description="Discounted price if applicable, else null")
    in_stock: bool = Field(description="Whether the product is currently in stock")

class PricingRecommendation(BaseModel):
    action: str = Field(description="Action to take: 'raise', 'lower', or 'keep'")
    suggested_price: float = Field(description="The suggested new price")
    reason: str = Field(description="Explanation for the recommendation")

class AgentState(TypedDict):
    raw_html: str
    url: str
    my_price: float
    my_product_name: str
    extracted_data: Optional[ExtractedProductData]
    recommendation: Optional[PricingRecommendation]
    error: Optional[str]

# Nodes
def normalize_data_node(state: AgentState):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(ExtractedProductData)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert data extractor. Extract product details from the given raw HTML text."),
        ("user", "URL: {url}\n\nHTML/Text:\n{raw_html}")
    ])
    
    chain = prompt | structured_llm
    try:
        result = chain.invoke({"url": state["url"], "raw_html": state["raw_html"]})
        return {"extracted_data": result}
    except Exception as e:
        return {"error": str(e)}

def analyze_pricing_node(state: AgentState):
    if state.get("error") or not state.get("extracted_data"):
        return {"recommendation": None}
    
    extracted = state["extracted_data"]
    my_price = state["my_price"]
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(PricingRecommendation)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an e-commerce pricing expert. Compare our product with the competitor's product and provide a pricing recommendation to maximize profit while staying competitive."),
        ("user", """
        Our Product: {my_product_name}
        Our Price: ${my_price}
        
        Competitor Store: {competitor_name}
        Competitor Product: {competitor_product_name}
        Competitor Price: ${competitor_price}
        Competitor Discount Price: {competitor_discount_price}
        Competitor In Stock: {in_stock}
        """)
    ])
    
    chain = prompt | structured_llm
    try:
        result = chain.invoke({
            "my_product_name": state["my_product_name"],
            "my_price": my_price,
            "competitor_name": extracted.competitor_name,
            "competitor_product_name": extracted.name,
            "competitor_price": extracted.price,
            "competitor_discount_price": extracted.discount_price if extracted.discount_price else "None",
            "in_stock": extracted.in_stock
        })
        return {"recommendation": result}
    except Exception as e:
        return {"error": str(e)}

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("normalize", normalize_data_node)
workflow.add_node("analyze", analyze_pricing_node)

workflow.add_edge(START, "normalize")
workflow.add_edge("normalize", "analyze")
workflow.add_edge("analyze", END)

app = workflow.compile()

def run_ecommerce_agent(raw_html: str, url: str, my_price: float, my_product_name: str):
    initial_state = {
        "raw_html": raw_html,
        "url": url,
        "my_price": my_price,
        "my_product_name": my_product_name,
        "extracted_data": None,
        "recommendation": None,
        "error": None
    }
    result = app.invoke(initial_state)
    return result
