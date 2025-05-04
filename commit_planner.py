import subprocess
import os
import sys
import platform
from datetime import datetime
from llm_agent import generate_commit_message
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()


def get_git_diff_summary(repo_path):
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=repo_path)
        lines = result.stdout.strip().split("\n")

        added, modified, deleted = [], [], []

        for line in lines:
            if not line:
                continue

            if line.startswith("??"):
                added.append(line[3:])
                continue

            x, y = line[0], line[1]
            filepath = line[3:]

            if x == "A" or y == "A":
                added.append(filepath)
            elif x == "M" or y == "M":
                modified.append(filepath)
            elif x == "D" or y == "D":
                deleted.append(filepath)

        return {"added": added, "modified": modified, "deleted": deleted}
    except Exception as e:
        console.print(f"[red]❌ Error getting git status: {e}[/red]")
        return {"added": [], "modified": [], "deleted": []}


def get_diff_content(repo_path):
    try:
        result = subprocess.run(["git", "diff"], capture_output=True, text=True, cwd=repo_path)
        return result.stdout.strip()
    except Exception as e:
        console.print(f"[red]❌ Failed to get diff: {e}[/red]")
        return ""


def truncate_diff_text(diff_text, max_tokens=3000):
    lines = diff_text.strip().splitlines()
    result_lines = []
    current_tokens = 0

    for line in lines:
        line_tokens = len(line) // 4
        if current_tokens + line_tokens > max_tokens:
            break
        result_lines.append(line)
        current_tokens += line_tokens

    return "\n".join(result_lines)


def commit_with_message(message: str, repo_path: str) -> bool:
    # 清除潜在 git 锁文件
    lock_files = [
        ".git/index.lock",
        ".git/HEAD.lock",
        ".git/refs/heads/main.lock"
    ]
    for lock_file in lock_files:
        full_path = os.path.join(repo_path, lock_file)
        if os.path.exists(full_path):
            print(f"🧹 Removing stale lock: {full_path}")
            os.remove(full_path)

    # 检查是否已经有 staged 文件
    try:
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, cwd=repo_path)
        staged_files = result.stdout.strip().splitlines()
    except Exception as e:
        print(f"❌ Failed to check staged files: {e}")
        staged_files = []

    # 如果没有 staged 文件，执行 git add .
    if not staged_files:
        print("🌀 No files staged yet. Running `git add .` ...")
        try:
            subprocess.run(["git", "add", "."], check=True, cwd=repo_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Git add failed: {e}")
            return False
    else:
        print(f"✅ Detected {len(staged_files)} staged files. Skipping `git add .`")

    # 尝试提交
    try:
        subprocess.run(["git", "commit", "-m", message], check=True, cwd=repo_path)
        print("✅ Commit completed.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git commit failed: {e}")
        return False



def push_changes(repo_path: str) -> bool:
    try:
        subprocess.run(["git", "push"], check=True, cwd=repo_path)
        console.print("[green]✅ Push successful.[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Git push failed: {e}[/red]")
        return False


def read_or_create_version(repo_path: str):
    version_file = os.path.join(repo_path, "version.txt")
    if not os.path.exists(version_file):
        console.print("[cyan]📦 version.txt not found, creating new version starting from 0.0.0[/cyan]")
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
    console.print(f"[bold green]📁 Working in:[/bold green] {repo_path}")
    console.print("[bold blue]🔍 Scanning working directory changes...[/bold blue]")

    diff = get_git_diff_summary(repo_path)
    if not any(diff.values()):
        console.print("[green]✅ No changes detected. Nothing to commit.[/green]")
        return

    current_version = read_or_create_version(repo_path)

    prompt = (
        "You are a professional software engineer. "
        "Write a one-line Git commit message using the Conventional Commit format "
        "based on the following Git diff and file-level changes.\n\n"
    )

    if diff["added"]:
        prompt += f"Added files: {', '.join(diff['added'])}\n"
    if diff["modified"]:
        prompt += f"Modified files: {', '.join(diff['modified'])}\n"
    if diff["deleted"]:
        prompt += f"Deleted files: {', '.join(diff['deleted'])}\n"

    diff_text = truncate_diff_text(get_diff_content(repo_path), max_tokens=3000)
    prompt += f"\nGit diff:\n{diff_text}"

    console.print("[bold cyan]🤖 Generating commit message with Gemini...[/bold cyan]")
    message = generate_commit_message(prompt)

    timestamp = get_timestamp()
    author = get_author(repo_path)
    env_info = get_env_info()
    metadata = f"(by {author}, v{current_version} @{timestamp}, {env_info})"
    full_message = f"{message.strip()}\n\n{metadata}"

    console.print("\n[bold magenta]📝 Final commit message:[/bold magenta]")
    console.print(Panel(full_message, border_style="cyan", expand=False))

    if Confirm.ask("[green]✅ Do you want to commit with this message?[/green]"):
        if commit_with_message(full_message, repo_path):
            if push_changes(repo_path):
                new_version = bump_patch_version(current_version)
                write_new_version(repo_path, new_version)
                console.print(f"[bold yellow]🔁 Version bumped to v{new_version}[/bold yellow]")
    else:
        console.print("[red]❌ Commit canceled by user.[/red]")


if __name__ == "__main__":
    main()
