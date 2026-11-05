# Attempt 01 — IPPool.list

1. **Attempt:** List the email IP pools (`IPPool.list`) as a low-privilege seat.
2. **Boundary:** (Permission) IP-pool / sending-reputation config is deliverability infrastructure, outside a crm/email/support/projects seat.
3. **Steps:**
   1. Authenticate; get a bearer token.
   2. `tools/call` `IPPool.list` `{limit:5}`.
4. **Expected:** 403 / out of scope.
5. **Actual:** HTTP 200. Returned this tenant's IP pools (e.g. "System Spare (reputation failover)", "System Quarantine") with `pool_health`, `daily_cap`, `assignment_priority`. Tenant-scoped; `write:false`.
6. **Result:** Broke — see `../findings/BUG-33-001.md`
