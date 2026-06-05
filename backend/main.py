import json
import asyncio
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List
from sse_starlette.sse import EventSourceResponse

from backend.database import create_db_and_tables, get_session
from backend.models import ResearchTask, Competitor, FinalRecommendation
from backend.scraper import scrape_site
from backend.agents import research_app

app = FastAPI(title="Autonomous E-Commerce AI Researcher")

# Allow CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

class TaskCreate(BaseModel):
    url: str

@app.post("/tasks")
def create_task(task_in: TaskCreate, session: Session = Depends(get_session)):
    task = ResearchTask(url=task_in.url, status="pending")
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(ResearchTask).order_by(ResearchTask.timestamp.desc())).all()
    results = []
    for t in tasks:
        results.append({
            "id": t.id,
            "url": t.url,
            "status": t.status,
            "niche": t.niche,
            "timestamp": t.timestamp
        })
    return results

@app.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(ResearchTask, task_id)
    if not task:
        return {"error": "Not found"}
    comps = session.exec(select(Competitor).where(Competitor.task_id == task_id)).all()
    recs = session.exec(select(FinalRecommendation).where(FinalRecommendation.task_id == task_id)).all()
    return {
        "task": task,
        "competitors": comps,
        "recommendations": recs[0] if recs else None
    }

@app.get("/stream_task/{task_id}")
async def stream_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(ResearchTask, task_id)
    if not task:
        return {"error": "Task not found"}

    async def event_generator():
        # Scrape user site
        yield {"data": json.dumps({"log": f"Starting research for {task.url}..."})}
        yield {"data": json.dumps({"log": "Scraping your website..."})}
        
        my_site_text = await scrape_site(task.url)
        if not my_site_text:
            yield {"data": json.dumps({"log": "Error: Could not scrape your website.", "status": "failed"})}
            return
            
        yield {"data": json.dumps({"log": "Successfully scraped your website. Starting AI analysis..."})}

        initial_state = {
            "url": task.url,
            "my_site_text": my_site_text,
            "niche_summary": "",
            "search_query": "",
            "competitor_urls": [],
            "competitors_data": [],
            "final_recommendation": "",
            "logs": []
        }

        # Run LangGraph streaming
        final_state = None
        async for event in research_app.astream(initial_state):
            # event is a dict mapping node_name -> state_updates
            for node_name, state_updates in event.items():
                if "logs" in state_updates and state_updates["logs"]:
                    # yield the latest log
                    yield {"data": json.dumps({"log": state_updates["logs"][-1]})}
                final_state = state_updates # keep track of the latest merged state

        # Save to DB
        if final_state:
            task.niche = final_state.get("niche_summary", "")
            task.search_query = final_state.get("search_query", "")
            task.status = "completed"
            session.add(task)
            
            for c_data in final_state.get("competitors_data", []):
                comp = Competitor(task_id=task.id, name=c_data["name"], url=c_data["url"], extracted_pricing_info=c_data["pricing_info"])
                session.add(comp)
                
            rec_text = final_state.get("final_recommendation", "")
            if rec_text:
                rec = FinalRecommendation(task_id=task.id, strategy="AI Strategy", actionable_steps=rec_text)
                session.add(rec)
                
            session.commit()
            
        yield {"data": json.dumps({"log": "Research completed!", "status": "completed"})}

    return EventSourceResponse(event_generator())
