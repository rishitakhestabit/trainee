import os
import sqlite3
from datetime import datetime
from pathlib import Path
from config import BASE_DIR


class LongTermMemory:

    def __init__(self, db_path="memory/long_term.db"):
        path = Path(db_path)
        if not path.is_absolute():
            path = BASE_DIR / path

        os.makedirs(path.parent, exist_ok=True)

        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self._create_table()

    def _create_table(self):

        cursor = self.conn.cursor()

        cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY,
            fact TEXT,
            category TEXT,
            importance REAL,
            created_at TEXT
        )
        """
        )

        self.conn.commit()


    def store(self, memory_id, fact, category="general", importance=0.5):

        cursor = self.conn.cursor()

        cursor.execute(
        """
        INSERT INTO memories (id, fact, category, importance, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            memory_id,
            fact,
            category,
            importance,
            datetime.utcnow().isoformat()
        )
        )

        self.conn.commit()


    def get_by_ids(self, ids):

        if not ids:
            return []

        cursor = self.conn.cursor()

        placeholders = ",".join(["?"] * len(ids))

        query = f"""
        SELECT fact
        FROM memories
        WHERE id IN ({placeholders})
        """

        cursor.execute(query, ids)

        rows = cursor.fetchall()

        return [row[0] for row in rows]


    def delete(self, memory_id):

        cursor = self.conn.cursor()

        cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
        """,
        (memory_id,)
        )

        self.conn.commit()


    def get_all(self):

        cursor = self.conn.cursor()

        cursor.execute(
        """
        SELECT id, fact, category, importance
        FROM memories
        """
        )

        return cursor.fetchall()
