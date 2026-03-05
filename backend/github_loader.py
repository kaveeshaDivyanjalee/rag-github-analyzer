import os
import shutil
import tempfile
from pathlib import Path
from git import Repo

# File extensions to analyze for errors
SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs",
    ".go", ".rb", ".php", ".swift", ".kt", ".rs",
    ".jsx", ".tsx", ".html", ".css", ".yaml", ".yml",
    ".json", ".sh", ".bash", ".sql"
}

def clone_repo(github_url: str) -> tuple[str, str]:
    """Clone a GitHub repo to a temp directory. Returns (temp_dir, repo_name)."""
    temp_dir = tempfile.mkdtemp()
    try:
        repo_name = github_url.rstrip("/").split("/")[-1].replace(".git", "")
        Repo.clone_from(github_url, temp_dir, depth=1)
        return temp_dir, repo_name
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to clone repository: {e}")

def load_repo_files(repo_path: str) -> list[dict]:
    """Walk repo and load all supported code files."""
    documents = []
    repo_root = Path(repo_path)

    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".idea", ".vscode"}

    for file_path in repo_root.rglob("*"):
        # Skip hidden/build dirs
        if any(part in skip_dirs for part in file_path.parts):
            continue
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        # Skip very large files (>500KB)
        if file_path.stat().st_size > 500_000:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            relative_path = str(file_path.relative_to(repo_root))
            documents.append({
                "content": content,
                "source": relative_path,
                "extension": file_path.suffix.lower(),
                "size": file_path.stat().st_size,
            })
        except Exception:
            continue

    return documents

def cleanup_repo(repo_path: str):
    """Remove cloned repo from disk."""
    shutil.rmtree(repo_path, ignore_errors=True)