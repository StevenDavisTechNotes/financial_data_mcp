# Other sql mcp servers for testing

## Running

Configuration is in `.vscode\mcp.json`

### SSE

```ps1
python -m src.mcp_server_sqlite.main
```

```json
{
    "servers": {
        "fun_mcp_server_sse": {
            "url": "http://127.0.0.1:8000/sse"
        }
    }
}
```
