# We create two tools here
# get_office_jokes and get_current_date

from mcp.server.fastmcp import FastMCP
from datetime import datetime
import random
# Initialize FastMCP server
mcp = FastMCP("custom_mcp_tools ")


@mcp.tool()
async def get_office_jokes() -> str:
    """Get office jokes
    """
    # List of office jokes
    jokes = ["Why don't scientists trust atoms? Because they make up everything!",
             "Why did the scarecrow become a successful motivational speaker? Because he was outstanding in his field!",
             "Why don't skeletons fight each other? They don't have the guts.",
             "Why did the bicycle fall over? It was two-tired!", "Why did the math book look sad? Because it had too many problems."
             ]

    return random.choice(jokes)


@mcp.tool()
async def get_current_date() -> str:
    """Get current date
    """
    return str(datetime.today().strftime('%Y-%m-%d'))


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
