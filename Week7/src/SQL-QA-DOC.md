# SQL-QA System (Day 4)

This document explains what I built for **Day 4 — SQL Question Answering System (Text -> SQL -> Answer)**.
---
![Final result](src/ss/day4ss/output.png)


We type a natural language question -> the system generates **SQL using an LLM** , validates it , runs it on **SQLite** , shows a clean summary of the result.

---

### 1) Put the dataset in the project
- I used the dataset file: `customers1000.csv`
- I placed it here:

```
src/data/sql/customers1000.csv
```

This keeps all Day‑4 SQL files in one place.

---

### 2) Converted CSV -> SQLite database
Because the assignment needs a database, the pipeline creates one automatically from the CSV:

- Output DB file:

```
src/data/sql/customers.db
```

- Output table created:

```
customers
```

**Important column fix**  
The CSV has a column named `Index`, which becomes `index` after cleaning, and `index` can break SQL.  
So I renamed it safely to:

- `Index` -> `row_index`

---

### 3) Saved API key safely in `.env`
I didn’t hardcode the key in code.

Project root file:

```
.env
```

Example:

```
GROQ_API_KEY=xxxxxxxxxxxxxxxx
GROQ_MODEL=your-working-groq-model-name
```
---

### 4) Loaded schema automatically
Before generating SQL, the system reads the database schema automatically so the LLM knows:
- which table exists
- which columns exist

That prevents wrong column names.

---

### 5) Generated SQL using the LLM (schema-aware)
When I type a question, the LLM is prompted with:
- schema
- rules (ONLY SELECT, no dangerous queries)
- the user question

It returns a single SQL query.

---

### 6) Validated SQL 
Before execution:
- it checks SQL starts with `SELECT`
- it blocks risky keywords like `DROP`, `DELETE`, `INSERT`, `UPDATE`, etc.
- it blocks multi‑statement queries

So even if the question is malicious, the SQL is rejected.

---

### 7) Executed SQL safely on SQLite
Once validated:
- it runs the SQL on `customers.db`
- fetches rows + columns
- returns results to the pipeline

---

### 8) Summarized the results
Instead of dumping a huge table, the pipeline prints:
- number of rows returned
- column names
- a short preview of the first few rows

This makes output readable.

---

## How to run (commands)

### 1) Create / rebuild DB from CSV 
Run this once (or anytime you change the CSV):

```bash
python -m src.pipelines.sql_pipeline --rebuild_db
```

### 2) Start the SQL-QA system
```bash
python -m src.pipelines.sql_pipeline
```

Then ask questions like:
- `list all customers from new york`
- `count customers by country`
- `show customers who subscribed in 2023`

Press **Ctrl+C** to exit.

---


### `src/pipelines/sql_pipeline.py`
**Main runner / pipeline**
- Converts CSV → SQLite (creates `customers.db`)
- Loads schema using `schema_loader`
- Runs the loop: question → SQL → validate → execute → summarize
- Prints final output in terminal

---

### `src/generator/sql_generator.py`
**Text → SQL generator (LLM)**
- Loads `.env` (so API key stays outside code)
- Builds the LLM client (Groq via LangChain)
- Generates SQL from (schema + question)
- Contains rules so output is ONLY a single SELECT query

---

### `src/utils/schema_loader.py`
**Schema reader**
- Connects to SQLite DB
- Extracts table + columns
- Formats schema into a clean string for prompts

---



