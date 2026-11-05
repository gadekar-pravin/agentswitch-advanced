# Attempt 12 — Party.get (foreign id)

1. **Attempt:** Fetch a party by an id taken from the other instance (`Party.get`).
2. **Boundary:** (Other company) A foreign id must not resolve.
3. **Steps:**
   1. `tools/call` `Party.get` `{id:<id from other instance>}`.
4. **Expected:** Not found / denied.
5. **Actual:** HTTP 200 isError, `-32004` "Party not found" (`not_found`). The id came from the other instance, which is a separate system, so the record does not exist on Suryodaya at all. `not_found` is the expected answer either way.
6. **Result:** Unclear — needs the id of a record owned by another company on the same instance, which our login cannot see.
