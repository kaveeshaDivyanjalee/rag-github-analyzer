import re

def is_valid_github_url(url: str) -> bool:
    """Validate GitHub URL format."""
    pattern = r'^https?://github\.com/[\w\-\.]+/[\w\-\.]+(\.git)?/?$'
    return bool(re.match(pattern, url.strip()))

def format_file_stats(documents: list[dict]) -> dict:
    """Summarize loaded file stats."""
    ext_count = {}
    for doc in documents:
        ext = doc["extension"]
        ext_count[ext] = ext_count.get(ext, 0) + 1
    return {
        "total_files": len(documents),
        "by_extension": dict(sorted(ext_count.items(), key=lambda x: -x[1]))
    }