import importlib.util
import shutil
import subprocess
import sys

print("python", sys.version)
for m in ["playwright", "reportlab", "fitz", "markdown", "weasyprint", "bs4"]:
    print(m, bool(importlib.util.find_spec(m)))
print("node", shutil.which("node"))
print("npm", shutil.which("npm"))
print("npx", shutil.which("npx"))
print("mmdc", shutil.which("mmdc"))
print("pandoc", shutil.which("pandoc"))
try:
    subprocess.run(["npm", "-v"], check=False)
except Exception as e:
    print("npm err", e)
