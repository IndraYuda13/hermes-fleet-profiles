---
name: github-profile-management
description: SOP for managing and formatting GitHub profile READMEs and bulk repository operations.
---

# GitHub Profile & Bulk Operations

This skill covers cleanup of GitHub profile READMEs (`{username}/{username}/README.md`) and bulk repository management via the `gh` CLI.

## Profile README Cleanup

When the user asks to review or improve their profile README:
1. **Remove redundant lists**: If there is a table of "Featured Projects" and a separate list of "Selected Public Repositories" that contain mostly the same items, merge the unique items into the table and delete the redundant list.
2. **Remove internal/meta notes**: Delete paragraphs explaining *how* the README is built. That is internal context, not public-facing content.
3. **Remove obvious information**: Delete items like `- GitHub: **Username**` from the "About" section.
4. **Group related items**: When adding multiple related repositories to a featured projects table, group them in a single row under a category (e.g., `| Automation & Bots | [bot1](url1), [bot2](url2) |`).
5. **Editing Strategy**: If `patch` fails, fallback to targeted `sed` commands for deletions and `cat << 'EOF' >>` for additions.

## Bulk Repository Operations

### Visibility Update (Public to Private)
When making multiple repositories private:
1. **Execute via `gh api` in a loop**: Use `gh api -X PATCH repos/{owner}/{repo} -f private=true`.
2. **Suppress noise**: Redirect output to `/dev/null` so the terminal output isn't flooded with full JSON responses for every repo.

Example:
```bash
for repo in repo1 repo2 repo3; do
  echo "Setting $repo to private..."
  gh api -X PATCH repos/IndraYuda13/$repo -f private=true > /dev/null
done
```
