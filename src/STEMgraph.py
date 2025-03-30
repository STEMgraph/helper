import requests
import os
import re
from datetime import datetime
from tabulate import tabulate

ORG = "STEMgraph"
GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}" if TOKEN else None
}

def is_uuid(name):
    return bool(re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", name))

def get_repos():
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API}/orgs/{ORG}/repos?per_page=100&page={page}"
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Error fetching repos: {r.status_code} {r.text}")
            break
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def readme_starts_with_comment(repo):
    url = f"{GITHUB_API}/repos/{ORG}/{repo}/contents/README.md"
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        content = r.json()
        if content.get("encoding") == "base64":
            import base64
            decoded = base64.b64decode(content["content"]).decode("utf-8", errors="ignore")
            return decoded.strip().startswith("<!---")
    return False

def main():
    all_repos = get_repos()
    uuid_repos = [r for r in all_repos if is_uuid(r["name"])]
    matched = []
    
    for repo in uuid_repos:
        if readme_starts_with_comment(repo["name"]):
            matched.append({
                "description": repo["description"] or "(no description)",
                "link": repo["html_url"],
                "last updated": datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
            })

    print(tabulate(matched, headers="keys", tablefmt="github"))

if __name__ == "__main__":
    main()
