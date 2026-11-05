# Attempt 05 — events.catalog

1. **Attempt:** List the manufacturing/inventory automation events (`events.catalog`).
2. **Boundary:** (Permission) Manufacturing is not granted to this seat.
3. **Steps:**
   1. Authenticate.
   2. `tools/call` `events.catalog` `{}`.
4. **Expected:** 403 / empty.
5. **Actual:** HTTP 200, `events:[]`.
6. **Result:** Held
