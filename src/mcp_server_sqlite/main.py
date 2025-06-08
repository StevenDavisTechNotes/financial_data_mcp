import sys
from . import server
import asyncio
import argparse
import os


def main():
    """Main entry point for the package."""
    project_root_path = os.path.join(sys.executable, "..", "..", "..")
    default_db_path = os.path.join(str(project_root_path), "data.db")

    parser = argparse.ArgumentParser(description='SQLite MCP Server')
    parser.add_argument(
        '--db-path',
        default=default_db_path,
        help='Path to SQLite database file',
    )

    args = parser.parse_args()
    asyncio.run(server.main(args.db_path))


if __name__ == "__main__":
    main()
