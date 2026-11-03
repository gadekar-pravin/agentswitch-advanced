# Boundary catalogue

Keep the catalogue in this folder as `catalogue/attempts.md` (a table) and one file per attempt, `catalogue/attempt-01.md` to `attempt-20.md`.

Each attempt file has the same headings:

1. Attempt: what you tried, in one sentence
2. Boundary: what it should not allow (permission, other company, injection)
3. Steps: exact requests, no credentials
4. Expected: the refusal you expect
5. Actual: what came back
6. Result: Held, Broke, or Unclear. A Broke result also gets a bug report (`BUG_REPORT_FORMAT.md`)

Suggested folder shape for the seat:

    33-red-team/
      README.md
      CATALOGUE_FORMAT.md
      catalogue/attempts.md
      catalogue/attempt-01.md ... attempt-20.md
      replay/            a script that repeats the attempts from a login (reads the login from the environment, never from a file)
      findings/          one bug report per Broke result

Re-runs: the platform runs on private servers and the attempts need a login, so they do not run in GitHub. The course team re-runs the replay script against the test systems before each release and sends you the result.
