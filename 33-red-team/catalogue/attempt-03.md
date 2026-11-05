# Attempt 03 — mission_control.incidents

1. **Attempt:** Query the mission-control incidents console (`endpoint.mission_control.incidents`).
2. **Boundary:** (Permission) Ops console, out of scope for this seat.
3. **Steps:**
   1. Authenticate.
   2. `tools/call` `endpoint.mission_control.incidents` `{}`.
4. **Expected:** 403.
5. **Actual:** HTTP 200, `read_only:true`, 14-day window, `rows:[]` (0 incidents). The endpoint is reachable but there is no data to disclose right now.
6. **Result:** Unclear
