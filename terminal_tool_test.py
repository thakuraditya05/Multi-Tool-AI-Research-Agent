import os
import sqlite3
import requests
import json
from bs4 import BeautifulSoup
import yfinance as yf
from pymongo import MongoClient
from dotenv import load_dotenv

import praw
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



@tool
def fetch_social_trends(subreddit_name: str = "technology") -> str:
    """
    Fetches the top currently trending posts directly from Real Reddit using the official PRAW API.
    Args:
        subreddit_name (str): The name of the subreddit (e.g., 'artificial', 'MachineLearning').
    """
    try:
        REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
        REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
        
        if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
            return "Error: Reddit API credentials (REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET) missing in .env file."

        # Authenticating with Reddit officially
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent="AgenticAI_Bot/1.0 (by /u/your_reddit_username)" # Standard practice to include a user agent
        )
        
        subreddit = reddit.subreddit(subreddit_name)
        
        trends = []
        # Fetching the top 5 'hot' posts
        for post in subreddit.hot(limit=5):
            # Skipping pinned/sticky posts
            if not post.stickied:
                trends.append(f"📌 {post.title}\n   Upvotes: {post.score} | Link: https://reddit.com{post.permalink}")
            
        if not trends:
            return f"No trending posts found in r/{subreddit_name}."
            
        return "\n\n".join(trends)
    except Exception as e:
        return f"Official Reddit API Error: {str(e)}"

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
def query_dynamic_mongodb(database_name: str, collection_name: str, query_filter_json: str) -> str:
    """
    Queries documents from any specific database and collection in the cluster.
    Args:
        database_name (str): The name of the database.
        collection_name (str): The name of the collection.
        query_filter_json (str): A strict JSON string representing the MongoDB find() filter.
    """
    try:
        MONGO_URI = os.environ.get("MONGODB_URI") 
        if not MONGO_URI: return "Error: MONGODB_URI not found."
            
        import json
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        
        db = client.get_database(database_name)
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


@tool
def list_mongodb_databases() -> str:
    """
    Fetches and returns the names of all databases present in the MongoDB cluster.
    Use this when the user asks what databases are available.
    """
    try:
        MONGO_URI = os.environ.get("MONGODB_URI") 
        if not MONGO_URI:
            return "Error: MONGODB_URI not found in environment variables."
            
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        
        # Lists all databases in the cluster
        databases = client.list_database_names()
        client.close()
        
        if not databases:
            return "No databases found in the cluster."
        return f"Databases available: {', '.join(databases)}"
    except Exception as e:
        return f"MongoDB Error: {str(e)}"

@tool
def list_mongodb_collections(database_name: str) -> str:
    """
    Fetches and returns the names of all collections present in a specific MongoDB database.
    Args:
        database_name (str): The exact name of the database to check.
    """
    try:
        MONGO_URI = os.environ.get("MONGODB_URI") 
        if not MONGO_URI:
            return "Error: MONGODB_URI not found in environment variables."
            
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        
        # Dynamically connects to the requested database
        db = client.get_database(database_name) 
        collections = db.list_collection_names()
        client.close()
        
        if not collections:
            return f"No collections found in the '{database_name}' database."
        return f"Collections in '{database_name}': {', '.join(collections)}"
    except Exception as e:
        return f"MongoDB Error: {str(e)}"


@tool
def insert_dynamic_mongodb(database_name: str, collection_name: str, document_json: str) -> str:
    """
    Inserts a new document (data) into any specific database and collection.
    Args:
        database_name (str): The name of the database.
        collection_name (str): The name of the collection.
        document_json (str): A strict JSON string representing the data to be inserted.
    """
    try:
        MONGO_URI = os.environ.get("MONGODB_URI") 
        if not MONGO_URI: return "Error: MONGODB_URI not found."
            
        import json
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI)
        
        db = client.get_database(database_name)
        collection = db[collection_name]
        
        document_dict = json.loads(document_json)
        result = collection.insert_one(document_dict)
        client.close()
        
        return f"Success: Document successfully inserted into '{database_name}.{collection_name}' with ID {str(result.inserted_id)}"
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
    insert_mongodb_document,
    list_mongodb_databases,
    query_dynamic_mongodb,
    insert_dynamic_mongodb,
    
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
        "configurable": {"thread_id": "test_session_5"}, 
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