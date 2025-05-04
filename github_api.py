from github import Github
from git import Repo
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
g = Github(TOKEN)

def get_current_repo_full_name():
    repo = Repo(".")
    origin_url = repo.remotes.origin.url

    if origin_url.startswith("git@"):
        path = origin_url.split(":")[1]
    elif origin_url.startswith("https://"):
        path = origin_url.split("github.com/")[1]
    else:
        raise ValueError("Unsupported remote URL format")

    return path.replace(".git", "").strip()

def get_recent_commits_diff(branch="main", limit=1):
    repo_name = get_current_repo_full_name()
    repo = g.get_repo(repo_name)
    commits = repo.get_commits(sha=branch)[:limit]

    all_changes = []

    for commit in commits:
        files = commit.files
        for file in files:
            all_changes.append({
                "filename": file.filename,
                "status": file.status,
                "patch": file.patch
            })

    return all_changes
