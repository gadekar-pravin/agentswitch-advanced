# Attempt 08 — AgentTask.update (foreign)

1. **Attempt:** Update another seat's agent task (`AgentTask.update`), echoing one field unchanged.
2. **Boundary:** (Permission) Only the owner may change another seat's task.
3. **Steps:**
   1. Read the task via `AgentTask.get`.
   2. `tools/call` `AgentTask.update` `{id:<foreign task>, <field>:<same value>}`.
4. **Expected:** 403.
5. **Actual:** HTTP 200 isError, `-32001` "Permission denied" (`permission_denied`). The tool is exposed (own tasks) but the foreign record is refused.
6. **Result:** Held
