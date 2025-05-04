import subprocess
import os
import sys
import platform
from datetime import datetime
from llm_agent import generate_commit_message

def get_git_diff_summary(repo_path):
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=repo_path)
        lines = result.stdout.strip().split("\n")

        added, modified, deleted = [], [], []

        for line in lines:
            if not line:
                continue

            # Handle untracked files
            if line.startswith("??"):
                added.append(line[3:])
                continue

            x = line[0]
            y = line[1]
            filepath = line[3:]

            if x == "A" or y == "A":
                added.append(filepath)
            elif x == "M" or y == "M":
                modified.append(filepath)
            elif x == "D" or y == "D":
                deleted.append(filepath)

        return {"added": added, "modified": modified, "deleted": deleted}
    except Exception as e:
        print(f"❌ Error getting git status: {e}")
        return {"added": [], "modified": [], "deleted": []}

def prompt_user_confirmation(message: str) -> bool:
    print("\n✏️ Suggested commit message:\n")
    print(f">>> {message}\n")
    confirm = input("✅ Do you want to commit with this message? (Y/n): ").strip().lower()
    return confirm in ["", "y", "yes"]

def commit_with_message(message: str, repo_path: str) -> bool:
    try:
        subprocess.run(["git", "add", "."], check=True, cwd=repo_path)
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=repo_path)
        print("✅ Commit completed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit failed: {e}")
        return False

def push_changes(repo_path: str) -> bool:
    try:
        subprocess.run(["git", "push"], check=True, cwd=repo_path)
        print("✅ Push successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git push failed: {e}")
        return False

def read_or_create_version(repo_path: str):
    version_file = os.path.join(repo_path, "version.txt")
    if not os.path.exists(version_file):
        print("📦 version.txt not found, creating new version starting from 0.0.0")
        with open(version_file, "w") as f:
            f.write("0.0.0")
        return "0.0.0"
    with open(version_file, "r") as f:
        return f.read().strip()

def bump_patch_version(version: str) -> str:
    major, minor, patch = map(int, version.strip().split("."))
    patch += 1
    return f"{major}.{minor}.{patch}"

def write_new_version(repo_path: str, version: str):
    version_file = os.path.join(repo_path, "version.txt")
    with open(version_file, "w") as f:
        f.write(version)

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def get_author(repo_path: str):
    try:
        result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, cwd=repo_path)
        return result.stdout.strip() or "unknown"
    except:
        return "unknown"

def get_env_info():
    python_version = ".".join(map(str, sys.version_info[:3]))
    system_info = f"{platform.system()}-{platform.release()}"
    return f"Python {python_version}, {system_info}"

def main():
    repo_path = os.getcwd()
    print(f"📁 Working in: {repo_path}")
    print("🔍 Scanning working directory changes...")

    diff = get_git_diff_summary(repo_path)
    if not any(diff.values()):
        print("✅ No changes detected. Nothing to commit.")
        return

    current_version = read_or_create_version(repo_path)

    prompt = (
        "You are a professional software developer. "
        "Given the following file changes, write a concise Git commit message in English, following the Conventional Commit format.\n"
        "- Use only one line.\n"
        "- Do NOT include file names or markdown.\n"
        "- Do NOT list all changes.\n"
        "- Focus on summarizing the purpose of the commit.\n\n"
    )
    if diff["added"]:
        prompt += f"Added files: {', '.join(diff['added'])}\n"
    if diff["modified"]:
        prompt += f"Modified files: {', '.join(diff['modified'])}\n"
    if diff["deleted"]:
        prompt += f"Deleted files: {', '.join(diff['deleted'])}\n"

    print("🤖 Generating commit message with Gemini...")
    message = generate_commit_message(prompt)

    timestamp = get_timestamp()
    author = get_author(repo_path)
    env_info = get_env_info()
    full_message = f"{message} (v{current_version} @{timestamp}) [by {author}, {env_info}]"

    print(f"\n📝 Final commit message:\n{full_message}")

    if prompt_user_confirmation(full_message):
        success_commit = commit_with_message(full_message, repo_path)
        if success_commit:
            success_push = push_changes(repo_path)
            if success_push:
                new_version = bump_patch_version(current_version)
                write_new_version(repo_path, new_version)
                print(f"🔁 Version bumped to v{new_version}")
    else:
        print("❌ Commit canceled by user.")

if __name__ == "__main__":
    main()
