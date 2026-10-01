# Multi-Tool AI Research Agent 🚀

An autonomous, multi-modal AI agent built with **LangGraph** and **Streamlit**. This agent is capable of orchestrating multiple tools to fetch real-time stock market data, scrape web pages, analyze social media trends (Reddit & YouTube), dynamically query/write to MongoDB clusters, and generate downloadable research reports.

Powered by **Google Gemini 3.5 Flash-Lite** (via LangChain), this agent features persistent memory (SQLite), real-time UI streaming, and transparent tool execution visibility.

## 📸 Screenshots

*(Replace the paths below with your actual image filenames once you upload them to your repository)*

![Agent UI - Tool Execution](path/to/your/image1.png)
*Caption: Transparent tool execution showing raw JSON outputs and agent chain-of-thought.*

![Agent UI - File Download](path/to/your/image2.png)
*Caption: Generating executive summaries and providing seamless local file downloads.*

## ✨ Key Features

* **Stateful Multi-Agent Architecture:** Built using LangGraph with SQLite Checkpointing for cross-thread memory and state retention.
* **Transparent Tool Execution:** Streamlit UI automatically detects and displays which tools the agent is calling along with the raw output using expandable blocks.
* **Dynamic Database Routing:** Read and write data to *any* database or collection across your MongoDB cluster dynamically based on natural language prompts.
* **Ephemeral File Generation:** The agent can synthesize research into Markdown (`.md`) files and instantly generate download buttons in the UI for the user.
* **Real-time Web & Social Data:** Live access to web search, financial data, and social media trends bypassing static LLM knowledge cutoffs.

## 🛠️ Integrated Tools

1. **Web Scraper:** Extracts clean, stripped text content from any provided URL.
2. **Tavily Search:** Real-time web search engine for the latest news and facts.
3. **Market Data (yfinance):** Fetches real-time stock prices, market cap, and P/E ratios.
4. **Reddit Trends (PRAW):** Retrieves top trending posts from any specific subreddit via the official Reddit API.
5. **YouTube Trends:** Fetches the most viewed trending videos based on specific search queries.
6. **MongoDB Tools:** Full CRUD capabilities—list databases, list collections, insert documents, and execute complex JSON queries across the cluster.
7. **Report Generator:** Writes formatted markdown reports to temporary storage and renders a native Streamlit download button.

## ⚙️ Tech Stack

* **LLM Engine:** Google Gemini (via `langchain-google-genai`)
* **Agent Framework:** LangGraph & LangChain Core
* **Frontend UI:** Streamlit
* **Memory & Storage:** SQLite (LangGraph Checkpointer), MongoDB (PyMongo)
* **APIs & Data:** Tavily, yfinance, PRAW (Reddit), YouTube Data API v3, BeautifulSoup4



## 🏗️ System Architecture

The application follows a tool-driven agent architecture:

```text
                    ┌─────────────────────┐
                    │      User Query     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Streamlit UI      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   LangGraph Agent   │
                    │                     │
                    │  Google Gemini      │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │   Tool Selection    │
                    └──────────┬──────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       │                       │                        │
       ▼                       ▼                        ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ Tavily Search│       │ Web Scraper  │       │ yfinance     │
└──────────────┘       └──────────────┘       └──────────────┘
       │                       │                        │
       └───────────────────────┼────────────────────────┘
                               │
       ┌───────────────────────┼────────────────────────┐
       │                       │                        │
       ▼                       ▼                        ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ Reddit / PRAW│       │ YouTube API  │       │   MongoDB    │
└──────────────┘       └──────────────┘       └──────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Gemini Synthesis  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Research Report     │
                    │     Generator       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Streamlit Download  │
                    └─────────────────────┘

             SQLite → LangGraph Checkpoint / State
```
## 🛠️ Integrated Tools

| Tool                | Technology          | Purpose                                     |
| ------------------- | ------------------- | ------------------------------------------- |
| 🌐 Web Scraper      | BeautifulSoup4      | Extract clean text from web pages           |
| 🔎 Web Search       | Tavily              | Retrieve real-time web information          |
| 📈 Market Data      | yfinance            | Retrieve stock market information           |
| 🟠 Reddit           | PRAW                | Analyze subreddit trends                    |
| ▶️ YouTube          | YouTube Data API v3 | Search and analyze video trends             |
| 🍃 Database         | PyMongo             | MongoDB database operations                 |
| 📝 Report Generator | Python + Streamlit  | Generate downloadable Markdown reports      |
| 🧠 LLM              | Google Gemini       | Reasoning, synthesis and tool orchestration |
| 🔄 Agent Framework  | LangGraph           | Stateful agent workflow                     |
| 💾 Checkpointing    | SQLite              | Persistent agent state                      |


## 🚀 Installation & Setup

**1. Clone the repository:**

```bash
git clone [https://github.com/yourusername/Multi-Tool-AI-Research-Agent.git](https://github.com/yourusername/Multi-Tool-AI-Research-Agent.git)
cd Multi-Tool-AI-Research-Agent

```

**2. Create a virtual environment:**

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

```

**3. Install dependencies:**

```bash
pip install -r requirements.txt

```

**4. Environment Variables:**
Create a `.env` file in the root directory and add your API keys:

```env
GEMINI_API_KEY_TOOL=your_google_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
YOUTUBE_API_KEY=your_youtube_api_key
MONGODB_URI=your_mongodb_cluster_connection_string

```

**5. Run the Application:**

```bash
streamlit run streamlit_frontend_tool.py

```

## 🧪 Example Prompts to Try

Once the app is running, try these prompts to test the agent's multi-tool capabilities:

* **Web Research:** `"Search the web using Tavily for the latest news on 'LangGraph AI agents' from this month and give me a quick summary."`
* **Finance & Report Generation:** `"Fetch the current stock market data for Apple (AAPL). Generate a neat executive summary and save the report to apple_stock.md."`
* **Social Media Analysis:** `"What are the top 5 trending posts on the 'MachineLearning' subreddit right now?"`
* **Database Management:** `"List all the databases currently available on my MongoDB cluster, and then list the collections in the 'Growthify_db' database."`

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License

This project is licensed under the MIT License.

```
```
