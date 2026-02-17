# Fabric Pitfalls

Lessons learned about common pitfalls when working with Microsoft Fabric.

---

## 2026-02-17 Missing `.platform` File for New Notebook/Lakehouse Artifacts

**Context**: IT domain restructure — creating new notebooks via Git (not Fabric UI)
**Problem**: After creating new notebook folders and content files in Git, Fabric Git sync did not import the artifacts. They were invisible in the workspace.
**Solution**: Every Fabric artifact must include a `.platform` file alongside its content. The `.platform` file declares the artifact type, display name, and a unique `logicalId` (UUID4). Without it, Fabric Git integration silently ignores the folder.
**Generalization**: Whenever creating any Fabric artifact in Git (Notebook, Lakehouse, DataPipeline), always create the `.platform` file first. Add a verification step after implementation: `find fabric/ -name "*.Notebook" -type d | while read d; do [ -f "$d/.platform" ] || echo "MISSING: $d"; done`
**Related**:
- Docs: `docs/platforms/fabric/pitfalls.md` (Missing .platform File section)
- Spec: SDD-20260217-it-dev-ddm-mock-data

**Status**: Generalized

---

## 2026-02-17 Pushing to Wrong Branch — Domain Workspaces Use Domain Branches

**Context**: IT dev deployment — pushed implementation to `main`, workspace never showed changes
**Problem**: Assumed `main` was the deployment target. Fabric `it_dev` workspace syncs to `it_dev` branch, not `main`.
**Solution**: Always match branch name to workspace name: `{domain}_dev` workspace → `{domain}_dev` branch. Run `git branch -a` to see all available branches and confirm the right target. Check Fabric workspace Git integration settings if unsure.
**Generalization**: In projects with per-domain branching, never default to pushing `main`. Always confirm which branch each workspace is watching before pushing.
**Related**:
- Docs: `docs/platforms/fabric/pitfalls.md` (Pushing to Wrong Branch section)

**Status**: Generalized

---

## 2026-02-17 Duplicate logicalId in .platform Files Blocks Fabric Sync

**Context**: IT dev deployment — Fabric sync failed with "Failed to fix duplicate IDs"
**Problem**: Placeholder UUID `a1b2c3d4-e5f6-7890-abcd-ef1234567890` was copy-pasted into both `lh_it_bronze_dev.Lakehouse/.platform` and `silver_transform_freshservice.Notebook/.platform`. Fabric rejected the sync.
**Solution**: (1) For existing Fabric artifacts: find the real logicalId in the most recent Fabric auto-commit on that branch (`git log --oneline | grep Committing`, then `git show <hash>:path/.platform`). (2) For new artifacts: generate a fresh UUID4 per artifact. (3) Verify uniqueness: `grep -r "logicalId" fabric/ --include=".platform" | sort -t: -k3`.
**Generalization**: All `.platform` logicalIds must be globally unique. Placeholder IDs are a deployment risk — always use real Fabric IDs for existing items and fresh UUIDs for new items.
**Related**:
- Docs: `docs/platforms/fabric/pitfalls.md` (Duplicate logicalId section)

**Status**: Generalized

---

## 2026-02-17 Wrong workspaceId in Pipeline TridentNotebook Activities

**Context**: IT dev deployment — pipelines failed with "One of its dependencies can't be found" during Update all
**Problem**: Pipeline `pipeline-content.json` used `workspaceId: "4681b1cd-..."` (real workspace ID) for same-workspace TridentNotebook activities. Fabric then resolves `notebookId` as a **physical item ID**, not a `logicalId` — which doesn't match what's in the notebook `.platform` files.
**Solution**: For TridentNotebook activities referencing notebooks in the **same workspace**, always use `workspaceId: "00000000-0000-0000-0000-000000000000"`. This tells Fabric to resolve `notebookId` as a `logicalId`, matching the notebook's `.platform` file entry. Fabric's own auto-commits always use the zero UUID for same-workspace references.
**Verification**: `grep -r "workspaceId" fabric/ --include="pipeline-content.json"` — every same-workspace entry must be `00000000-0000-0000-0000-000000000000`.
**Generalization**: Only use the real workspace ID when referencing notebooks in a **different** workspace (cross-workspace pipeline). For all same-workspace references, use the zero UUID placeholder.
**Related**:
- Docs: `docs/platforms/fabric/pitfalls.md`

**Status**: Generalized

---

## 2026-02-17 Fabric Auto-Commits Can Create Corrupted Nested Paths

**Context**: IT dev deployment — cherry-pick onto it_dev caused cascading conflicts due to `fabric/it/fabric/it/` nested path
**Problem**: Previous Fabric auto-commits had stored files at the wrong path (`fabric/it/fabric/it/` instead of `fabric/it/`). Not noticed until cherry-pick conflicted on these files.
**Solution**: Before applying changes to a domain branch: pull latest, inspect `find fabric/{domain} -type f | sort` for corrupted nesting, remove bad paths with `git rm -r --cached` + `rm -rf`, then re-apply correct files with `git checkout main -- fabric/{domain}/`.
**Generalization**: Never assume a Fabric domain branch has clean structure. Always inspect with `find` before cherry-picking or merging. Fabric Git auto-commits can go wrong if the workspace folder mapping changes.
**Related**:
- Docs: `docs/platforms/fabric/pitfalls.md` (Inspect Target Branch section)

**Status**: Generalized

---
