from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage , SystemMessage
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool, BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import aiosqlite
import requests
import asyncio
import threading
from pathlib import Path


import os
import shutil

load_dotenv()


PROJECT_DIR = Path(__file__).resolve().parent
_PROJECT_DIR=PROJECT_DIR

# Dedicated async loop for backend tasks
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
_ASYNC_THREAD.start()

def _submit_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)

def run_async(coro):
    return _submit_async(coro).result()

def submit_async_task(coro):
    """Schedule a coroutine on the backend event loop."""
    return _submit_async(coro)

# -------------------
# 1. LLM
# -------------------
# llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

llm = ChatGoogleGenerativeAI(
    # model="gemini-3.8-flash",
    # model="gemini-2.5-flash",
    model="gemini-3.5-flash-lite",
    
    temperature=0,
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

# -------------------
# 2. Tools
# -------------------
search_tool = DuckDuckGoSearchRun(region="us-en")


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()





def find_npx():
    node = shutil.which("node.exe") or shutil.which("node")
    npx_cmd = shutil.which("npx.cmd") or shutil.which("npx")
    npx_cli = os.path.join(os.path.dirname(npx_cmd), "node_modules", "npm", "bin", "npx-cli.js")
    return node, [npx_cli]


node_cmd, npx_args = find_npx()
full_env = dict(os.environ) # Node.js ko OS environment dene ke liye

client = MultiServerMCPClient(
    {
        # 1. Local Filesystem (Aapke PC ki files/folders padhne/likhne ke liye)
        "filesystem": {
            "transport": "stdio",
            "command": "npx.cmd",
            # Aap apna C:/ drive ka koi bhi path de sakte hain
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/Users/thaku/Desktop"],
        },
        
        # 2. Memory / Knowledge Graph (AI ko permanent memory dene ke liye)
        "memory": {
            "transport": "stdio",
            "command": "npx.cmd",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
        },
        
        # # 3. Puppeteer (Websites ka data scrape karne ke liye)
        "puppeteer": {
            "transport": "stdio",
            "command": "npx.cmd",
            "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        },

        # # 4. Brave Search (Deep internet search ke liye)
        "brave_search": {
            "transport": "stdio",
            "command": "npx.cmd",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            # Python Node.js ko explicitly key pass karega
            "env": {
                "BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY", "")
            }
        },

        # 5. GitHub (Code aur repositories check karne ke liye)
        "github": {
            "transport": "stdio",
            "command": "npx.cmd",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            # Iske liye .env me GITHUB_PERSONAL_ACCESS_TOKEN chahiye
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
            }
        },
        
        
        
        "notion": {
            "transport": "stdio",
            "command": node_cmd,
            "args": npx_args + ["-y", "@notionhq/notion-mcp-server"],
            "env": {
                **full_env,
                "NOTION_TOKEN": os.environ.get("NOTION_TOKEN") or os.environ.get("NOTION_API_KEY", "")
            }
        },

        # 7. Google Drive
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
        
        # 8. Gmail
        "gmail": {
            "transport": "stdio",
            "command": node_cmd,
            "args": npx_args + ["-y", "@mcp-z/mcp-gmail", "--headless"],
            "env": {
                **full_env,
                "GOOGLE_CLIENT_ID": os.environ.get("GOOGLE_CLIENT_ID", ""),
                "GOOGLE_CLIENT_SECRET": os.environ.get("GOOGLE_CLIENT_SECRET", "")
            }
        },
        
        
        
        
        
        # 10. Math Server (Jo aapne khud local banaya tha)
        "arith": {
            "transport": "stdio",
            "command": "python",
            "args": ["mcp-server/math.py"],
        },
        "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            # "transport": "sse",  # if this fails, try "sse"
            "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
        },
    }
)


# client = MultiServerMCPClient(
#     {
#         # 1. Local Filesystem
#         "filesystem": {
#             "transport": "stdio",
#             "command": node_cmd,
#             "args": npx_args + ["-y", "@modelcontextprotocol/server-filesystem", "C:/Users/thaku/Desktop"],
#             "env": full_env
#         },
        
#         # 2. Memory / Knowledge Graph
#         "memory": {
#             "transport": "stdio",
#             "command": node_cmd,
#             "args": npx_args + ["-y", "@modelcontextprotocol/server-memory"],
#             "env": full_env
#         },
        
#         # 3. Puppeteer
#         "puppeteer": {
#             "transport": "stdio",
#             "command": node_cmd,
#             "args": npx_args + ["-y", "@modelcontextprotocol/server-puppeteer"],
#             "env": full_env
#         },

#         # 4. Brave Search
#         "brave_search": {
#             "transport": "stdio",
#             "command": node_cmd,
#             "args": npx_args + ["-y", "@modelcontextprotocol/server-brave-search"],
#             "env": {
#                 **full_env,
#                 "BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY", "")
#             }
#         },

#         # 5. GitHub
#         "github": {
#             "transport": "stdio",
#             "command": node_cmd,
#             "args": npx_args + ["-y", "@modelcontextprotocol/server-github"],
#             "env": full_env
#         },
#         # 9. Math Server (Local Python)
#         "arith": {
#             "transport": "stdio",
#             "command": "python",
#             "args": ["mcp-server/math.py"],
#         },
        
#         # 10. Expense
#         "expense": {
#             "transport": "sse",
#             "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
#         }
#     }
# )


def load_mcp_tools() -> list[BaseTool]:
    try:
        print("⏳ Loading MCP tools...")
        tools = run_async(client.get_tools())
        print(f"✅ Successfully loaded {len(tools)} tools!")
        return tools
    except Exception as e:
        print(f"\n❌ ERROR LOADING MCP TOOLS: {str(e)}\n")
        return []

mcp_tools = load_mcp_tools()

tools = [search_tool, get_stock_price, *mcp_tools]
llm_with_tools = llm.bind_tools(tools) if tools else llm

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------

# async def chat_node(state: ChatState):
#     """LLM node that may answer or request a tool call."""
#     messages = state["messages"]
#     response = await llm_with_tools.ainvoke(messages)
#     return {"messages": [response]}


async def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    # AI ko strict instruction dena zaroori hai
    system_prompt = SystemMessage(
        content=(
            "You are a highly capable AI assistant equipped with multiple tools including "
            "Gmail, Google Drive, GitHub, local filesystem, Brave Search, and a Math tool. "
            "IMPORTANT: When a user asks you to read their emails, check their Drive files, "
            "or access personal data, DO NOT refuse. You have the authorization and the tools to do so. "
            "ALWAYS use the provided tools (like gmail or gdrive) to fetch the real information "
            "and then answer the user's question."
        )
    )
    # System prompt ko user ke messages ke aage lagana
    messages = [system_prompt] + state["messages"]
    # LLM ko call karna
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools) if tools else None

# -------------------
# 5. Checkpointer
# -------------------


async def _init_checkpointer():
    conn = await aiosqlite.connect(database="chatbot.db")
    return AsyncSqliteSaver(conn)


checkpointer = run_async(_init_checkpointer())

# -------------------
# 6. Graph
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")

if tool_node:
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")
else:
    graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
async def _alist_threads():
    all_threads = set()
    async for checkpoint in checkpointer.alist(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


def retrieve_all_threads():
    return run_async(_alist_threads())



















# from langgraph.graph import StateGraph, START, END
# from typing import TypedDict, Annotated
# from langchain_core.messages import BaseMessage, HumanMessage
# from langchain_openai import ChatOpenAI
# from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
# from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolNode, tools_condition
# from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_core.tools import tool, BaseTool
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from dotenv import load_dotenv
# import aiosqlite
# import requests
# import asyncio
# import threading

# load_dotenv()

# # Dedicated async loop for backend tasks
# _ASYNC_LOOP = asyncio.new_event_loop()
# _ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
# _ASYNC_THREAD.start()


# def _submit_async(coro):
#     return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)


# def run_async(coro):
#     return _submit_async(coro).result()


# def submit_async_task(coro):
#     """Schedule a coroutine on the backend event loop."""
#     return _submit_async(coro)


# # -------------------
# # 1. LLM
# # -------------------
# llm = ChatOpenAI()

# # -------------------
# # 2. Tools
# # -------------------
# search_tool = DuckDuckGoSearchRun(region="us-en")


# @tool
# def get_stock_price(symbol: str) -> dict:
#     """
#     Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
#     using Alpha Vantage with API key in the URL.
#     """
#     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
#     r = requests.get(url)
#     return r.json()


# client = MultiServerMCPClient(
#     {
#         "arith": {
#             "transport": "stdio",
#             "command": "python3",
#             "args": ["/Users/nitish/Desktop/mcp-math-server/main.py"],
#         },
#         "expense": {
#             "transport": "streamable_http",  # if this fails, try "sse"
#             "url": "https://splendid-gold-dingo.fastmcp.app/mcp"
#         }
#     }
# )


# def load_mcp_tools() -> list[BaseTool]:
#     try:
#         return run_async(client.get_tools())
#     except Exception:
#         return []


# mcp_tools = load_mcp_tools()

# tools = [search_tool, get_stock_price, *mcp_tools]
# llm_with_tools = llm.bind_tools(tools) if tools else llm

# # -------------------
# # 3. State
# # -------------------
# class ChatState(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]

# # -------------------
# # 4. Nodes
# # -------------------
# async def chat_node(state: ChatState):
#     """LLM node that may answer or request a tool call."""
#     messages = state["messages"]
#     response = await llm_with_tools.ainvoke(messages)
#     return {"messages": [response]}


# tool_node = ToolNode(tools) if tools else None

# # -------------------
# # 5. Checkpointer
# # -------------------


# async def _init_checkpointer():
#     conn = await aiosqlite.connect(database="chatbot.db")
#     return AsyncSqliteSaver(conn)


# checkpointer = run_async(_init_checkpointer())

# # -------------------
# # 6. Graph
# # -------------------
# graph = StateGraph(ChatState)
# graph.add_node("chat_node", chat_node)
# graph.add_edge(START, "chat_node")

# if tool_node:
#     graph.add_node("tools", tool_node)
#     graph.add_conditional_edges("chat_node", tools_condition)
#     graph.add_edge("tools", "chat_node")
# else:
#     graph.add_edge("chat_node", END)

# chatbot = graph.compile(checkpointer=checkpointer)

# # -------------------
# # 7. Helper
# # -------------------
# async def _alist_threads():
#     all_threads = set()
#     async for checkpoint in checkpointer.alist(None):
#         all_threads.add(checkpoint.config["configurable"]["thread_id"])
#     return list(all_threads)


# def retrieve_all_threads():
#     return run_async(_alist_threads())
