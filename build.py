#!/usr/bin/env python
"""
Utility script to build the Expense & Time Tracker MCP server into a
portable Windows package.

Usage:
    python build.py
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parent
DIST_NAME = "ExpenseTimeTracker"
PACKAGE_DIR = ROOT / "ExpenseTracker-Portable"
REQUIRED_PACKAGES = {
    "pyinstaller": "PyInstaller",
    "fastmcp": "fastmcp",
    "py-key-value-aio[disk]": "key_value",
}


def print_step(title: str) -> None:
    bar = "=" * 60
    print(f"\n{bar}\n{title}\n{bar}")


def run(cmd: Iterable[str]) -> None:
    cmd_list: List[str] = list(cmd)
    print(f"\n$ {' '.join(cmd_list)}\n")
    subprocess.check_call(cmd_list, cwd=ROOT)


def ensure_dependencies() -> None:
    print_step("Step 1/4 - Checking dependencies")
    missing = []
    for install_name, import_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
            print(f"  [OK] {import_name} found")
        except ImportError:
            missing.append(install_name)

    if not missing:
        return

    print(f"\n  Installing missing packages: {', '.join(missing)}")
    for pkg in missing:
        run([sys.executable, "-m", "pip", "install", pkg])
    print("  [OK] Dependencies installed\n")


def _handle_remove_readonly(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
    except Exception:
        pass
    try:
        func(path)
    except Exception as exc:  # pragma: no cover - best effort cleanup
        raise exc


def clean_previous_artifacts() -> None:
    print_step("Step 2/4 - Cleaning previous build artifacts")
    for target in ("build", "dist", "__pycache__", f"{DIST_NAME}.spec"):
        path = ROOT / target
        if path.is_dir():
            shutil.rmtree(path, onerror=_handle_remove_readonly)
            print(f"  [OK] Removed {path.relative_to(ROOT)}")
        elif path.exists():
            path.unlink()
            print(f"  [OK] Removed {path.name}")


def ensure_categories_file() -> None:
    json_path = ROOT / "categories.json"
    if json_path.exists():
        return

    print("  categories.json missing - creating default file")
    default_categories = {
        "categories": [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Bills & Utilities",
            "Healthcare",
            "Travel",
            "Education",
            "Business",
            "Other",
        ]
    }
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(default_categories, fh, indent=2)
    print("  [OK] Created categories.json")


def find_fastmcp_package() -> Path:
    try:
        import fastmcp  # type: ignore

        path = Path(fastmcp.__file__).resolve().parent
        print(f"  [OK] fastmcp package located at {path}")
        return path
    except ImportError:
        raise SystemExit(
            "fastmcp is not installed. Please rerun the script so it can install dependencies."
        )


def build_executable() -> None:
    print_step("Step 3/4 - Building ExpenseTimeTracker.exe")
    ensure_categories_file()
    fastmcp_path = find_fastmcp_package()

    data_sep = ";" if os.name == "nt" else ":"

    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        f"--name={DIST_NAME}",
        f"--add-data=categories.json{data_sep}.",
        f"--add-data={fastmcp_path}{data_sep}fastmcp",
        "--hidden-import=fastmcp",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=datetime",
        "--collect-all=fastmcp",
        "--collect-all=key_value",
        "--noconfirm",
        "--clean",
        "main.py",
    ]

    run(pyinstaller_cmd)
    exe_path = ROOT / "dist" / f"{DIST_NAME}.exe"
    if not exe_path.exists():
        raise SystemExit("PyInstaller did not produce the expected executable.")
    print(f"  [OK] Built {exe_path}")


def write_text_file(path: Path, content: str) -> None:
    path.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"  [OK] Wrote {path.relative_to(ROOT)}")


def create_portable_package() -> None:
    print_step("Step 4/4 - Creating ExpenseTracker-Portable/")
    if PACKAGE_DIR.exists():
        shutil.rmtree(PACKAGE_DIR, onerror=_handle_remove_readonly)
    PACKAGE_DIR.mkdir()

    files_to_copy = {
        ROOT / "dist" / f"{DIST_NAME}.exe": PACKAGE_DIR / f"{DIST_NAME}.exe",
        ROOT / "categories.json": PACKAGE_DIR / "categories.json",
    }

    tracker_db = ROOT / "tracker.db"
    if tracker_db.exists():
        files_to_copy[tracker_db] = PACKAGE_DIR / "tracker.db"

    for src, dst in files_to_copy.items():
        if not src.exists():
            print(f"  [WARN] Skipping missing file: {src.name}")
            continue
        shutil.copy2(src, dst)
        print(f"  [OK] Copied {src.name} -> {dst.relative_to(ROOT)}")

    readme_text = """
Expense & Time Tracker - Portable Build
=======================================

Quick Start
-----------
1. Extract the `ExpenseTracker-Portable` folder anywhere you like
   (for example `D:\\Apps\\ExpenseTracker`). Keep that full path handy.
2. Open `sample_claude_config.txt`, copy the JSON snippet, and paste it into
   Claude Desktop → Settings → Developer → Edit Config. Replace the example
   path with the real path to `ExpenseTimeTracker.exe` and keep the double
   backslashes (\\\\) in every path segment.
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
"""
    write_text_file(PACKAGE_DIR / "README.txt", readme_text)

    sample_config = r"""
{
  "mcpServers": {
    "ExpenseTracker": {
      "command": "C:\\\\ExpenseTracker\\\\ExpenseTimeTracker.exe"
    }
  }
}

Notes:
1. Replace C:\\\\ExpenseTracker\\\\ with the actual folder path where you extracted the package.
2. Always use double backslashes in the JSON file.
3. Keep the executable file name exactly the same.

Example paths:
- "C:\\\\Users\\\\Tanvi\\\\Documents\\\\ExpenseTracker\\\\ExpenseTimeTracker.exe"
- "D:\\\\Apps\\\\ExpenseTracker\\\\ExpenseTimeTracker.exe"
"""
    write_text_file(PACKAGE_DIR / "sample_claude_config.txt", sample_config)

    print(f"\nPortable package ready at: {PACKAGE_DIR}")
    print("Next steps:")
    print("  1. Zip the ExpenseTracker-Portable folder.")
    print("  2. Share the archive with your intended users.")
    print("  3. They only need to extract and reference the executable in Claude.")


def main() -> None:
    print("Expense & Time Tracker - Portable Builder")
    print("------------------------------------------")
    if not (ROOT / "main.py").exists():
        raise SystemExit("main.py not found in this directory. Run the script from the project root.")
    ensure_dependencies()
    clean_previous_artifacts()
    build_executable()
    create_portable_package()
    print("\nAll done!")


if __name__ == "__main__":
    main()
