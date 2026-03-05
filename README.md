# 🔍 GitHub RAG Error Analyzer

Analyze any GitHub repository for bugs, security vulnerabilities, and code quality issues using RAG (Retrieval-Augmented Generation) powered by GPT-4o and FAISS.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API key
Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the app
```bash
streamlit run app.py
```

## Features
- 🔗 Paste any public GitHub repo URL
- 📂 Automatically clones & indexes all code files
- 🧠 Embeds code with OpenAI embeddings into FAISS
- 🐛 GPT-4o detects bugs, security flaws, and anti-patterns
- 💡 Provides fix suggestions per issue
- ⬇️ Download the full report as `.txt`

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| LLM | GPT-4o (OpenAI) |
| Embeddings | text-embedding-3-small |
| Vector DB | FAISS |
| RAG Framework | LangChain |
| Repo Cloning | GitPython |