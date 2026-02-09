# Architecture Decision Records (ADRs)

Record architectural decisions using the MADR (Markdown Any Decision Records) format.

## What is an ADR?

An ADR documents a significant architectural decision along with its context and consequences. ADRs are immutable once accepted - if a decision is revisited, a new ADR is created that supersedes the old one.

## Format

We use the [MADR](https://adr.github.io/madr/) format. See [../../templates/adr.md](../../templates/adr.md) for the template.

## ADR Numbering

- Format: `ADR-{NNNN}-{slug}.md`
- Example: `ADR-0001-medallion-architecture.md`
- Numbers are sequential within a project
- Never reuse numbers

## Statuses

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet decided |
| **Accepted** | Decision has been made and is in effect |
| **Deprecated** | No longer applies (context changed) |
| **Superseded** | Replaced by a newer ADR |

## This Repository

This repository contains **generic** principles and patterns. Project-specific ADRs belong in project subrepos.

### Reference: Generic Principles

Common architectural decisions are documented as principles:

| Topic | Documentation |
|-------|--------------|
| Data layers | [Medallion Architecture](../../principles/medallion-architecture.md) |
| PII handling | [Security & Privacy](../../principles/security-privacy.md) |
| Environments | [Environment Separation](../../principles/environment-separation.md) |
| Data classification | [Data Governance](../../principles/data-governance.md) |
| MDM | [MDM Patterns](../../principles/mdm-patterns.md) |

## Creating ADRs in Project Subrepos

1. Create folder: `docs/architecture/decisions/`
2. Copy template from `docs/templates/adr.md`
3. Use next available number
4. Set status to `Proposed`
5. Get team review (PR)
6. Update status to `Accepted` after consensus

## References

- [MADR Format](https://adr.github.io/madr/)
- [ADR GitHub Organization](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)

---

*Last Updated: 2026-02-09*
