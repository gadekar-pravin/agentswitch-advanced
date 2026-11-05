# Attempt 02 — job_ledger.forensics

1. **Attempt:** Read the agent job-ledger forensics (`endpoint.job_ledger.forensics`).
2. **Boundary:** (Permission) The job-ledger forensics is a governance/audit surface; the 3 Nov access note lists only agent records (seats, skills, tasks) as readable.
3. **Steps:**
   1. Authenticate.
   2. `tools/call` `endpoint.job_ledger.forensics` `{}`.
4. **Expected:** 403.
5. **Actual:** HTTP 200, `read_only:true`, paged rows disclosing job numbers (`JOB-2026-096xx`), `correlation_id`, `seal_count`, `events_read`, `outcome`, `status`, and titles ("Review N newly late production order(s)"). `has_more:true`.
6. **Result:** Broke — see `../findings/BUG-33-002.md`
