# Fabric Patterns

Lessons learned about effective patterns when working with Microsoft Fabric.

---

## 2026-02-17 Dual Lakehouse per Domain (Bronze + Curated)

**Context**: IT domain restructure — adding DDM and mock data support
**Problem**: Single lakehouse conflates raw PII bronze data with cleaned silver tables, making access control complex.
**Solution**: Use two lakehouses per domain: `lh_{domain}_bronze_{env}` (raw, restricted) and `lh_{domain}_curated_{env}` (silver + DDM views, analyst-accessible). Silver notebook reads bronze cross-lakehouse via `spark.table("lh_{domain}_bronze_dev.{table}")`.
**Generalization**: Any domain with PII should separate bronze (raw) from curated (silver+DDM). Single lakehouse is fine for non-PII domains.
**Related**:
- Docs: `docs/platforms/fabric/workspace-patterns.md` (Dual Lakehouse per Domain section)
- Spec: SDD-20260217-it-dev-ddm-mock-data

**Status**: Generalized

---

## 2026-02-17 DDM Views via pyodbc + Power BI Bearer Token

**Context**: IT domain DDM setup — deploying SQL views programmatically to curated lakehouse SQL endpoint
**Problem**: DDM views need to be deployed to the SQL Analytics Endpoint. The Fabric UI doesn't support CREATE VIEW from notebooks directly.
**Solution**: Use pyodbc with Power BI Bearer token (`mssparkutils.credentials.getToken("https://analysis.windows.net/powerbi/api")`) to connect to the SQL endpoint and run `CREATE OR ALTER VIEW`. Views use `IS_MEMBER('{aad_group}')` for column-level masking. Deploy from a `setup_ddm_views_{domain}` notebook run once after schema changes.
**Generalization**: Applies to any domain needing programmatic SQL view deployment on Fabric SQL Analytics Endpoint.
**Related**:
- Docs: `docs/platforms/fabric/onelake-patterns.md` (Dynamic Data Masking section)
- Spec: SDD-20260217-it-dev-ddm-mock-data

**Status**: Generalized

---

## 2026-02-17 `use_mock_data` Bool Parameter Pattern

**Context**: IT bronze notebook — enabling mock data mode for dev without live API calls
**Problem**: Bronze notebooks call live APIs, preventing dev testing without API credentials or real PII exposure.
**Solution**: Add `use_mock_data = False` as a notebook parameter. When `True`, loads from `Files/mock/{domain}/{entity}/data.json` instead. Pipeline passes the param so mock mode can be triggered without code changes.
**Generalization**: All bronze ingestion notebooks should support `use_mock_data`. Wire it through pipeline parameters so ops can trigger mock runs in CI/dev pipelines.
**Related**:
- Docs: `docs/platforms/fabric/notebook-standards.md` (use_mock_data Parameter section)
- Spec: SDD-20260217-it-dev-ddm-mock-data

**Status**: Generalized

---
