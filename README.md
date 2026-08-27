# MIRA 2.0

**MIRA — Modular Intelligence & Reasoning Assistant**

MIRA is the user-facing intelligent assistant and control plane. It helps the user understand, plan, reconcile, decide, and execute bounded actions across their real life and work.

**MIRROR** is MIRA's companion reality database: the durable structured record of facts, evidence, entities, state, provenance, and relationships that MIRA reasons over. MIRROR is a product component, not the primary brand, and its acronym does not need to be expanded in user-facing copy.

## Development authority

This repository is authoritative for MIRA 2.0 product development.

Git is the source of truth for:

- `ROADMAP.md`
- `FEATURES.md`
- `BACKLOG.md`
- `CURRENT_WORK.md`
- work-packet policy and engineering decisions

Existing legacy MIRA Google spreadsheets, Drive artifacts, briefs, schedules, and other live state are protected production data. MIRA 2.0 development must use a separate sandbox and must not modify or silently migrate legacy production data.

## Customer/developer model

The user is the customer/product owner. The assistant/developer owns decomposition, architecture, dependency analysis, work-packet sizing, acceptance criteria, backlog ranking, durable checkpoints, testing, and implementation sequencing.

The customer may brainstorm freely. New ideas become backlog work by default and do not silently expand the active packet.

## Current phase

MIRA 2.0 begins with a full forensic feature audit and dependency reconstruction before new product implementation. Legacy MIRA repositories and PRs are evidence/reference sources, not code to merge wholesale.
