# Run the fun mcp servers for testing

## Credits
From [medium](https://medium.com/@scholarly360/mcp-deep-dive-series-local-mcp-server-on-visual-studio-code-39914c1a1e3c) at [github](https://github.com/scholarly360/MCP-Deep-Dive-Series-Local-MCP-Servers-on-VSC)

## Running

Configuration is in `.vscode\mcp.json`

### STDIO

```json
{
    "servers": {
        "fun_mcp_server_stdio": {
            "type": "stdio",
            "command": "C:\\Src\\GitHub_Hosted\\financial_data_mcp\\.venv\\Scripts\\python.exe",
            "args": [
                "C:\\Src\\GitHub_Hosted\\financial_data_mcp\\src\\fun_mcp_server\\custom_mcp_tools.py"
            ]
        }
    }
}
```

### SSE

```ps1
python -m src.fun_mcp_server.main
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
