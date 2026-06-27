import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_FOLDER = "data/github_issues"


# Start with repos that usually have real product/feature discussions.
# You can change these later.
REPOSITORIES = [
    {
        "owner": "calcom",
        "repo": "cal.com",
        "labels": ["feature", "enhancement"],
        "limit": 8
    },
    {
        "owner": "appwrite",
        "repo": "appwrite",
        "labels": ["feature", "enhancement"],
        "limit": 8
    },
    {
        "owner": "strapi",
        "repo": "strapi",
        "labels": ["feature request", "enhancement"],
        "limit": 8
    },
    {
        "owner": "supabase",
        "repo": "supabase",
        "labels": ["feature request", "enhancement"],
        "limit": 8
    }
]


def safe_filename(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return text[:80] if text else "github_issue"


def build_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ReqLens-RAG"
    }

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    return headers


def fetch_issue_comments(owner, repo, issue_number):
    """
    Fetches comments for one issue.
    We keep only a limited number so the file does not become huge.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"

    params = {
        "per_page": 5,
        "page": 1
    }

    response = requests.get(
        url,
        headers=build_headers(),
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        return []

    comments = response.json()

    cleaned_comments = []

    for comment in comments:
        body = comment.get("body", "")

        if body and len(body.strip()) > 30:
            cleaned_comments.append({
                "author": comment.get("user", {}).get("login", "unknown"),
                "created_at": comment.get("created_at", ""),
                "body": body.strip()
            })

    return cleaned_comments


def fetch_issues(owner, repo, label, limit=8):
    """
    Fetches GitHub issues for a repository and label.
    Skips pull requests because GitHub's issues endpoint can return PRs too.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    params = {
        "state": "open",
        "labels": label,
        "sort": "comments",
        "direction": "desc",
        "per_page": min(limit, 100),
        "page": 1
    }

    response = requests.get(
        url,
        headers=build_headers(),
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        print(f"Failed: {owner}/{repo} label={label}")
        print(f"Status code: {response.status_code}")
        print(response.text[:500])
        return []

    issues = response.json()
    real_issues = []

    for issue in issues:
        if "pull_request" in issue:
            continue

        body = issue.get("body", "")

        if not body or len(body.strip()) < 100:
            continue

        real_issues.append(issue)

        if len(real_issues) >= limit:
            break

    return real_issues


def save_issue_as_text(owner, repo, label, issue):
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    issue_number = issue.get("number")
    title = issue.get("title", "No title")
    body = issue.get("body", "")
    html_url = issue.get("html_url", "")
    state = issue.get("state", "")
    comments_count = issue.get("comments", 0)
    created_at = issue.get("created_at", "")
    updated_at = issue.get("updated_at", "")

    labels = [
        label_item.get("name", "")
        for label_item in issue.get("labels", [])
    ]

    comments = fetch_issue_comments(owner, repo, issue_number)

    comments_text = ""

    if comments:
        comments_text = "\n\nCOMMENTS / DISCUSSION:\n"

        for index, comment in enumerate(comments, start=1):
            comments_text += f"""
Comment {index}
Author: {comment["author"]}
Created At: {comment["created_at"]}
Body:
{comment["body"]}
"""

    filename = f"{owner}_{repo}_{issue_number}_{safe_filename(title)}.txt"
    file_path = os.path.join(OUTPUT_FOLDER, filename)

    content = f"""
SOURCE TYPE: GitHub Issue
REPOSITORY: {owner}/{repo}
ISSUE NUMBER: {issue_number}
ISSUE URL: {html_url}
STATE: {state}
FETCHED LABEL FILTER: {label}
ISSUE LABELS: {", ".join(labels)}
COMMENTS COUNT: {comments_count}
CREATED AT: {created_at}
UPDATED AT: {updated_at}

TITLE:
{title}

ISSUE BODY:
{body}
{comments_text}

REQUIREMENTS ANALYSIS TASK:
Analyze this GitHub issue as a software requirement or feature request.
Extract:
- Problem statement
- User need
- Confirmed requirements
- Assumptions
- User story
- Acceptance criteria
- Technical impact
- Frontend impact
- Backend impact
- Database impact
- API impact
- Risks
- Missing questions
- Implementation readiness
"""

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content.strip())

    print(f"Saved: {file_path}")


def main():
    total_saved = 0

    for repository in REPOSITORIES:
        owner = repository["owner"]
        repo = repository["repo"]
        labels = repository["labels"]
        limit = repository["limit"]

        for label in labels:
            print(f"\nFetching {owner}/{repo} issues with label: {label}")

            issues = fetch_issues(
                owner=owner,
                repo=repo,
                label=label,
                limit=limit
            )

            print(f"Found usable issues: {len(issues)}")

            for issue in issues:
                save_issue_as_text(owner, repo, label, issue)
                total_saved += 1

    print(f"\nDone. Saved {total_saved} GitHub issue files.")


if __name__ == "__main__":
    main()