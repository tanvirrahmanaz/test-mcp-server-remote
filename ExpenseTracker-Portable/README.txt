Expense & Time Tracker - Portable Build
=======================================

Quick Start
-----------
1. Extract the `ExpenseTracker-Portable` folder anywhere you like
   (for example `D:\Apps\ExpenseTracker`). Keep that full path handy.
2. Open `sample_claude_config.txt`, copy the JSON snippet, and paste it into
   Claude Desktop → Settings → Developer → Edit Config. Replace the example
   path with the real path to `ExpenseTimeTracker.exe` and keep the double
   backslashes (\\) in every path segment.
3. Save the config, completely close Claude Desktop (use the tray icon → Quit),
   then launch Claude Desktop again so it loads the new MCP server.
4. Verify everything works by asking Claude something like "Show today's summary".
   If you get a response, the server is running and ready.

Using the MCP Server
--------------------
- Track expenses: "Add expense: 500 taka for lunch today"
- Track time: "Log 2 hours of study time"
- Reports: "Show today's summary" or "Give me expense report for November"

Data Storage
------------
All information is stored in `tracker.db` alongside the executable. To back up,
copy that file. To restore, place it next to the executable before launching.

Troubleshooting
---------------
- If Claude cannot find the server, open Settings → Developer and confirm the path,
  then restart Claude Desktop.
- If antivirus blocks the executable, add ExpenseTimeTracker.exe to its allowlist.
- The server runs in the background; interact with it through Claude prompts only.

Need help? Reach out to the developer who shared this build.
