Expense & Time Tracker MCP Server (Final Bundle)
===============================================

Everything inside this `/final` directory is the minimal set you need to share
the MCP server with someone else (either as raw files or via Docker). Keep the
folder contents together; nothing outside of it is required for a clean run.

What’s Included
---------------
- `main.py` - FastMCP server implementation. Running `python main.py` starts
  the MCP process and automatically creates `tracker.db` in this same directory
  if it doesn’t already exist.
- `categories.json` - Default expense categories shipped with the server.
- `pyproject.toml` - Optional helper so the same dependencies can be installed
  with `pip install -e .` or `uv pip install -r pyproject.toml`.
- `Dockerfile` & `.dockerignore` - Ready-to-build container context scoped only
  to this folder.
- `README.md` - (this file) Local/Docker instructions in one place.

Local Development From `/final`
-------------------------------
1. Open a terminal **inside this folder**.
2. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Install the minimal runtime dependencies:
   ```powershell
   pip install --upgrade pip
   pip install "fastmcp>=2.13.0.2" "aiosqlite>=0.21.0"
   ```
4. Start the MCP server:
   ```powershell
   python main.py
   ```
   Claude Desktop (or any MCP client) can now be pointed at this script.

Docker Usage (Run From `/final`)
--------------------------------
1. Build the image using this folder as the build context:
   ```bash
   docker build -t expense-tracker:latest .
   ```
2. Run with a fresh throwaway database:
   ```bash
   docker run --rm -it expense-tracker:latest
   ```
3. Run with a persistent host database by bind-mounting a file:
   - PowerShell / Command Prompt:
     ```powershell
     docker run --rm -it `
       -v ${PWD}\tracker.db:/app/tracker.db `
       expense-tracker:latest
     ```
   - macOS / Linux shell:
     ```bash
     docker run --rm -it \
       -v $(pwd)/tracker.db:/app/tracker.db \
       expense-tracker:latest
     ```
   The container writes directly to `/app/tracker.db`, so mounting keeps the
   data on the host while still letting the MCP server run in Docker.

Sharing the Image
-----------------
Push `expense-tracker:latest` to any registry (Docker Hub, GHCR, etc.) or export
it with `docker save expense-tracker:latest -o expense-tracker.tar`. Recipients
can then run `docker load -i expense-tracker.tar` followed by the same run
commands above.
