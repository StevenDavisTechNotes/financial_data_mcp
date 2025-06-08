# Script for exercising the mcp_server_sqlite on Star Wars data

## Credits

### Install

- Run `python -m src.test_data.populate_db --data star-wars`
- Run `python -m src.sqlite-explorer-fastmcp-mcp-server.main`
- Restart mcp server in client

### SSE
Use a separate mcp client rather than the same VSCode project, or Github Copilot will just read the code and not call the server!

#### Planets

```txt
What tables does the MCP Server mcp_server_sql_sse have access to?

GitHub Copilot
Ran list-tables fun_mcp_server_sse (MCP Server)
The MCP Server mcp_server_sql_sse has access to the following table:

people
planet

```

#### Current Date

```txt
What are the distinct gravity values in the table planet?

GitHub Copilot
Ran read_query fun_mcp_server_sse (MCP Server)
The distinct gravity values in the planet table are:

1 standard
1.1 standard
N/A
1.5 (surface), 1 standard (Cloud City)
0.85 standard
0.9 standard
0.56 standard
0.75 standard
null
0.62 standard
1
1.56
0.9
0.98

```
