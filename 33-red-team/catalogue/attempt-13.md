# Attempt 13 — Company.get (foreign id)

1. **Attempt:** Fetch a company by an id from the other instance (`Company.get`).
2. **Boundary:** (Other company) A foreign company id must not resolve.
3. **Steps:**
   1. `tools/call` `Company.get` `{id:<id from other instance>}`.
4. **Expected:** Not found / denied.
5. **Actual:** HTTP 200 isError, `-32004` "Company not found" (`not_found`). The id came from the other instance, which is a separate system, so that company does not exist on Suryodaya. `not_found` is the expected answer either way.
6. **Result:** Unclear — needs the id of another company on the same instance, which our login cannot see.
