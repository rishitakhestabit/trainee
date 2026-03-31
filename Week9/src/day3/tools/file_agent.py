# import os, re

# OUT = os.path.join(os.getcwd(), "output")
# os.makedirs(OUT, exist_ok=True)

# class FileAgent:
#     def path(self, name):
#         return os.path.join(OUT, os.path.basename(name))

#     def save(self, name, content):
#         p = self.path(name)
#         with open(p, "w", encoding="utf-8") as f:
#             f.write(content.strip())
#         return p

#     def read(self, name):
#         p = self.path(name)
#         return open(p).read() if os.path.exists(p) else None

#     @staticmethod
#     def detect(query, ext):
#         m = re.search(rf"(\w+\.{ext})", query)
#         return m.group(1) if m else None

#     @staticmethod
#     def default_name(query, ext):
#         """Derive a filename from the first noun in the query, never hardcode."""
#         m = re.search(r"\b([a-zA-Z]+(?:s)?)\b", query)
#         base = m.group(1).lower() if m else "file"
#         return f"{base}.{ext}"

#     @staticmethod
#     def extract_csv(text):
#         lines = []
#         for line in text.splitlines():
#             s = line.strip().strip("`").strip()
#             if s and "," in s and not s.startswith(("#", "//", "```")):
#                 lines.append(s)
#         return "\n".join(lines)


import os, re

OUT = os.path.join(os.getcwd(), "output")
os.makedirs(OUT, exist_ok=True)

class FileAgent:
    def path(self, name):
        return os.path.join(OUT, os.path.basename(name))

    def save(self, name, content):
        p = self.path(name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content.strip())
        return p

    def read(self, name):
        p = self.path(name)
        return open(p).read() if os.path.exists(p) else None

    @staticmethod
    def detect(query, ext):
        m = re.search(rf"(\w+\.{ext})", query)
        return m.group(1) if m else None

    @staticmethod
    def default_name(query, ext):
        m = re.search(r"\b([a-zA-Z]+)\b", query)
        base = m.group(1).lower() if m else "file"
        return f"{base}.{ext}"

    @staticmethod
    def clean_csv(text):
        """Remove only markdown fences/backticks, keep all data lines including header."""
        lines = []
        for line in text.splitlines():
            s = line.strip()
            if s and not s.startswith(("```", "#", "//")):
                lines.append(s)
        return "\n".join(lines)