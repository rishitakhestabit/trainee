import os
import json
import csv
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from config import BASE_DIR


def _resolve_path(filepath: str) -> Path:
    p = Path(filepath)
    if p.is_absolute() or p.exists():
        return p
    candidate = BASE_DIR / filepath
    if candidate.exists():
        return candidate
    return p


# ================== FILE TOOLS ==================

def read_file(filepath: str) -> str:
    try:
        resolved = _resolve_path(filepath)
        with open(resolved, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    try:
        from config import OUTPUT_DIR
        filename = os.path.basename(filepath)
        safe_path = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {safe_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def append_file(filepath: str, content: str) -> str:
    try:
        from config import OUTPUT_DIR
        filename = os.path.basename(filepath)
        safe_path = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(safe_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully appended to {safe_path}"
    except Exception as e:
        return f"Error appending file: {str(e)}"


def list_directory(dirpath: str) -> List[str]:
    try:
        return os.listdir(dirpath)
    except Exception as e:
        return [f"Error listing directory: {str(e)}"]


# ================== CSV TOOLS ==================

def read_csv(filepath: str) -> Dict[str, Any]:
    """Read first 10 rows of a CSV file for preview."""
    try:
        limit = 10
        resolved = _resolve_path(filepath)
        with open(resolved, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
            headers = reader.fieldnames

        return {
            "headers": headers,
            "rows": rows[:limit],
            "total_rows": len(rows),
            "note": f"Showing first {limit} of {len(rows)} rows",
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_csv_columns(filepath: str) -> Dict[str, Any]:
    """
    Generic column-level analysis for ANY CSV file.
    Returns stats for every column: counts, unique values, numeric stats, top values.
    No hardcoded column names — works with any CSV structure.
    """
    try:
        resolved = _resolve_path(filepath)
        with open(resolved, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
            headers = reader.fieldnames

        if not headers:
            return {"error": "No headers found in CSV"}

        total_rows = len(rows)
        analysis = {"total_rows": total_rows, "total_columns": len(headers), "columns": {}}

        for header in headers:
            values = [str(row.get(header, "")).strip() for row in rows]
            non_empty = [v for v in values if v]

            # count frequency of each unique value
            freq = {}
            for v in non_empty:
                freq[v] = freq.get(v, 0) + 1

            # top 10 most frequent values
            top_values = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]

            # numeric stats if applicable
            numeric_values = []
            for v in non_empty:
                try:
                    numeric_values.append(float(v))
                except:
                    pass

            col_info = {
                "total": total_rows,
                "non_empty": len(non_empty),
                "empty": total_rows - len(non_empty),
                "unique_count": len(freq),
                "top_values": [{"value": k, "count": v} for k, v in top_values],
            }

            if numeric_values:
                col_info["numeric_stats"] = {
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "mean": round(sum(numeric_values) / len(numeric_values), 4),
                    "sum": round(sum(numeric_values), 4),
                }

            analysis["columns"][header] = col_info

        return analysis

    except Exception as e:
        return {"error": str(e)}


def get_csv_summary(filepath: str) -> Dict[str, Any]:
    """
    Smart CSV summary — works with ANY CSV file.
    Automatically detects column types and produces relevant summaries:
    - For text/categorical columns: frequency counts and top values
    - For numeric columns: sum, mean, min, max
    - For date columns: date range
    No hardcoded column names.
    """
    try:
        resolved = _resolve_path(filepath)
        with open(resolved, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
            headers = reader.fieldnames or []

        if not headers:
            return {"error": "No headers found in CSV"}

        total_rows = len(rows)
        summary = {
            "file": str(resolved),
            "total_rows": total_rows,
            "columns": headers,
            "categorical_analysis": {},
            "numeric_analysis": {},
            "date_columns": {},
        }

        for header in headers:
            values = [str(row.get(header, "")).strip() for row in rows]
            non_empty = [v for v in values if v]

            if not non_empty:
                continue

            # try numeric
            numeric_values = []
            for v in non_empty:
                try:
                    numeric_values.append(float(v))
                except:
                    pass

            # try date
            date_values = []
            for v in non_empty[:20]:  # sample first 20 to detect date format
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
                    try:
                        from datetime import datetime as dt
                        date_values.append(dt.strptime(v, fmt).date())
                        break
                    except:
                        pass

            if len(numeric_values) > len(non_empty) * 0.7:
                # mostly numeric column
                summary["numeric_analysis"][header] = {
                    "sum": round(sum(numeric_values), 4),
                    "mean": round(sum(numeric_values) / len(numeric_values), 4),
                    "min": min(numeric_values),
                    "max": max(numeric_values),
                    "count": len(numeric_values),
                }
            elif len(date_values) > 5:
                # date column
                all_dates = []
                for v in non_empty:
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
                        try:
                            from datetime import datetime as dt
                            all_dates.append(dt.strptime(v, fmt).date())
                            break
                        except:
                            pass
                if all_dates:
                    summary["date_columns"][header] = {
                        "start": str(min(all_dates)),
                        "end": str(max(all_dates)),
                        "count": len(all_dates),
                    }
            else:
                # categorical column — count frequency
                freq = {}
                for v in non_empty:
                    freq[v] = freq.get(v, 0) + 1
                top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:15]
                summary["categorical_analysis"][header] = {
                    "unique_count": len(freq),
                    "top_values": [{"value": k, "count": v, "pct": round(v/total_rows*100, 1)} for k, v in top],
                }

        return summary

    except Exception as e:
        return {"error": str(e)}


# ================== JSON TOOLS ==================

def read_json(filepath: str) -> Dict[str, Any]:
    try:
        resolved = _resolve_path(filepath)
        with open(resolved, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}


def write_json(filepath: str, data: Any, indent: int = 2) -> str:
    try:
        from config import OUTPUT_DIR
        filename = os.path.basename(filepath)
        safe_path = os.path.join(OUTPUT_DIR, filename)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(safe_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent)
        return f"Successfully wrote JSON to {safe_path}"
    except Exception as e:
        return f"Error writing JSON: {str(e)}"


# ================== LOG TOOLS ==================

def create_log_entry(log_file: str, agent_name: str, action: str, details: Dict[str, Any]) -> str:
    try:
        parent = os.path.dirname(log_file)
        if parent:
            os.makedirs(parent, exist_ok=True)
        log_entry = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "agent": agent_name,
            "action": action,
            "details": details,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        return log_file
    except Exception as e:
        return f"Error creating log: {str(e)}"


def read_logs(log_dir: str) -> List[Dict[str, Any]]:
    logs = []
    limit = 8
    try:
        if not os.path.exists(log_dir):
            return logs
        for filename in os.listdir(log_dir):
            if not filename.endswith(".log"):
                continue
            filepath = os.path.join(log_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        logs.append(json.loads(line))
                    except:
                        continue
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return logs[:limit]
    except Exception as e:
        return [{"error": str(e)}]