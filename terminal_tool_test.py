import os
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import yfinance as yf
from pymongo import MongoClient
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# -------------------
# 1. LLM
# -------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite", # Ya jo tumhara current working model ho
    temperature=0,
    google_api_key=os.environ.get("GEMINI_API_KEY_TOOL")
)

# -------------------
# 2. THE 5 NEW TOOLS
# -------------------

@tool
def scrape_website_text(url: str) -> str:
    """Scrapes and extracts the main text content from a given web page URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join(soup.stripped_strings)
        return text[:3000] + "... [TRUNCATED]" # Returning first 3000 chars
    except Exception as e:
        return f"Scraping Error: {str(e)}"

@tool
def save_report_to_file(filename: str, markdown_content: str) -> str:
    """Saves research findings or reports into a Markdown (.md) file locally."""
    try:
        if not filename.endswith(".md"):
            filename += ".md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        return f"Success: Report saved locally as {filename} in the current directory."
    except Exception as e:
        return f"File Error: {str(e)}"

@tool
def fetch_market_data(ticker: str) -> dict:
    """Fetches real-time stock price, market cap, and PE ratio using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "current_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("forwardPE"),
            "sector": info.get("sector")
        }
    except Exception as e:
        return {"error": str(e)}

# @tool
# def fetch_social_trends(subreddit: str = "technology") -> str:
#     """
#     Fetches the top currently trending topics/posts from a specific Reddit community 
#     (e.g., 'technology', 'artificial', 'stocks') without needing an API key.
#     """
#     try:
#         url = f"https://www.reddit.com/r/{subreddit}/top.json?limit=5&t=day"
#         headers = {'User-Agent': 'TrendAggregatorBot/1.0'}
#         response = requests.get(url, headers=headers)
#         data = response.json()
        
#         trends = []
#         for post in data['data']['children']:
#             title = post['data']['title']
#             score = post['data']['score']
#             trends.append(f"Title: {title} (Score: {score})")
            
#         return "\n".join(trends)
#     except Exception as e:
#         return f"Trend Fetching Error: {str(e)}"

@tool
def fetch_social_trends(subreddit: str = "technology") -> str:
    """
    Fetches the top currently trending posts directly from Real Reddit communities 
    (e.g., 'technology', 'artificial', 'MachineLearning').
    """
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=5"
        
        # PRO-TRICK: Masking the Python script as a Real Chrome Browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 429:
            return "Error: Reddit is strictly rate-limiting right now. Need an official Reddit Developer API key to proceed."
            
        data = response.json()
        
        trends = []
        for post in data['data']['children']:
            title = post['data']['title']
            score = post['data']['score']
            post_url = post['data']['url']
            trends.append(f"📌 {title}\n   Upvotes: {score} | Link: {post_url}")
            
        return "\n\n".join(trends)
    except Exception as e:
        return f"Reddit Fetching Error: {str(e)}"



@tool
def fetch_youtube_trends(search_query: str = "Artificial Intelligence") -> str:
    """
    Fetches the top trending YouTube videos based on a specific topic.
    Requires YOUTUBE_API_KEY in .env file.
    """
    try:
        # Puts your YouTube API key here or in .env
        YT_API_KEY = os.environ.get("YOUTUBE_API_KEY") 
        if not YT_API_KEY:
            return "Error: YouTube API key missing."
            
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={search_query}&type=video&order=viewCount&key={YT_API_KEY}"
        
        response = requests.get(url)
        data = response.json()
        
        trends = []
        for item in data.get('items', []):
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            video_id = item['id']['videoId']
            trends.append(f"🎥 {title}\n   Channel: {channel} | Link: https://youtube.com/watch?v={video_id}")
            
        return "\n\n".join(trends)
    except Exception as e:
        return f"YouTube Fetching Error: {str(e)}"

# @tool
# def query_personal_mongodb(collection_name: str, query_filter_json: str) -> str:
#     """
#     Queries your personal MongoDB database. 
#     Args:
#         collection_name (str): The name of the collection.
#         query_filter_json (str): A strict JSON string representing the MongoDB find() filter (e.g. '{"status": "active"}').
#     """
#     try:
#         # NOTE: Apni MongoDB URI yahan replace karna (local ya Atlas)
#         MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/") 
#         client = MongoClient(MONGO_URI)
#         db = client["my_personal_db"] # Apna Database name yahan daalo
#         collection = db[collection_name]
        
#         query_dict = json.loads(query_filter_json)
        
#         # Fetch top 5 documents to prevent overwhelming the LLM
#         results = list(collection.find(query_dict, {"_id": 0}).limit(5))
#         client.close()
        
#         if not results:
#             return "No documents matched the query."
#         return json.dumps(results, indent=2)
#     except Exception as e:
#         return f"MongoDB Error: {str(e)}"

@tool
def query_personal_mongodb(collection_name: str, query_filter_json: str) -> str:
    """
    Queries your personal MongoDB database. 
    Args:
        collection_name (str): The name of the collection.
        query_filter_json (str): A strict JSON string representing the MongoDB find() filter.
    """
    try:
        # Puling the exact URI you set in the .env file
        MONGO_URI = os.environ.get("MONGODB_URI") 
        if not MONGO_URI:
            return "Error: MONGODB_URI not found in environment variables."
            
        client = MongoClient(MONGO_URI)
        
        # Taking the DB name directly from your URI string ("tool-agenticAi-db")
        db = client.get_database("tool-agenticAi-db")
        collection = db[collection_name]
        
        query_dict = json.loads(query_filter_json)
        results = list(collection.find(query_dict, {"_id": 0}).limit(5))
        client.close()
        
        if not results:
            return "No documents matched the query."
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"MongoDB Error: {str(e)}"

@tool
def list_mongodb_collections() -> str:
    """
    Fetches and returns the names of all collections present in the connected MongoDB database.
    Use this when the user asks what collections are available.
    """
    try:
        MONGO_URI = os.environ.get("MONGODB_URI") 
        if not MONGO_URI:
            return "Error: MONGODB_URI not found in environment variables."
            
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        db = client.get_database("tool-agenticAi-db") # Tumhara DB name
        
        collections = db.list_collection_names()
        client.close()
        
        if not collections:
            return "No collections found in the database."
        return f"Collections available: {', '.join(collections)}"
    except Exception as e:
        return f"MongoDB Error: {str(e)}"

@tool
def insert_mongodb_document(collection_name: str, document_json: str) -> str:
    """
    Inserts a new document (data) into a specific MongoDB collection.
    Args:
        collection_name (str): The name of the collection.
        document_json (str): A strict JSON string representing the data to be inserted.
    """
    try:
        MONGO_URI = os.environ.get("MONGODB_URI") 
        if not MONGO_URI:
            return "Error: MONGODB_URI not found in environment variables."
            
        from pymongo import MongoClient
        import json
        
        client = MongoClient(MONGO_URI)
        db = client.get_database("tool-agenticAi-db") # Ensure no trailing slash
        collection = db[collection_name]
        
        # JSON string ko Python dictionary me convert karna
        document_dict = json.loads(document_json)
        
        # Database me insert karna
        result = collection.insert_one(document_dict)
        client.close()
        
        return f"Success: Document successfully inserted with ID {str(result.inserted_id)}"
    except Exception as e:
        return f"MongoDB Insert Error: {str(e)}"

# Update tool list
tools = [
    scrape_website_text, 
    save_report_to_file, 
    fetch_market_data, 
    fetch_social_trends, 
    fetch_youtube_trends,
    query_personal_mongodb,
    list_mongodb_collections,
    insert_mongodb_document
]
llm_with_tools = llm.bind_tools(tools)

# -------------------
# 3. State & Graph Architecture
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

# -------------------
# 4. Checkpointer (Memory)
# -------------------
conn = sqlite3.connect(database="chatbot_test.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

# -------------------
# 5. Graph Compilation
# -------------------
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 6. TERMINAL TESTING LOOP
# -------------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 Agent Terminal Testing Mode Started!")
    print("Type 'exit' or 'quit' to stop the chat.")
    print("="*50 + "\n")
    
    config = {
        "configurable": {"thread_id": "test_session_2"}, 
        "recursion_limit": 5
    }
    
    while True:
        user_input = input("\n🧑 You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Stopping the agent...")
            break
        if not user_input.strip():
            continue
            
        print("🤖 Agent is thinking... (Calling tools if needed)\n")
        
        events = chatbot.stream(
            {"messages": [("user", user_input)]}, 
            config, 
            stream_mode="values"
        )
        
        for event in events:
            # Print only the latest message from the agent
            latest_msg = event["messages"][-1]
            if latest_msg.type == "ai" and latest_msg.content:
                print(f"🤖 Agent: {latest_msg.content}")
            elif latest_msg.type == "ai" and latest_msg.tool_calls:
                print(f"🛠️  Agent decided to use tools: {[t['name'] for t in latest_msg.tool_calls]}")