import json
import asyncio
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List, Dict
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

# Global in-memory store for task logs to stream to frontend
task_logs_store: Dict[int, List[str]] = {}
task_status_store: Dict[int, str] = {} # "running", "completed", "failed"

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

class TaskCreate(BaseModel):
    url: str

async def run_research_background(task_id: int, url: str):
    task_status_store[task_id] = "running"
    task_logs_store[task_id] = []
    
    def log(msg: str):
        task_logs_store[task_id].append(msg)
        print(f"[Task {task_id}] {msg}")

    log(f"Starting research for {url}...")
    log("Scraping your website...")
    
    my_site_text = await scrape_site(url)
    if not my_site_text:
        log("Error: Could not scrape your website.")
        task_status_store[task_id] = "failed"
        return
        
    log("Successfully scraped your website. Starting AI analysis...")

    initial_state = {
        "url": url,
        "my_site_text": my_site_text,
        "niche_summary": "",
        "search_query": "",
        "competitor_urls": [],
        "competitors_data": [],
        "final_recommendation": "",
        "logs": []
    }

    final_state = None
    try:
        async for event in research_app.astream(initial_state):
            for node_name, state_updates in event.items():
                if "logs" in state_updates and state_updates["logs"]:
                    # extract the latest log
                    log_msg = state_updates["logs"][-1]
                    log(log_msg)
                final_state = state_updates
    except Exception as e:
        log(f"Agent execution failed: {e}")
        task_status_store[task_id] = "failed"
        return

    # Save to DB
    if final_state:
        # We need a new session since this is a background task
        with next(get_session()) as session:
            task = session.get(ResearchTask, task_id)
            if task:
                task.niche = final_state.get("niche_summary", "")
                task.search_query = final_state.get("search_query", "")
                task.status = "completed"
                session.add(task)
                
                for c_data in final_state.get("competitors_data", []):
                    comp = Competitor(
                        task_id=task.id, 
                        name=c_data["name"], 
                        url=c_data["url"], 
                        extracted_pricing_info=c_data["pricing_info"]
                    )
                    session.add(comp)
                    
                rec_text = final_state.get("final_recommendation", "")
                if rec_text:
                    rec = FinalRecommendation(
                        task_id=task.id, 
                        strategy="AI Strategy", 
                        actionable_steps=rec_text
                    )
                    session.add(rec)
                    
                session.commit()
                
    log("Research completed!")
    task_status_store[task_id] = "completed"

@app.post("/tasks")
def create_task(task_in: TaskCreate, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    task = ResearchTask(url=task_in.url, status="pending")
    session.add(task)
    session.commit()
    session.refresh(task)
    
    # Fire off background task
    background_tasks.add_task(run_research_background, task.id, task.url)
    
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
async def stream_task(task_id: int):
    async def event_generator():
        last_yielded_index = 0
        
        while True:
            # Check if task logs exist
            if task_id in task_logs_store:
                logs = task_logs_store[task_id]
                
                # Yield any new logs
                while last_yielded_index < len(logs):
                    yield {"data": json.dumps({"log": logs[last_yielded_index]})}
                    last_yielded_index += 1
                    
                # Check status
                status = task_status_store.get(task_id, "running")
                if status in ["completed", "failed"]:
                    yield {"data": json.dumps({"status": status})}
                    break
                    
            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())
