import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "trading_journal.db")

def init_db():
    """
    Initializes the SQLite database and creates the journal table if it does not exist.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trading_journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        asset TEXT NOT NULL,
        trade_class TEXT NOT NULL, -- 'Swing Equity', 'Intraday Equity', 'Intraday Options'
        entry_price REAL NOT NULL,
        exit_price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        pnl REAL NOT NULL,
        notes TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_journal_entry(
    asset: str,
    trade_class: str,
    entry_price: float,
    exit_price: float,
    quantity: int,
    notes: str
) -> None:
    """
    Adds a new trade record to the manual journal.
    """
    init_db()
    pnl = round((exit_price - entry_price) * quantity, 2)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO trading_journal (asset, trade_class, entry_price, exit_price, quantity, pnl, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (asset.upper(), trade_class, entry_price, exit_price, quantity, pnl, notes))
    
    conn.commit()
    conn.close()

def get_journal_entries() -> pd.DataFrame:
    """
    Fetches all logged trades in the journal database as a pandas DataFrame.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM trading_journal ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def delete_journal_entry(entry_id: int) -> None:
    """
    Deletes a journal entry by its ID.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trading_journal WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def save_bulk_entries(df: pd.DataFrame) -> None:
    """
    Saves a DataFrame back to the SQLite database.
    Used for bulk edits via Streamlit's st.data_editor.
    """
    init_db()
    conn = sqlite3.connect(DB_PATH)
    # Re-calculate P&L just to be sure
    if not df.empty:
        df['pnl'] = (df['exit_price'] - df['entry_price']) * df['quantity']
        df['pnl'] = df['pnl'].round(2)
        df['asset'] = df['asset'].str.upper()
    df.to_sql("trading_journal", conn, if_exists="replace", index=False)
    conn.close()
