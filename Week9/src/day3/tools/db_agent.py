# import sqlite3, csv
# from tools.file_agent import FileAgent

# class DatabaseAgent:
#     def __init__(self):
#         self.fa = FileAgent()

#     def csv_to_db(self, csv_name):
#         db_name = csv_name.replace(".csv", ".db")
#         with open(self.fa.path(csv_name)) as f:
#             rows = list(csv.reader(f))
#         headers, data = rows[0], rows[1:]
#         conn = sqlite3.connect(self.fa.path(db_name))
#         cols = ", ".join(f'"{h.strip()}" TEXT' for h in headers)
#         conn.execute("DROP TABLE IF EXISTS data")
#         conn.execute(f"CREATE TABLE data ({cols})")
#         conn.executemany(f"INSERT INTO data VALUES ({','.join(['?']*len(headers))})", data)
#         conn.commit(); conn.close()
#         return db_name

#     def schema(self, db_name):
#         conn = sqlite3.connect(self.fa.path(db_name))
#         cols = [r[1] for r in conn.execute("PRAGMA table_info(data)")]
#         conn.close()
#         return cols

#     def query(self, sql, db_name):
#         try:
#             conn = sqlite3.connect(self.fa.path(db_name))
#             cur = conn.execute(sql)
#             rows = cur.fetchmany(20)
#             conn.commit(); conn.close()
#             return rows if rows else "Query executed. No rows returned."
#         except Exception as e:
#             return f"SQL Error: {e}"

#     def update(self, db_name, rowid, column, value):
#         return self.query(f'UPDATE data SET "{column}"="{value}" WHERE rowid={rowid}', db_name)



import sqlite3, csv
from tools.file_agent import FileAgent

class DatabaseAgent:
    def __init__(self):
        self.fa = FileAgent()

    def _connect(self, db_name):
        conn = sqlite3.connect(self.fa.path(db_name))
        conn.row_factory = sqlite3.Row
        return conn

    def _format(self, rows):
        if not rows:
            return "No rows returned."
        cols = rows[0].keys()
        header = " | ".join(cols)
        body   = "\n".join(" | ".join(str(r[c]) for c in cols) for r in rows)
        return f"{header}\n{'-'*len(header)}\n{body}"

    def csv_to_db(self, csv_name):
        db_name = csv_name.replace(".csv", ".db")
        with open(self.fa.path(csv_name)) as f:
            rows = list(csv.reader(f))
        headers, data = rows[0], rows[1:]
        conn = sqlite3.connect(self.fa.path(db_name))
        cols = ", ".join(f'"{h.strip()}" TEXT' for h in headers)
        conn.execute("DROP TABLE IF EXISTS data")
        conn.execute(f"CREATE TABLE data ({cols})")
        conn.executemany(f"INSERT INTO data VALUES ({','.join(['?']*len(headers))})", data)
        conn.commit(); conn.close()
        return db_name

    def schema(self, db_name):
        conn = sqlite3.connect(self.fa.path(db_name))
        cols = [r[1] for r in conn.execute("PRAGMA table_info(data)")]
        conn.close()
        return cols

    def query(self, sql, db_name):
        try:
            conn = self._connect(db_name)
            rows = conn.execute(sql).fetchmany(20)
            conn.close()
            return self._format(rows)
        except Exception as e:
            return f"SQL Error: {e}"

    def update(self, db_name, row_num, column, value):
        try:
            conn = self._connect(db_name)
            # Use row number as position (1-based) mapped to rowid via subquery
            conn.execute(
                f'UPDATE data SET "{column}"=? WHERE rowid='
                f'(SELECT rowid FROM data LIMIT 1 OFFSET ?)',
                (value, row_num - 1)
            )
            conn.commit()
            # Fetch the updated row by same offset to show user
            row = conn.execute(
                f"SELECT * FROM data LIMIT 1 OFFSET {row_num - 1}"
            ).fetchone()
            conn.close()
            return self._format([row]) if row else "Updated. Row not found."
        except Exception as e:
            return f"SQL Error: {e}"