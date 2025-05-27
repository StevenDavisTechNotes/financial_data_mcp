from . import server
import asyncio
import argparse


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description='SQLite MCP Server')
    parser.add_argument('--db-path', 
                       default="C:/Src/GitHub_Hosted/mcp_example_servers/src/sqlite/test.db",
                       help='Path to SQLite database file')
    
    args = parser.parse_args()
    asyncio.run(server.main(args.db_path))

if __name__ == "__main__":
    main()