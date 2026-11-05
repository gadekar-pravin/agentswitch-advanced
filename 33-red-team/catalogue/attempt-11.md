# Attempt 11 — Party.list (foreign company filter)

1. **Attempt:** List parties while passing a foreign tenant's `company_id` as a filter.
2. **Boundary:** (Other company) The server must scope to my own tenant and ignore an attacker-supplied `company_id`.
3. **Steps:**
   1. `tools/call` `Party.list` `{company_id:<foreign>, limit:5}`.
   2. Compare with no filter and with my own `company_id`.
4. **Expected:** Empty for the foreign id.
5. **Actual:** HTTP 200, `total=0` for the foreign id, vs `total=233` with no filter and with my own `company_id`. The foreign id came from the other instance (Keystone), which is a separate system, so that company does not exist on Suryodaya. `total=0` is therefore the expected answer whether or not the server enforces tenant scoping, and this attempt cannot tell the two apart.
6. **Result:** Unclear — a real test needs the id of another company on the same instance, which our login cannot see. Re-test if one becomes available (see open question 7 in `PLAN.md`).
