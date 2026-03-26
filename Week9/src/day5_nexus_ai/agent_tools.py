from autogen_core.tools import FunctionTool
from typing import List
import tools


def get_coder_tools() -> List:
    return []


def get_optimizer_tools() -> List:
    return []


def get_reporter_tools() -> List:
    return []


def get_analyst_tools() -> List[FunctionTool]:
    return [
        FunctionTool(
            tools.get_csv_summary,
            description=(
                "Smart CSV summary for ANY CSV file. "
                "Automatically detects column types and returns: "
                "frequency counts for categorical columns (like Country, City, Category), "
                "sum/mean/min/max for numeric columns, date ranges for date columns. "
                "Use this first for any CSV analysis task. "
                "Args: filepath (str) — the CSV filename e.g. 'customers-1000.csv'"
            )
        ),
        FunctionTool(
            tools.analyze_csv_columns,
            description=(
                "Detailed column-by-column analysis of ANY CSV file. "
                "Returns top values, unique counts, and numeric stats for every column. "
                "Use this when you need deep per-column analysis. "
                "Args: filepath (str) — the CSV filename"
            )
        ),
        FunctionTool(
            tools.read_csv,
            description=(
                "Read first 10 rows of a CSV file for preview. "
                "Use to understand structure before deeper analysis. "
                "Args: filepath (str) — the CSV filename"
            )
        ),
        FunctionTool(
            tools.read_file,
            description="Read any text file. Args: filepath (str)"
        ),
        FunctionTool(
            tools.list_directory,
            description="List files in a directory. Args: dirpath (str)"
        ),
    ]