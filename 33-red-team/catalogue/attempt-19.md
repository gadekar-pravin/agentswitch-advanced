# Attempt 19 — Cross-system token

1. **Attempt:** Use the other instance's token against this system.
2. **Boundary:** (Auth) Tokens are scoped per system.
3. **Steps:**
   1. Obtain a Keystone token.
   2. Call Suryodaya `/api/mcp` with the Keystone bearer.
4. **Expected:** 401.
5. **Actual:** HTTP 401 — the Keystone token is rejected on Suryodaya.
6. **Result:** Held
