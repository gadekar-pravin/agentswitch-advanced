import json

import pytest

from data_steward import mcp_client
from data_steward.mcp_client import AuthExpired, McpClient, McpError


class FakeSession:
    base = "https://instance.example"

    def __init__(self):
        self.token = "old"
        self.logins = 0

    def login(self):
        self.logins += 1
        self.token = f"new{self.logins}"

    def with_reauth(self, fn):
        try:
            return fn()
        except AuthExpired:
            self.login()
            return fn()


def fake_http(replies):
    """Serve `replies` in order, recording each JSON-RPC body; an exception in the list is raised instead."""
    calls = []

    def _http(url, body=None, token=None, **kwargs):
        calls.append({"body": body, "token": token, **kwargs})
        reply = replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply

    return _http, calls


def ok(result):
    return 200, {"jsonrpc": "2.0", "id": 1, "result": result}


def client(monkeypatch, replies):
    _http, calls = fake_http([ok({}), *replies])
    monkeypatch.setattr(mcp_client, "_http", _http)
    return McpClient(FakeSession()), calls


def test_jsonrpc_error_inside_http_200_raises(monkeypatch):
    c, _ = client(monkeypatch, [(200, {"jsonrpc": "2.0", "id": 2, "error": {
        "code": -32601, "message": "Unknown tool: party.merge"}})])
    with pytest.raises(McpError) as e:
        c.call("party.merge", {})
    assert e.value.kind == "unknown_tool"


def test_tool_error_flag_raises_with_content(monkeypatch):
    c, _ = client(monkeypatch, [ok({"isError": True, "content": [{"type": "text", "text": '{"code": "permission_denied"}'}]})])
    with pytest.raises(McpError) as e:
        c.call("Party.list")
    assert e.value.kind == "permission_denied"


def test_text_content_is_parsed_as_json(monkeypatch):
    c, _ = client(monkeypatch, [ok({"content": [{"type": "text", "text": '{"data": [{"id": 1}], "total": 1}'}]})])
    assert c.call("Party.list") == {"data": [{"id": 1}], "total": 1}


def test_expired_token_logs_in_once_and_retries(monkeypatch):
    c, calls = client(monkeypatch, [AuthExpired("x"), ok({"tools": [{"name": "Party.list"}]})])
    assert c.tool_names() == {"Party.list"}
    assert c.session.logins == 1
    assert calls[-1]["token"] == "new1"


def test_writes_are_not_marked_read_only(monkeypatch):
    c, calls = client(monkeypatch, [ok({"content": []}), ok({"content": []})])
    c.call("Party.list")
    c.call("Party.update", {"id": 1})
    assert [call["read_only"] for call in calls[1:]] == [True, False]


def test_list_all_pages_until_total(monkeypatch):
    pages = [ok({"structuredContent": {"data": [{"id": i} for i in range(n, n + 2)], "total": 5}}) for n in (0, 2)]
    pages.append(ok({"structuredContent": {"data": [{"id": 4}], "total": 5}}))
    c, _ = client(monkeypatch, pages)
    rows = c.list_all("Party", page=2)
    assert [r["id"] for r in rows] == [0, 1, 2, 3, 4]
    assert rows.truncated is False


def test_list_all_reports_truncation(monkeypatch):
    c, _ = client(monkeypatch, [ok({"structuredContent": {"data": [{"id": 1}, {"id": 2}], "total": 9}})])
    rows = c.list_all("Party", page=2, max_rows=2)
    assert len(rows) == 2 and rows.total == 9 and rows.truncated is True


def test_sse_body_decodes_last_data_event():
    raw = b'event: message\ndata: {"jsonrpc": "2.0", "id": 1, "result": {"ok": true}}\n\n'
    assert mcp_client._decode(raw, "text/event-stream; charset=utf-8")["result"] == {"ok": True}
    assert mcp_client._decode(json.dumps({"a": 1}).encode(), "application/json") == {"a": 1}
