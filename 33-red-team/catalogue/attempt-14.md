# Attempt 14 — EmailMessage.list

1. **Attempt:** List email messages at maximum limit (`EmailMessage.list limit=1000`).
2. **Boundary:** (Permission) No other user's mail may be visible.
3. **Steps:**
   1. `tools/call` `EmailMessage.list` `{limit:1000}`.
4. **Expected:** Empty (this seat owns no mailbox).
5. **Actual:** HTTP 200, empty (`total 0`). Caveat: the seat owns no mailbox, so this does not test isolation between two populated mailboxes.
6. **Result:** Held
