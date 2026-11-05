# Attempt 04 — DnsRecord.list

1. **Attempt:** List DNS records (`DnsRecord.list`).
2. **Boundary:** (Permission) DNS administration, beyond ordinary email use.
3. **Steps:**
   1. Authenticate.
   2. `tools/call` `DnsRecord.list` `{limit:5}`.
4. **Expected:** 403 / empty.
5. **Actual:** HTTP 200, empty list. Nothing disclosed (endpoint reachable).
6. **Result:** Held
