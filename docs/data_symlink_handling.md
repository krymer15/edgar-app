# 🔗 Handling `data/` and `test_data/` Symlinks in `edgar-app/`

## Overview

This project uses symlinked folders (`data/` and `test_data/`) to manage large datasets and temporary test artifacts that **should not be tracked by Git**.

Symlinks are useful for:
- Mounting large filing corpora from an external SSD
- Separating working data from source control
- Avoiding GitHub bloat and commit issues

---

## 🚫 Why These Folders Are Ignored

### `data/`
- Used for production-scale ingestion output
- Often symlinked to external drives (e.g., `D:/safeharbor-postgres/data/`)
- May be mounted by Docker volumes or indexed by file systems
- Can cause `Permission denied`, Git object errors, and OS-level locks

### `test_data/`
- Stores temporary or large files used in development and test workflows
- May be generated dynamically by parsers or test scripts
- Does not need to be versioned or uploaded to GitHub

---

## ✅ Git Ignore Setup

Ensure the following entries exist in `.gitignore`:

```
# Symlinked and dynamic data folders
data/
test_data/
```

This prevents accidental commits of:
- Raw filings
- Local test fixtures
- Mounted or symlinked content

---

## 🧹 If You Accidentally Added These Folders

If `data/` or `test_data/` were ever tracked by Git:

```bash
git rm -r --cached data/
git rm -r --cached test_data/
```

Then commit the `.gitignore` update:

```bash
git add .gitignore
git commit -m "Ignore symlinked data/ and test_data/ folders"
git push
```

---

## 🧠 Best Practices Going Forward

- Keep symlinked folders outside of Git tracking.
- Use `.gitignore` to block ingestion output and test artifacts.
- Commit only scripts, notebooks, configs, and code.

---

📁 Save this file at:
```
edgar-app/docs/data_symlink_handling.md
```
So future devs and GPT threads understand the exclusion policy clearly.