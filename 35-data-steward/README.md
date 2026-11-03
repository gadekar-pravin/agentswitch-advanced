# Seat 35: Data Steward

## Scope
Data quality: duplicate parties and items, missing required fields, orphan records. Proposes merges; a person approves them.

## First task
A duplicate-party and duplicate-item report with merge proposals and a confidence for each.

## Access
crm, inventory, accounting (read)

## Milestones
- 15 Nov 2026: first task delivered
- 30 Nov 2026: version 1, with a 12-task test suite
- 20 Dec 2026: integration run of all eight seats
- 31 Dec 2026: final

## Working rules
See the top-level README. Put your agent code, tests and notes in this folder; open a pull request for every change.

## Setup
```bash
uv sync
cp .env.example .env                   # paste both passwords; .env is git-ignored
uv run pytest                          # offline tests
uv run python -m data_steward.probe    # read-only login and tool list on both systems
```
The probe writes the full tool list to `local/`, which is git-ignored because it is platform-derived. See
[AGENTS.md](AGENTS.md) for what may run against the live systems.
