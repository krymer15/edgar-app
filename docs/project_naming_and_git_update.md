📋 Safe Harbor Edgar AI App Project
Project Naming and Git Strategy Update (April 2025)

✅ Official Project Folder:
edgar-app/

All development work is now under the edgar-app/ folder.

The old filing-engine/ project name is deprecated and no longer used.

GitHub repository is properly linked to edgar-app.

All future GPT conversations, commits, diagrams, and planning must refer to edgar-app as the project.

🛠 File Placement and Documentation Rules

Save this document in your repo at:

```
edgar-app/docs/project_naming_and_git_update.txt
```
Rules:

Keep updated documentation about naming, repo structure, and migrations inside /docs/.

Use this file for onboarding, handoffs, or GPT project context going forward.

📋 Git Strategy Update for Edgar-App

GitHub Repo: https://github.com/krymer15/edgar-app.git

Active Development Branch: main

Git Remote: origin (already configured)

✅ Common Git Commands:
```
# Stage all changes (modified, deleted, new)
git add -A

# Commit with a clear message
git commit -m "Short description of the change"

# Push to GitHub
git push
```

✅ Best Practices:

Always run git status before pushing.

.env and all secret files are ignored automatically via .gitignore.

✨ Purpose:
This document formalizes the active project structure and version control process for the Safe Harbor Edgar AI App ("edgar-app/").