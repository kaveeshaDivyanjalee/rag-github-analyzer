# 🔍 GitHub RAG Error Analyzer

Analyze any GitHub repository for bugs, security vulnerabilities, and code quality issues using RAG (Retrieval-Augmented Generation) powered by LLaMA 3.3 (Groq) and FAISS.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your **free** Groq API key at: https://console.groq.com

### 3. Run the app
```bash
streamlit run app.py
```

## Features
- 🔗 Paste any public GitHub repo URL
- 📂 Automatically clones & indexes all code files
- 🧠 Embeds code locally using HuggingFace `all-MiniLM-L6-v2` (no API key needed)
- 🐛 LLaMA 3.3 70B detects bugs, security flaws, and anti-patterns
- 💡 Provides fix suggestions per issue with file references
- ⬇️ Download the full report as `.txt`
- 🎯 Supports custom queries for targeted analysis

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| LLM | LLaMA 3.3 70B (Groq - Free) |
| Embeddings | all-MiniLM-L6-v2 (HuggingFace - Local) |
| Vector DB | FAISS |
| RAG Framework | LangChain |
| Repo Cloning | GitPython |

## Supported Languages
`Python` `JavaScript` `TypeScript` `Java` `C/C++` `Go` `Ruby` `PHP` `Swift` `Kotlin` `Rust` `SQL` `YAML` and more

## Example Queries
- `Find all hardcoded passwords and API keys`
- `Find all potential runtime errors and missing error handlers`
- `Are there any SQL injection or security vulnerabilities?`
- `Find all functions with incorrect time complexity`
- `Find all TODO and FIXME comments`

## Project Structure
```
rag-github-analyzer/
├── app.py                  # Streamlit frontend
├── backend/
│   ├── __init__.py
│   ├── github_loader.py    # Clone & load GitHub repo files
│   ├── embeddings.py       # Chunking + vector store
│   ├── rag_chain.py        # RAG chain + error detection
│   └── utils.py            # Helper utilities
├── .env                    # API keys (not committed to git)
├── requirements.txt
└── README.md
```

## Notes
- Works on **public repositories** only
- First run downloads the embedding model (~90MB), cached after that
- Large repos may take 1–2 minutes to clone and embed