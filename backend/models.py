from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import datetime as dt

class ResearchTaskBase(SQLModel):
    url: str = Field(index=True)
    niche: Optional[str] = None
    search_query: Optional[str] = None
    status: str = Field(default="pending") # pending, analyzing, searching, scraping, completed
    timestamp: dt.datetime = Field(default_factory=dt.datetime.utcnow)

class ResearchTask(ResearchTaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    competitors: List["Competitor"] = Relationship(back_populates="task")
    recommendations: List["FinalRecommendation"] = Relationship(back_populates="task")

class CompetitorBase(SQLModel):
    name: str
    url: str
    extracted_pricing_info: str

class Competitor(CompetitorBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="researchtask.id")
    task: ResearchTask = Relationship(back_populates="competitors")

class FinalRecommendationBase(SQLModel):
    strategy: str
    actionable_steps: str

class FinalRecommendation(FinalRecommendationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="researchtask.id")
    task: ResearchTask = Relationship(back_populates="recommendations")
