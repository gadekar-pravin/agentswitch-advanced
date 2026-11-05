# Attempt 16 — EmailAccount.list

1. **Attempt:** List email accounts (`EmailAccount.list limit=1000`).
2. **Boundary:** (Permission) Email privacy: own only.
3. **Steps:**
   1. `tools/call` `EmailAccount.list` `{limit:1000}`.
4. **Expected:** Own only.
5. **Actual:** HTTP 200, empty.
6. **Result:** Held
