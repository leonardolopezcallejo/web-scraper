# 🕸️ Web Scraping by Garaje

POC that allows scraping text from a URL, storing it in Azure Cognitive Search, and querying a language model (GPT) with related questions using semantic search (RAG: Retrieval-Augmented Generation)

---

## 🧰 Technology

- `FastAPI` para Python backend
- `BeautifulSoup` to scrap HTML text
- `Azure Cognitive Search` for indexing and retrieval
- `OpenAI GPT` (via Azure OpenAI) to answer questions
- `HTML + Vanilla JS` for an interactive frontend
- `.env` for API key configuration

---

## 🚀 How to Run the POC (from PowerShell)

### 0. Install Python and pip
```bash
winget install --id Python.Python.3 --source winget
python --version
pip --version
```

### 1. Clone the repository

```bash
git clone https://github.com/leonardolopezcallejo/web-scraper.git
cd web-scraper
```

### 2. Create virtual environment and install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Set environment variables
```bash
AZURE_SEARCH_ENDPOINT=https://<nombre>.search.windows.net
AZURE_SEARCH_KEY=<clave-api>
AZURE_SEARCH_INDEX=web-index

AZURE_OPENAI_KEY=<clave-api-openai>
AZURE_OPENAI_ENDPOINT=https://<tu-resource>.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
```

### 4. Open the HTML and run the app
```bash
uvicorn frontend_server:app --reload
uvicorn app.scraper_api:app --reload --port 8001
Start-Process "http://127.0.0.1:8000/"
```
