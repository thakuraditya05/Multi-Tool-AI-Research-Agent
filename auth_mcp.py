import os
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# .env file load karein taaki GOOGLE_CLIENT_ID mil sake
load_dotenv()
PROJECT_DIR = Path(__file__).resolve().parent

def find_npx():
    node = shutil.which("node.exe") or shutil.which("node")
    npx_cmd = shutil.which("npx.cmd") or shutil.which("npx")
    npx_cli = os.path.join(os.path.dirname(npx_cmd), "node_modules", "npm", "bin", "npx-cli.js")
    return node, [npx_cli]

node_cmd, npx_args = find_npx()
full_env = dict(os.environ)

print("\n" + "="*50)
print("1. STARTING GOOGLE DRIVE AUTH")
print("="*50)
drive_env = full_env.copy()
# Drive ko exact paths batana zaroori hai
drive_env["GDRIVE_OAUTH_PATH"] = str(PROJECT_DIR / "gcp-oauth.keys.json")
drive_env["GDRIVE_CREDENTIALS_PATH"] = str(PROJECT_DIR / ".gdrive-server-credentials.json")

try:
    subprocess.run([node_cmd] + npx_args + ["-y", "@modelcontextprotocol/server-gdrive", "auth"], env=drive_env)
except Exception as e:
    print(f"Drive Auth Error: {e}")

print("\n" + "="*50)
print("2. STARTING GMAIL AUTH")
print("="*50)
print("NOTE: Gmail auth start hone par terminal mein ek URL aayega.")
print("Browser mein us URL ko open karke login karein.")
print("Jab Auth complete ho jaye, toh yahan click karke 'Ctrl + C' dabayein taaki script band ho jaye.")
print("="*50 + "\n")

try:
    subprocess.run([node_cmd] + npx_args + ["-y", "@mcp-z/mcp-gmail", "--headless"], env=full_env)
except Exception as e:
    print(f"Gmail Auth Error: {e}")