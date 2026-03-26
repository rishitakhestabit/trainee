import os
import re
import csv
from typing import Optional


class FileAgent:
    """
    Sandboxed File Agent with two strictly separated directories:

        READ sandbox  → base_dir/data/    (source files, NEVER overwritten)
        WRITE sandbox → base_dir/output/  (all new/created files go here)

    Both folders are created automatically on first run.
    Uploaded CSVs from Streamlit are saved to data/ (read-only sandbox).
    Agent-created files always go to output/ with auto-versioning.
    """

    def __init__(self, base_dir: str = "."):
        self.base_dir = os.path.abspath(base_dir)

        # ── Sandboxes (auto-created) ──────────────────────────────────────────
        self.read_sandbox  = os.path.join(self.base_dir, "data")    # READ-ONLY
        self.write_sandbox = os.path.join(self.base_dir, "output")  # WRITE-ONLY

        os.makedirs(self.read_sandbox,  exist_ok=True)
        os.makedirs(self.write_sandbox, exist_ok=True)

    # ─────────────────────────────────────────────────────────────────────────
    # Path helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _resolve_read_path(self, filename: str) -> Optional[str]:
        """
        Search for a file to READ.
        Order: data/ → output/ → base_dir
        Returns absolute path if found, else None.
        """
        bare = os.path.basename(filename)  # strip any directory prefix
        search_dirs = [self.read_sandbox, self.write_sandbox, self.base_dir]
        for directory in search_dirs:
            candidate = os.path.abspath(os.path.join(directory, bare))
            if not candidate.startswith(self.base_dir):
                continue  # block path traversal
            if os.path.exists(candidate):
                return candidate
        return None

    def _resolve_write_path(self, filename: str) -> str:
        """
        Always writes into output/ sandbox.
        Auto-versions if file already exists:
            inventory.csv → inventory_v2.csv → inventory_v3.csv ...
        Never touches data/ (read-only sandbox).
        """
        bare = os.path.basename(filename)  # ignore any directory prefix
        base, ext = os.path.splitext(bare)

        candidate = os.path.join(self.write_sandbox, bare)
        version = 2
        while os.path.exists(candidate):
            candidate = os.path.join(self.write_sandbox, f"{base}_v{version}{ext}")
            version += 1

        final_path = os.path.abspath(candidate)
        if not final_path.startswith(self.write_sandbox):
            raise PermissionError(f"Blocked unsafe write path: {final_path}")
        return final_path

    # ─────────────────────────────────────────────────────────────────────────
    # Core operations
    # ─────────────────────────────────────────────────────────────────────────

    def _list_files(self) -> str:
        lines = []
        for label, directory in [
            ("data/   (read-only — source files)", self.read_sandbox),
            ("output/ (agent-created files)",      self.write_sandbox),
        ]:
            files = sorted(os.listdir(directory))
            lines.append(f"[{label}]")
            lines += [f"  {f}" for f in files] if files else ["  (empty)"]
            lines.append("")
        return "\n".join(lines).strip()

    def _read_file(self, filename: str) -> str:
        resolved = self._resolve_read_path(filename)
        if not resolved:
            return (
                f"File not found: '{filename}'\n"
                f"Searched in:\n"
                f"  {self.read_sandbox}\n"
                f"  {self.write_sandbox}\n"
                f"  {self.base_dir}"
            )
        with open(resolved, "r", encoding="utf-8") as f:
            return f.read()

    def _write_file(self, filename: str, content: str) -> str:
        """Write any text/csv/md file — always goes to output/ with auto-versioning."""
        if filename.lower().endswith(".db"):
            return "File agent error: .db files cannot be written as plain text."

        full_path = self._resolve_write_path(filename)
        with open(full_path, "w", encoding="utf-8", newline="") as f:
            f.write(content or "")

        saved_name = os.path.basename(full_path)
        return f"Wrote file: output/{saved_name}"

    def save_uploaded_file(self, filename: str, content: bytes) -> str:
        """
        Called by Streamlit when a user uploads a file.
        Saves to data/ (read-only sandbox). Never overwrites.
        """
        dest = os.path.join(self.read_sandbox, os.path.basename(filename))
        if os.path.exists(dest):
            return f"File already exists in data/: {filename} (not overwritten)"
        with open(dest, "wb") as f:
            f.write(content)
        return f"Saved uploaded file to data/{filename}"

    # ─────────────────────────────────────────────────────────────────────────
    # Intent extraction helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _extract_file_name(self, request: str) -> Optional[str]:
        match = re.search(r"([\w\-./\\]+\.(txt|csv|md))\b", request, re.IGNORECASE)
        if match:
            return os.path.basename(match.group(1))  # always strip directory prefix
        return None

    def _extract_write_content(self, request: str) -> str:
        # write_match = re.search(r"\bwrite\b(.+)$", request, re.IGNORECASE | re.DOTALL)
        # if write_match:
        #     return write_match.group(1).strip()
        # return ""
    
        write_match = re.search(r"--- Generated CSV content.*?\n(.+)", request, re.DOTALL)
        if write_match:
            return write_match.group(1).strip()

        # fallback
        write_match = re.search(r"\bwrite\b(.+)$", request, re.IGNORECASE | re.DOTALL)
        if write_match:
            return write_match.group(1).strip()

        return ""

    # ─────────────────────────────────────────────────────────────────────────
    # Main dispatcher
    # ─────────────────────────────────────────────────────────────────────────

    async def process_request(self, request: str) -> str:
        lowered = request.lower().strip()

        # ── List files ────────────────────────────────────────────────────────
        if any(x in lowered for x in ["list files", "show files", "display files", "list all files"]):
            return self._list_files()

        file_name = self._extract_file_name(request)

        READ_KEYWORDS  = [
            "read", "show", "display", "open", "view", "contents", "content",
            "analyze", "analysis", "load", "fetch", "get", "summarize",
            "inspect", "check", "print", "query",
        ]
        WRITE_KEYWORDS = ["create", "write", "save", "generate", "make"]

        if file_name:
            has_read  = any(x in lowered for x in READ_KEYWORDS)
            has_write = any(x in lowered for x in WRITE_KEYWORDS)

            # ── Ambiguous: both read + write keywords ─────────────────────────
            # Rule: file exists → READ (protect source data)
            #       file missing → WRITE (intentional creation)
            if has_read and has_write:
                if self._resolve_read_path(file_name):
                    return self._read_file(file_name)
                content = self._extract_write_content(request)
                return self._write_file(file_name, content)

            if has_read:
                return self._read_file(file_name)

            if has_write:
                content = self._extract_write_content(request)
                return self._write_file(file_name, content)

        return "File agent could not determine the requested file operation."