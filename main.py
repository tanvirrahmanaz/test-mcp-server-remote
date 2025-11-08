from fastmcp import FastMCP
import os
import sqlite3
from datetime import datetime, timedelta

# Local paths
DB_PATH = os.path.join(os.path.dirname(__file__), "tracker.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseAndTimeTracker")

def init_db():
    """Initialize both expense and time tracking tables"""
    with sqlite3.connect(DB_PATH) as c:
        # Expense table
        c.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        
        # Time tracking table
        c.execute("""
            CREATE TABLE IF NOT EXISTS time_entries(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                activity TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                start_time TEXT,
                end_time TEXT,
                note TEXT DEFAULT ''
            )
        """)
        
        # Activity categories for time tracking
        c.execute("""
            CREATE TABLE IF NOT EXISTS activity_categories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#3b82f6'
            )
        """)
        
        # Insert default activity categories if empty
        cur = c.execute("SELECT COUNT(*) FROM activity_categories")
        if cur.fetchone()[0] == 0:
            default_activities = [
                ('Study', '#10b981'),
                ('Work', '#3b82f6'),
                ('Game', '#8b5cf6'),
                ('Exercise', '#f59e0b'),
                ('Reading', '#ec4899'),
                ('Coding', '#06b6d4'),
                ('Sleep', '#6366f1'),
                ('Social', '#f97316'),
                ('Other', '#6b7280')
            ]
            c.executemany(
                "INSERT INTO activity_categories(name, color) VALUES (?, ?)",
                default_activities
            )

init_db()

# ==================== EXPENSE TOOLS ====================

@mcp.tool()
def add_expense(date: str, amount: float, category: str, subcategory: str = "", note: str = ""):
    """Add a new expense entry to the database.
    
    Args:
        date: Date in YYYY-MM-DD format
        amount: Expense amount
        category: Expense category
        subcategory: Optional subcategory
        note: Optional note
    """
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status": "success", "id": cur.lastrowid, "message": "Expense added successfully"}

@mcp.tool()
def list_expenses(start_date: str, end_date: str):
    """List expense entries within an inclusive date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    """
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            SELECT id, date, amount, category, subcategory, note
            FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, id DESC
            """,
            (start_date, end_date)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def summarize_expenses(start_date: str, end_date: str, category: str = None):
    """Summarize expenses by category within an inclusive date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        category: Optional category filter
    """
    with sqlite3.connect(DB_PATH) as c:
        query = """
            SELECT category, SUM(amount) AS total_amount, COUNT(*) as count
            FROM expenses
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " GROUP BY category ORDER BY total_amount DESC"
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

# ==================== TIME TRACKING TOOLS ====================

@mcp.tool()
def add_time_entry(date: str, activity: str, duration_minutes: int, start_time: str = None, end_time: str = None, note: str = ""):
    """Add a new time tracking entry.
    
    Args:
        date: Date in YYYY-MM-DD format
        activity: Activity name (e.g., Study, Game, Work)
        duration_minutes: Duration in minutes
        start_time: Optional start time in HH:MM format
        end_time: Optional end time in HH:MM format
        note: Optional note about the activity
    """
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO time_entries(date, activity, duration_minutes, start_time, end_time, note) VALUES (?,?,?,?,?,?)",
            (date, activity, duration_minutes, start_time, end_time, note)
        )
        return {"status": "success", "id": cur.lastrowid, "message": f"Time entry added: {duration_minutes} minutes on {activity}"}

@mcp.tool()
def list_time_entries(start_date: str, end_date: str, activity: str = None):
    """List time entries within a date range, optionally filtered by activity.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        activity: Optional activity filter
    """
    with sqlite3.connect(DB_PATH) as c:
        query = """
            SELECT id, date, activity, duration_minutes, start_time, end_time, note
            FROM time_entries
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if activity:
            query += " AND activity = ?"
            params.append(activity)
        query += " ORDER BY date DESC, start_time DESC"
        
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, r)) for r in cur.fetchall()]
        
        # Convert minutes to hours for easier reading
        for r in results:
            r['duration_hours'] = round(r['duration_minutes'] / 60, 2)
        
        return results

@mcp.tool()
def summarize_time(start_date: str, end_date: str, activity: str = None):
    """Summarize time spent by activity within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        activity: Optional activity filter
    """
    with sqlite3.connect(DB_PATH) as c:
        query = """
            SELECT activity, 
                   SUM(duration_minutes) AS total_minutes,
                   COUNT(*) as entry_count,
                   AVG(duration_minutes) as avg_minutes
            FROM time_entries
            WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if activity:
            query += " AND activity = ?"
            params.append(activity)
        query += " GROUP BY activity ORDER BY total_minutes DESC"
        
        cur = c.execute(query, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, r)) for r in cur.fetchall()]
        
        # Add hours conversion and percentage
        total_all = sum(r['total_minutes'] for r in results)
        for r in results:
            r['total_hours'] = round(r['total_minutes'] / 60, 2)
            r['avg_hours'] = round(r['avg_minutes'] / 60, 2)
            r['percentage'] = round((r['total_minutes'] / total_all * 100), 1) if total_all > 0 else 0
        
        return results

@mcp.tool()
def get_daily_summary(date: str):
    """Get a complete summary of expenses and time for a specific day.
    
    Args:
        date: Date in YYYY-MM-DD format
    """
    with sqlite3.connect(DB_PATH) as c:
        # Get expenses
        cur = c.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE date = ? GROUP BY category",
            (date,)
        )
        expenses = [{"category": r[0], "total": r[1]} for r in cur.fetchall()]
        
        # Get time entries
        cur = c.execute(
            "SELECT activity, SUM(duration_minutes) as total_minutes FROM time_entries WHERE date = ? GROUP BY activity",
            (date,)
        )
        time_entries = [{"activity": r[0], "minutes": r[1], "hours": round(r[1]/60, 2)} for r in cur.fetchall()]
        
        return {
            "date": date,
            "expenses": expenses,
            "total_expense": sum(e['total'] for e in expenses),
            "time_entries": time_entries,
            "total_hours": sum(t['hours'] for t in time_entries)
        }

@mcp.tool()
def list_activities():
    """List all available activity categories with their colors."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT name, color FROM activity_categories ORDER BY name")
        return [{"name": r[0], "color": r[1]} for r in cur.fetchall()]

@mcp.tool()
def add_activity_category(name: str, color: str = "#3b82f6"):
    """Add a new activity category.
    
    Args:
        name: Activity category name
        color: Hex color code (default: blue)
    """
    try:
        with sqlite3.connect(DB_PATH) as c:
            c.execute("INSERT INTO activity_categories(name, color) VALUES (?, ?)", (name, color))
            return {"status": "success", "message": f"Activity category '{name}' added"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": f"Activity category '{name}' already exists"}

# ==================== RESOURCES ====================

@mcp.resource("expense:///categories")
def expense_categories():
    """Get expense categories"""
    try:
        if os.path.exists(CATEGORIES_PATH):
            with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
                return f.read()
        else:
            # Default categories
            import json
            default = {
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
                    "Other"
                ]
            }
            return json.dumps(default, indent=2)
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'

if __name__ == "__main__":
    print(f"Database location: {DB_PATH}")
    print("Starting MCP server locally...")
    mcp.run()