# Overview

The purpose of this repo is to test out whether financial NLP queries could be answered using a MCP Server surfacing a SQLite database.

## Projects

### Folder `experiments`

This folder contains scripts of prompts and responses from these experiments.

### Folder `src\fun_mcp_server`

This folder contains a sample self-contained MCP Server to verify the basic plumbing.

### Folder `src\sqlite-explorer-fastmcp-mcp-server`

This folder contains an MCP Server that exposes a SQLite database.

### Folder `src\test_data`

This folder contains tooling to populate the SQLite database with either Star Wars or financial data.

## Install on Windows

In Powershell
```
rm venv -r # to remove the venv folder
get-childitem src -include __pycache__ -recurse | remove-item -Force -Recurse
py -m venv venv
.\venv\Scripts\Activate.ps1
python --version
python -c "import sys; print(sys.executable)"
.\venv\Scripts\python.exe -m pip install --upgrade pip
pip install -r .\requirements.txt
```
