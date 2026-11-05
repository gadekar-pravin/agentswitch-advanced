# Attempt 06 — LedgerRetentionPolicy.list

1. **Attempt:** List ledger retention policies (`LedgerRetentionPolicy.list`).
2. **Boundary:** (Permission) Governance configuration, out of scope.
3. **Steps:**
   1. Authenticate.
   2. `tools/call` `LedgerRetentionPolicy.list` `{limit:5}`.
4. **Expected:** 403 / empty.
5. **Actual:** HTTP 200, empty list.
6. **Result:** Held
