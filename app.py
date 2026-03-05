import os
import streamlit as st
from dotenv import load_dotenv

from backend.github_loader import clone_repo, load_repo_files, cleanup_repo
from backend.embeddings import build_vector_store
from backend.rag_chain import build_rag_chain, analyze_errors
from backend.utils import is_valid_github_url, format_file_stats

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GitHub RAG Error Analyzer",
    page_icon="🔍",
    layout="wide",
)

# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #e05c00, #ff8c42);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-box {
        background: #1e1e2e;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #333;
    }
    .source-tag {
        display: inline-block;
        background: #2d2d3d;
        border-radius: 5px;
        padding: 2px 8px;
        margin: 2px;
        font-size: 0.8rem;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🔍 GitHub RAG Error Analyzer</div>', unsafe_allow_html=True)
st.markdown("**Paste a GitHub repo URL → Instantly find bugs, security issues & code smells using AI**")
st.divider()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="Free API key from console.groq.com"
)
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    st.divider()
    st.markdown("### 📌 How it works")
    st.markdown("""
1. Enter a public GitHub repo URL
2. Repo is cloned & code files are loaded
3. Files are chunked & embedded into FAISS
4. Claude analyzes code for errors via RAG
5. Results shown with source file references
    """)
    st.divider()
    st.markdown("**Supported Languages**")
    st.markdown("`Python` `JS/TS` `Java` `C/C++` `Go` `Ruby` `PHP` `Swift` `Kotlin` `Rust` `SQL` `YAML` and more")

# ── Main Input ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    github_url = st.text_input(
        "🔗 GitHub Repository URL",
        placeholder="https://github.com/username/repository",
        label_visibility="collapsed"
    )
with col2:
    analyze_btn = st.button("🚀 Analyze Repo", use_container_width=True, type="primary")

# Custom query
with st.expander("🎯 Custom Query (optional)"):
    custom_query = st.text_area(
        "Ask a specific question about the code:",
        placeholder="e.g. Find all SQL injection vulnerabilities in this codebase",
        height=80
    )

st.divider()

# ── Analysis ─────────────────────────────────────────────────────────────────
if analyze_btn:
    if not api_key:
        st.error("❌ Please enter your Groq API key in the sidebar.")
        st.stop()

    if not github_url.strip():
        st.error("❌ Please enter a GitHub repository URL.")
        st.stop()

    if not is_valid_github_url(github_url.strip()):
        st.error("❌ Invalid GitHub URL. Use format: `https://github.com/user/repo`")
        st.stop()

    repo_path = None
    try:
        with st.status("📥 Cloning repository...", expanded=True) as status:

            # Step 1: Clone
            st.write("Connecting to GitHub...")
            repo_path, repo_name = clone_repo(github_url.strip())
            st.write(f"✅ Cloned `{repo_name}` successfully")

            # Step 2: Load files
            st.write("📂 Loading code files...")
            documents = load_repo_files(repo_path)
            if not documents:
                st.error("No supported code files found in this repository.")
                st.stop()
            stats = format_file_stats(documents)
            st.write(f"✅ Loaded **{stats['total_files']} files**")

            # Step 3: Embed
            st.write("🧠 Building vector store (embedding code)...")
            vector_store = build_vector_store(documents)
            st.write("✅ Vector store ready")

            # Step 4: Build chain
            st.write("🔗 Initializing RAG chain...")
            chain = build_rag_chain(vector_store)  # returns (chain, retriever) tuple
            st.write("✅ RAG chain ready")

            # Step 5: Analyze
            st.write("🔍 Analyzing for errors (this may take 30-60s)...")
            query = custom_query.strip() if custom_query.strip() else None
            result = analyze_errors(chain, query)
            status.update(label="✅ Analysis complete!", state="complete")

        # ── Results ──────────────────────────────────────────────────────────
        st.subheader(f"📊 Repository Stats — `{repo_name}`")
        cols = st.columns(min(len(stats["by_extension"]) + 1, 6))
        cols[0].metric("Total Files", stats["total_files"])
        for i, (ext, count) in enumerate(list(stats["by_extension"].items())[:5], 1):
            cols[i].metric(f"{ext}", count)

        st.divider()
        st.subheader("🐛 Error Analysis Report")
        st.markdown(result["answer"])

        # Source files used
        if result["sources"]:
            st.divider()
            st.subheader("📁 Files Analyzed in This Response")
            sources_html = " ".join(
                f'<span class="source-tag">📄 {src}</span>'
                for src in sorted(result["sources"])
            )
            st.markdown(sources_html, unsafe_allow_html=True)

        # Download report
        st.divider()
        st.download_button(
            label="⬇️ Download Report as .txt",
            data=f"GitHub RAG Error Analysis Report\nRepo: {github_url}\n\n{result['answer']}\n\nFiles Analyzed:\n" + "\n".join(result["sources"]),
            file_name=f"{repo_name}_error_report.txt",
            mime="text/plain",
        )

    except RuntimeError as e:
        st.error(f"❌ {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.exception(e)
    finally:
        if repo_path:
            cleanup_repo(repo_path)

elif not analyze_btn:
    st.info("👆 Enter a GitHub repo URL above and click **Analyze Repo** to get started.")
    st.markdown("""
    #### 🧪 Example repos to try:
    - `https://github.com/donnemartin/interactive-coding-challenges`
    - `https://github.com/vinta/awesome-python`
    - Any of your own repositories!
    """)