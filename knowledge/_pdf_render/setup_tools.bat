@echo off
cd /d "d:\BLUE-WATER\docs\knowledge\_pdf_render"
echo === npm init ===
call npm init -y
echo === install mermaid-cli ===
call npm install @mermaid-js/mermaid-cli@11.4.2 --no-fund --no-audit
echo === create venv ===
python -m venv .venv
call .venv\Scripts\activate.bat
echo === pip install ===
python -m pip install --upgrade pip
python -m pip install playwright reportlab pillow markdown
echo === playwright chromium ===
python -m playwright install chromium
echo === DONE ===
dir node_modules\@mermaid-js\mermaid-cli\package.json
python -c "import playwright, reportlab; print('ok', reportlab.Version)"
