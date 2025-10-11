# Branch Protection Setup

This document describes the recommended branch protection rules for this repository.

## How to Enable (Repository Owner)

Go to: **Settings → Branches → Add branch protection rule**

---

## Main Branch Protection

### Branch name pattern: `main`

#### Required Settings

**Protect matching branches:**
- ✅ Require a pull request before merging
  - ✅ Require approvals: **1**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners (if CODEOWNERS file exists)

- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - **Required checks:**
    - `Test Suite (3.11)`
    - `Test Suite (3.12)`
    - `Security Checks`
    - `Code Quality`

- ✅ Require conversation resolution before merging

- ✅ Require signed commits (optional but recommended)

- ✅ Require linear history

- ✅ Include administrators (recommended for hobby projects)

**Rules applied to everyone including administrators:**
- ✅ Restrict who can push to matching branches
  - Only repository owner/collaborators

- ✅ Allow force pushes: **No**

- ✅ Allow deletions: **No**

---

## Develop Branch Protection (Optional)

### Branch name pattern: `develop`

#### Required Settings

**Protect matching branches:**
- ✅ Require a pull request before merging
  - Require approvals: **0** (can be merged without review for faster iteration)

- ✅ Require status checks to pass before merging
  - **Required checks:**
    - `Test Suite (3.11)`
    - `Code Quality`

- ✅ Allow force pushes: **Yes** (only for feature branches)

---

## Why These Settings?

### Main Branch
- **Require PR + 1 approval**: Prevents accidental direct pushes to production
- **Require tests to pass**: Ensures code quality
- **No force push**: Prevents history rewriting
- **No deletion**: Protects main branch from accidental deletion
- **Linear history**: Keeps git history clean and readable

### Develop Branch (Optional)
- **Less strict**: Allows faster iteration for development
- **Still requires tests**: Maintains code quality
- **Allows force push**: Enables rebasing feature branches

---

## Additional Security

### Enable Dependabot Alerts
1. Go to **Settings → Security & analysis**
2. Enable:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates

### Enable Secret Scanning
1. Go to **Settings → Security & analysis**
2. Enable:
   - ✅ Secret scanning
   - ✅ Push protection (prevents committing secrets)

### Add CODEOWNERS (Optional)
Create `.github/CODEOWNERS`:
```
# Require review from owner for all changes
* @ESJavadex

# Critical files require owner review
/.github/ @ESJavadex
/src/ree_mcp/domain/ @ESJavadex
/pyproject.toml @ESJavadex
/LICENSE @ESJavadex
```

---

## Testing Protection Rules

After enabling, test by:

1. Creating a feature branch
2. Making a change
3. Opening a pull request
4. Verifying that:
   - ✅ Tests must pass
   - ✅ Cannot merge without approval
   - ✅ Cannot push directly to main

---

## Notes

- These rules apply to the **repository owner** too (if "Include administrators" is checked)
- For hobby projects, keeping rules strict helps maintain quality
- Rules can be adjusted as the project evolves
- CI/CD must be passing before rules are enabled (or initial setup will fail)
