from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from src.fun_mcp_server.custom_mcp_tools import mcp
import uvicorn


app = FastAPI(docs_url=None, redoc_url=None,)

sse = SseServerTransport("/messages/")
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))


@app.get("/sse", tags=["MCP"])
async def handle_sse(request: Request):

    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        init_options = mcp._mcp_server.create_initialization_options()

        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            init_options,
        )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
