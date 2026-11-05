# Attempt 17 — No token

1. **Attempt:** Call the MCP endpoint with no Authorization header.
2. **Boundary:** (Auth) Authentication is required.
3. **Steps:**
   1. `POST /api/mcp` with a `tools/call` body and no `Authorization` header.
4. **Expected:** 401.
5. **Actual:** HTTP 401 `{"detail":"Authentication required"}`.
6. **Result:** Held
