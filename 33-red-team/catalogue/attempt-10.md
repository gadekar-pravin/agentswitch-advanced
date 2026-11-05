# Attempt 10 — EmailAccount.update (foreign)

1. **Attempt:** Update an email account this seat does not own (`EmailAccount.update`).
2. **Boundary:** (Permission) Not my mailbox.
3. **Steps:**
   1. `tools/call` `EmailAccount.list` to find a target id.
4. **Expected:** 403.
5. **Actual:** Not testable: `EmailAccount.list` returns empty for this seat, so there is no account id to target.
6. **Result:** Unclear
