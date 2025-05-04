from github_api import get_recent_commits_diff

diffs = get_recent_commits_diff(branch="main", limit=1)

for diff in diffs:
    print("📄", diff["filename"])
    print("🔧 Status:", diff["status"])
    print("🔀 Patch:\n", diff["patch"])
    print("-" * 40)
