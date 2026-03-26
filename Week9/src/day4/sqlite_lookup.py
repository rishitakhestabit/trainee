import sqlite3


def view_all_memories(db_name="memory/long_term.db"):

    conn = None

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT id, fact, category, importance, created_at FROM memories")
        rows = cursor.fetchall()

        if not rows:
            print("The database is currently empty.")
            return

        print(f"{'ID':<18} | {'CATEGORY':<12} | {'IMPORTANCE':<10} | {'FACT'}")
        print("-" * 90)

        for row in rows:
            mem_id, fact, category, importance, timestamp = row

            print(f"{mem_id:<18} | {category:<12} | {importance:<10} | {fact}")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    view_all_memories()