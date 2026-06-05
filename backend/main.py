from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import List

from backend.database import create_db_and_tables, get_session
from backend.models import Product, CompetitorPrice, Recommendation
from backend.scraper import scrape_competitor_site
from backend.agents import run_ecommerce_agent
from backend.slack import send_slack_alert

app = FastAPI(title="E-Commerce AI Monitoring API")

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
    # Seed some mock data if DB is empty
    with next(get_session()) as session:
        product = session.exec(select(Product)).first()
        if not product:
            p1 = Product(name="Test Book: A Light in the Attic", my_price=55.00, url="https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html")
            session.add(p1)
            session.commit()

class ProductCreate(BaseModel):
    name: str
    my_price: float
    url: str

@app.get("/products")
def read_products(session: Session = Depends(get_session)):
    products = session.exec(select(Product)).all()
    results = []
    for p in products:
        prices = session.exec(select(CompetitorPrice).where(CompetitorPrice.product_id == p.id).order_by(CompetitorPrice.timestamp.desc())).all()
        recs = session.exec(select(Recommendation).where(Recommendation.product_id == p.id).order_by(Recommendation.timestamp.desc())).all()
        results.append({
            "id": p.id,
            "name": p.name,
            "my_price": p.my_price,
            "url": p.url,
            "competitor_prices": prices,
            "latest_recommendation": recs[0] if recs else None
        })
    return results

@app.post("/products")
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    db_product = Product(name=product.name, my_price=product.my_price, url=product.url)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

async def run_scan_task(product_id: int):
    # This runs in the background
    with next(get_session()) as session:
        product = session.get(Product, product_id)
        if not product or not product.url:
            return
        
        # 1. Scrape
        raw_html = await scrape_competitor_site(product.url)
        if not raw_html:
            print(f"Failed to scrape {product.url}")
            return
        
        # 2. Run LangGraph Agent
        result = run_ecommerce_agent(
            raw_html=raw_html,
            url=product.url,
            my_price=product.my_price,
            my_product_name=product.name
        )
        
        if result.get("error"):
            print(f"Agent Error: {result['error']}")
            return
            
        extracted_data = result.get("extracted_data")
        recommendation = result.get("recommendation")
        
        # 3. Save Competitor Price
        if extracted_data:
            comp_price = CompetitorPrice(
                product_id=product.id,
                competitor_name=extracted_data.competitor_name,
                price=extracted_data.price,
                discount_price=extracted_data.discount_price,
                in_stock=extracted_data.in_stock,
                url=product.url
            )
            session.add(comp_price)
        
        # 4. Save Recommendation & Notify
        if recommendation:
            rec_entry = Recommendation(
                product_id=product.id,
                action=recommendation.action,
                suggested_price=recommendation.suggested_price,
                reason=recommendation.reason
            )
            session.add(rec_entry)
            
            # Send Slack alert if action is required
            if recommendation.action in ['raise', 'lower']:
                alert_msg = f"🔔 *Pricing Alert for {product.name}*\n" \
                            f"Action: *{recommendation.action.upper()}*\n" \
                            f"Suggested Price: ${recommendation.suggested_price}\n" \
                            f"Reason: {recommendation.reason}"
                await send_slack_alert(alert_msg)
                
        session.commit()

@app.post("/trigger_scan/{product_id}")
async def trigger_scan(product_id: int, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        return {"error": "Product not found"}
    
    background_tasks.add_task(run_scan_task, product_id)
    return {"message": f"Scan triggered for product {product_id}"}
