---
name: github-bulk-operations
description: "Mass query, filter, and patch GitHub repos via parallel Python scripts and gh jq pipelines."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Repositories, REST API, jq, Python, Automation]
---

# GitHub Bulk Operations

Workflows for scanning, filtering, and mass-updating dozens of GitHub repos quickly.

## Python REST API (Parallel Processing)
Ideal for deep inspection (e.g., pulling raw file contents across all repos) where `gh` is too slow or complex.

```python
import urllib.request
import json
import concurrent.futures

url = "https://api.github.com/users/USERNAME/repos?per_page=100&type=public"
# For >100 repos, handle pagination via 'Link' headers
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
repos = json.loads(urllib.request.urlopen(req).read().decode())

def inspect_repo(repo):
    name = repo['name']
    branch = repo['default_branch']
    # Example: fetch README
    readme_url = f"https://raw.githubusercontent.com/USERNAME/{name}/{branch}/README.md"
    try:
        req = urllib.request.Request(readme_url, headers={'User-Agent': 'Mozilla/5.0'})
        content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
        return {"repo": name, "size": len(content)}
    except:
        return {"repo": name, "size": 0}

# ThreadPoolExecutor is perfect for network I/O
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Filter out forks inline
    results = list(executor.map(inspect_repo, [r for r in repos if not r['fork']]))
```

## `gh` CLI One-liners (Quick Analytics & Bulk Updates)

**Repo Counts**
```bash
gh api users/USERNAME --jq '.public_repos'
```

**Top Repos (Sort & Filter)**
```bash
# Top 5 by stars, excluding forks
gh api users/USERNAME/repos --paginate --jq '
  map(select(.fork == false)) | 
  sort_by(.stargazers_count) | 
  reverse | .[0:5] | .[] | 
  "\(.name): \(.stargazers_count) stars"
'
```

**Bulk Property Updates**
```bash
# Make a list of repos private
for repo in repo1 repo2 repo3; do
  gh api -X PATCH repos/USERNAME/$repo -f private=true
done
```