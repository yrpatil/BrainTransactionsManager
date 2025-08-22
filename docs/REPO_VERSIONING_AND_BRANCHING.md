## Versioning and Branching Standards (V1)

This repository follows simple, predictable rules so agents can maintain it reliably.

### Semantic Versioning
- We use `MAJOR.MINOR.PATCH` (e.g., `1.0.0`, `1.1.0`, `1.1.1`).
- Bump rules:
  - MAJOR: Breaking API/DB changes or significant architectural shifts
  - MINOR: Backward-compatible features
  - PATCH: Backward-compatible bug fixes and docs-only changes

### Tags and Releases
- Tags are prefixed with `v`: `v1.0.0`, `v1.1.0`, `v1.1.1`.
- Each release updates:
  - `VERSION` file (single line)
  - `setup.py` version field
  - `CHANGELOG.md` entries for the release
- Create a Git tag and (optionally) a GitHub Release.

### Branch Naming
- `main`: Always stable; only merged via release or hotfix branches.
- `release/<version>`: Release preparation branches.
  - Example: `release/1.1.0`
  - Purpose: finalize docs, bump versions, smoke tests before tagging
- `feature/<short-kebab>`: New features or improvements.
  - Examples: `feature/rest-resource-aliases`, `feature/strategy-summary-pnl`
- `hotfix/<short-kebab>` or `hotfix/<version>`: Urgent fixes on `main`.
  - Examples: `hotfix/fix-json-serialization`, `hotfix/1.1.1`

### Simple Release Flow (Normal Release)
1. Create branch: `git checkout -b release/1.1.0`
2. Update versions: `VERSION`, `setup.py`, and add `CHANGELOG.md` entry
3. Verify server start, basic smoke (health, a tool, a resource)
4. Merge `release/1.1.0` → `main` via PR
5. Tag: `git tag -a v1.1.0 -m "v1.1.0" && git push --tags`

### Hotfix Flow
1. Create branch from `main`: `git checkout -b hotfix/1.1.1`
2. Implement fix; bump PATCH in `VERSION` and `setup.py`, update `CHANGELOG.md`
3. Merge `hotfix/1.1.1` → `main`
4. Tag: `git tag -a v1.1.1 -m "v1.1.1" && git push --tags`

### Commit Hygiene
- Prefer concise, descriptive commits (scope: message)
- For visible changes, include one of: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`

### Database Changes
- Keep DDL in `database/ddl/` and migrations in `database/migrations/`
- For breaking schema changes, require MAJOR bump and clear upgrade notes in `CHANGELOG.md`

### Notes
- This document may become partially outdated as the system evolves. Treat it as the source of truth for the intended flow; adjust pragmatically when needed.

