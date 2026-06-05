# E-Commerce AI Competitor Monitoring

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![LangGraph](https://img.shields.io/badge/LangGraph-AI-blue)
![SQLite](https://img.shields.io/badge/SQLite-DB-lightgray)

An intelligent e-commerce competitor monitoring system powered by AI. This system automatically scrapes competitor websites, normalizes unstructured data using LangGraph and Pydantic, analyzes pricing trends, and provides actionable recommendations to maximize profit. It features a modern Next.js dashboard and Slack integration for real-time alerts.

## 🚀 Features

- **Automated Data Scraping:** Periodically visits competitor product pages to extract raw HTML/text data.
- **AI Data Normalization:** Uses LangGraph and OpenAI (GPT-4o-mini) with Pydantic structured outputs to cleanly parse messy HTML into a uniform schema (Competitor Name, Price, Discount, Stock status).
- **Intelligent Pricing Analysis:** An AI agent compares your current price with competitor prices, detects trends, and recommends whether to `raise`, `lower`, or `keep` your price.
- **Modern Dashboard:** Built with Next.js, Tailwind CSS, and Recharts to visualize price dynamics and AI recommendations.
- **Slack Alerts:** Instantly notifies your team in Slack when a price change is recommended.

## 🏗️ Architecture

1. **Backend (Python):**
   - **FastAPI** for robust and fast REST APIs.
   - **SQLModel & SQLite** for straightforward data storage.
   - **Httpx & BeautifulSoup** for web scraping.
   - **LangGraph & LangChain** for building the AI agent workflow.

2. **Frontend (TypeScript):**
   - **Next.js (App Router)** for a modern React experience.
   - **Tailwind CSS** for responsive styling.
   - **Recharts** for rendering competitor price charts.

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API Key

### 1. Clone the repository
```bash
git clone https://github.com/trigonosaurus-rgb/e-commerce-ai-monitoring.git
cd e-commerce-ai-monitoring
```

### 2. Backend Setup
```bash
# Create a virtual environment
python -m venv backend/venv

# Activate it (Windows)
backend\venv\Scripts\activate
# Activate it (Mac/Linux)
# source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here (optional)
```

### 4. Frontend Setup
```bash
cd frontend
npm install
```

## 🚀 Running the Project

### Start the Backend API
Open a terminal in the root folder:
```bash
# For Command Prompt (cmd.exe):
backend\venv\Scripts\activate

# For PowerShell (if you get an Execution Policy error):
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
backend\venv\Scripts\Activate.ps1

# Run the API
uvicorn backend.main:app --reload --port 8000
```

### Start the Frontend Dashboard
Open a new terminal in the `frontend` folder:
```bash
npm run dev
```

Visit `http://localhost:3000` to view the dashboard!

## 💡 How it works
1. When you click **"Run AI Analysis"**, the FastAPI backend triggers a background task.
2. The scraper visits the competitor URL and grabs the text data.
3. LangGraph runs node `normalize` to convert text -> Pydantic `ExtractedProductData`.
4. LangGraph runs node `analyze` to generate a `PricingRecommendation`.
5. Data is saved to SQLite, and an alert is dispatched to Slack.
6. The frontend automatically updates to show new graph data and the AI's recommendation.

## 📄 License
MIT License
