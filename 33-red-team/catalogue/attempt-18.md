# Attempt 18 — Malformed token

1. **Attempt:** Call the MCP endpoint with a malformed bearer token.
2. **Boundary:** (Auth) Authentication.
3. **Steps:**
   1. `POST /api/mcp` with `Authorization: Bearer garbage`.
4. **Expected:** 401.
5. **Actual:** HTTP 401 `{"detail":"Authentication required"}`.
6. **Result:** Held
