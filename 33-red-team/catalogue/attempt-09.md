# Attempt 09 — AgentMemory.create (foreign tenant)

1. **Attempt:** Create an agent memory bound to a foreign tenant (`AgentMemory.create` with a foreign `company_id`).
2. **Boundary:** (Other company) Cross-tenant write: cannot write into another company.
3. **Steps:**
   1. Authenticate.
   2. `tools/call` `AgentMemory.create` `{content:<benign>, company_id:<foreign>}`.
4. **Expected:** 403.
5. **Actual:** HTTP 200 isError, `-32001` `permission_denied`. (The tool also exposes no persona-target argument, so persona memory-poisoning is not reachable.)
6. **Result:** Held
