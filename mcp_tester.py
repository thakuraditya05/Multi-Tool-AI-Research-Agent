import asyncio
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()
PROJECT_DIR = Path(__file__).resolve().parent

# --- Windows npx helper (Best for Notion/Google packages) ---
def find_npx():
    node = shutil.which("node.exe") or shutil.which("node")
    npx_cmd = shutil.which("npx.cmd") or shutil.which("npx")
    if not node or not npx_cmd:
        raise RuntimeError("Node.js/npm were not found on PATH.")
    npx_cli = os.path.join(os.path.dirname(npx_cmd), "node_modules", "npm", "bin", "npx-cli.js")
    return node, [npx_cli]

node_cmd, npx_args = find_npx()
full_env = dict(os.environ)

# --- Configuration for ONLY the 3 tools ---
test_configs = {
    "notion": {
        "transport": "stdio",
        "command": node_cmd,
        "args": npx_args + ["-y", "@notionhq/notion-mcp-server"],
        "env": {
            **full_env,
            "NOTION_TOKEN": os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY", "")
        }
    },
    "gdrive": {
        "transport": "stdio",
        "command": node_cmd,
        "args": npx_args + ["-y", "@modelcontextprotocol/server-gdrive"],
        "env": {
            **full_env,
            "GDRIVE_OAUTH_PATH": os.environ.get("GDRIVE_OAUTH_PATH", str(PROJECT_DIR / "gcp-oauth.keys.json")),
            "GDRIVE_CREDENTIALS_PATH": os.environ.get("GDRIVE_CREDENTIALS_PATH", str(PROJECT_DIR / ".gdrive-server-credentials.json"))
        }
    },
    "gmail": {
        "transport": "stdio",
        "command": node_cmd,
        "args": npx_args + ["-y", "@mcp-z/mcp-gmail", "--headless"],
        "env": {
            **full_env,
            "GOOGLE_CLIENT_ID": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "GOOGLE_CLIENT_SECRET": os.environ.get("GOOGLE_CLIENT_SECRET", "")
        }
    }
}

async def test_server_isolated(server_name, config):
    print(f"\n⏳ Testing {server_name.upper()}...")
    # Ek baar mein sirf ek tool ko load karke check karega
    client = MultiServerMCPClient({server_name: config})
    try:
        tools = await client.get_tools()
        print(f"✅ SUCCESS: {server_name} loaded {len(tools)} tools!")
        for t in tools:
            print(f"   - {t.name}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {server_name}")
        print(f"   Error: {str(e)}")
        return False

async def run_diagnostics():
    print("🚀 Starting Isolated MCP Diagnostics for Notion, GDrive, and Gmail\n" + "="*60)
    for name, config in test_configs.items():
        await test_server_isolated(name, config)
    print("\n" + "="*60 + "\n🏁 Testing Complete.")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())



















# """Isolated startup check for Notion, Google Drive, and Gmail MCP servers."""

# import asyncio
# import argparse
# import os
# import shutil
# import sys
# from pathlib import Path

# from dotenv import load_dotenv
# from langchain_mcp_adapters.client import MultiServerMCPClient

# load_dotenv()
# PROJECT_DIR = Path(__file__).resolve().parent

# parser = argparse.ArgumentParser(description="Test one or more MCP servers independently.")
# parser.add_argument(
#     "--server", choices=("notion", "gdrive", "gmail"), action="append",
#     help="Server to test; repeat for multiple servers. Defaults to notion if omitted.",
# )
# parser.add_argument("--include-drive", action="store_true", help=argparse.SUPPRESS)
# parser.add_argument("--include-gmail", action="store_true", help=argparse.SUPPRESS)
# options = parser.parse_args()


# def find_npx():
#     """Launch npm's JS CLI with node.exe, bypassing cmd.exe/.cmd quoting issues."""
#     node = shutil.which("node.exe") or shutil.which("node")
#     npx_cmd = shutil.which("npx.cmd") or shutil.which("npx")
#     if not node or not npx_cmd:
#         raise RuntimeError("Node.js/npm were not found on PATH. Install Node.js and reopen the terminal.")
#     npx_cli = os.path.join(os.path.dirname(npx_cmd), "node_modules", "npm", "bin", "npx-cli.js")
#     if not os.path.isfile(npx_cli):
#         raise RuntimeError(f"Could not find npm's npx-cli.js next to npx.cmd: {npx_cli}")
#     return node, [npx_cli]


# def npm_server(package, *package_args):
#     command, prefix_args = find_npx()
#     return {
#         "transport": "stdio",
#         "command": command,
#         "args": prefix_args + ["-y", package, *package_args],
#         # Preserve PATH and other inherited environment needed by Node/npm.
#         "env": dict(os.environ),
#     }


# servers = options.server if options.server else ["notion"]
# if options.include_drive and "gdrive" not in servers:
#     servers.append("gdrive")
# if options.include_gmail and "gmail" not in servers:
#     servers.append("gmail")

# test_config = {}
# if "notion" in servers:
#     notion_config = npm_server("@notionhq/notion-mcp-server")
#     notion_config["env"]["NOTION_TOKEN"] = os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY", "")
#     test_config["notion"] = notion_config

# if "gdrive" in servers:
#     drive_config = npm_server("@modelcontextprotocol/server-gdrive")
#     drive_config["env"]["GDRIVE_OAUTH_PATH"] = os.getenv(
#         "GDRIVE_OAUTH_PATH", str(PROJECT_DIR / "gcp-oauth.keys.json")
#     )
#     drive_config["env"]["GDRIVE_CREDENTIALS_PATH"] = os.getenv(
#         "GDRIVE_CREDENTIALS_PATH", str(PROJECT_DIR / ".gdrive-server-credentials.json")
#     )
#     test_config["gdrive"] = drive_config

# if "gmail" in servers:
#     gmail_config = npm_server("@mcp-z/mcp-gmail")
#     gmail_config["env"]["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID", "")
#     gmail_config["env"]["GOOGLE_CLIENT_SECRET"] = os.getenv("GOOGLE_CLIENT_SECRET", "")
#     # First authorization is interactive; headless mode prints a URL instead
#     # of hanging or trying to open a browser in the subprocess.
#     test_config["gmail"] = {**gmail_config, "args": gmail_config["args"] + ["--headless"]}


# async def run_diagnostics():
#     print("Testing MCP server(s): " + ", ".join(test_config), flush=True)
#     launcher, launcher_args = find_npx()
#     print("Node launcher:", launcher, flush=True)
#     print("npx CLI:", launcher_args[0], flush=True)
#     client = MultiServerMCPClient(test_config)
#     all_tools = []
#     # Isolate failures per child process. get_tools() with no server_name runs
#     # all servers concurrently and obscures which process closed its connection.
#     for server_name in test_config:
#         print(f"\nStarting {server_name}...", flush=True)
#         try:
#             tools = await client.get_tools(server_name=server_name)
#         except Exception as exc:
#             print(f"FAILED: {server_name}: {type(exc).__name__}: {exc}", flush=True)
#             nested = getattr(exc, "exceptions", None)
#             while nested:
#                 exc = nested[0]
#                 print(f"  caused by {type(exc).__name__}: {exc}", flush=True)
#                 nested = getattr(exc, "exceptions", None)
#             if server_name == "notion":
#                 print("  Confirm .env has NOTION_TOKEN=... (or NOTION_API_KEY=...) with a valid integration token.", flush=True)
#             elif server_name == "gdrive":
#                 print("  Complete the server's one-time `npx -y @modelcontextprotocol/server-gdrive auth` setup first.", flush=True)
#             elif server_name == "gmail":
#                 print("  Gmail first needs OAuth authorization; --headless prints the URL if login is not saved yet.", flush=True)
#             continue
#         print(f"Loaded {len(tools)} tools from {server_name}:", flush=True)
#         for item in tools:
#             print(f" - {item.name}", flush=True)
#         all_tools.extend(tools)

#     print(f"\nTotal tools loaded: {len(all_tools)}", flush=True)


# if __name__ == "__main__":
#     asyncio.run(run_diagnostics())
