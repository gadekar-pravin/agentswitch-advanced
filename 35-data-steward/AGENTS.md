# AGENTS.md

Instructions for AI coding agents working in the seat 35 folder. The top-level README rules apply as well.

## Live systems: ask before running

Suryodaya (`agentswitch.theschoolofai.in`) and Keystone (`class.agentswitch.theschoolofai.in`) are live, shared
instances. Reading code and running the offline tests need no confirmation. Ask Pravin before anything that calls
them, apart from `python -m data_steward.probe` (login, `initialize`, `tools/list`; no writes).

- The agent proposes merges; it never changes a record. A person approves every change.
- Never delete or overwrite data this seat did not create.
- Ten wrong passwords in 15 minutes lock the login, so a failed login is never retried automatically.
- Each login has a daily token budget, and harness submissions are limited to one run per seat every 3 days.
  Never submit a run without being asked.

## The repository is public

- No passwords, tokens, keys or `.env` in commits. `.env` and `.tokens/` are git-ignored.
- No AgentSwitch source code, schemas, database files or screenshots of internal screens. Anything derived from the
  platform (tool lists, input schemas, field maps, probe dumps) goes in `local/`, which is git-ignored.

## Commands

```bash
uv sync
cp .env.example .env                   # both passwords; .env is git-ignored
uv run pytest                          # offline tests
uv run ruff check .
uv run python -m data_steward.probe    # read-only: what tools this seat sees on each system
```

## Environment

Python 3.11 locally; runtime code (`data_steward/`) must also run on 3.10 because the harness runner does not say
which Python it uses. `.env` values win over the shell, except under the harness runner (`AGENTSWITCH_TOKEN` set),
where `.env` is not read at all and the runner's `AGENTSWITCH_*` and `OPENAI_*` values are used.

## Platform quirks

- JSON-RPC errors arrive as HTTP 200: every MCP call inspects the envelope.
- Reads are retried on 502/503/504; writes never are.

## Code style

Match team04: double quotes, ~120-char lines, PEP 604 unions and builtin generics, plain dicts as the data
interchange format, stdlib → third-party → local imports. Ruff checks correctness rules only; no formatter is run.
Comments explain why the platform behaves oddly, not what the code does.
