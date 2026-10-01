# 🚀 Multi-Tool AI Research Agent

An autonomous, multi-modal **AI Research Agent** built with **LangGraph, LangChain, Google Gemini, and Streamlit**.

The agent intelligently orchestrates multiple tools to perform **real-time web research, stock market analysis, Reddit and YouTube trend analysis, web scraping, MongoDB operations, and automated research report generation**.

It uses a stateful LangGraph architecture with **SQLite checkpointing** for persistent conversation state, while Streamlit provides a real-time interface with transparent tool execution and downloadable research reports.

---

## 📌 Overview

The **Multi-Tool AI Research Agent** is designed to go beyond a traditional chatbot.

Instead of relying only on the knowledge stored inside an LLM, the agent can dynamically decide which external tools are required to answer a user's query.

For example:

> **"Research the latest AI agent trends, check Reddit discussions, compare them with YouTube trends, and create a research report."**

The agent can:

1. Search the web using Tavily.
2. Scrape relevant web pages.
3. Analyze Reddit discussions.
4. Search YouTube for trending content.
5. Process and synthesize the collected information using Gemini.
6. Generate a structured Markdown research report.
7. Provide the generated report as a downloadable file through Streamlit.

---

## ✨ Key Features

### 🤖 Stateful AI Agent

Built using **LangGraph** to create a stateful agent capable of:

* Tool selection
* Multi-step reasoning
* Conditional tool execution
* State management
* Persistent checkpoints
* Multi-turn conversations

SQLite is used as the LangGraph checkpointer to preserve agent state across interactions.

---

### 🛠️ Multi-Tool Orchestration

The agent can dynamically select and execute different tools depending on the user's request.

Supported tools include:

* 🌐 Web Scraper
* 🔎 Tavily Web Search
* 📈 Stock Market Data
* 🟠 Reddit Trends
* ▶️ YouTube Trends
* 🍃 MongoDB Operations
* 📝 Research Report Generator

---

### 🔎 Real-Time Web Research

The agent can access current information using **Tavily Search** instead of relying solely on the LLM's static knowledge.

Example:

```text
Search the web for the latest developments in LangGraph AI agents
and summarize the important updates.
```

---

### 📈 Financial Market Analysis

Using **yfinance**, the agent can retrieve market information such as:

* Current stock price
* Market capitalization
* P/E ratio
* Other available market statistics

Example:

```text
Get the latest market data for Apple (AAPL)
and generate a short investment research report.
```

> Financial information retrieved by the application is for research purposes and should not be treated as financial advice.

---

### 🟠 Reddit Trend Analysis

Using the **Reddit API through PRAW**, the agent can retrieve posts from specific subreddits.

Example:

```text
Find the top 5 trending posts from the MachineLearning subreddit.
```

The agent can then summarize and analyze the retrieved discussions.

---

### ▶️ YouTube Trend Analysis

Using **YouTube Data API v3**, the agent can search for videos based on user-provided topics.

Example:

```text
Find the most viewed recent videos about AI Agents
and summarize the major topics being discussed.
```

---

### 🍃 Dynamic MongoDB Operations

The agent can interact dynamically with MongoDB databases and collections.

Supported operations include:

* List databases
* List collections
* Insert documents
* Query documents
* Execute JSON-based queries
* Retrieve stored information

Example:

```text
List all databases available in my MongoDB cluster
and show the collections inside Growthify_db.
```

The database and collection can be selected dynamically based on the user's natural-language request.

---

### 📝 Automated Research Reports

The agent can transform collected information into structured Markdown reports.

For example:

```text
Research the latest AI agent market trends
and generate a detailed Markdown report.
```

The generated `.md` file can then be downloaded directly through the Streamlit interface.

---

### ⚡ Real-Time Streamlit UI

The Streamlit frontend provides visibility into the agent's execution process.

The interface can display:

* User queries
* Agent responses
* Tool execution
* Tool outputs
* Generated reports
* Downloadable files

This makes the agent's workflow easier to inspect and debug.

---

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

---

## 🔄 Agent Workflow

A typical request follows this workflow:

```text
User Query
    ↓
Streamlit Frontend
    ↓
LangGraph Agent
    ↓
Gemini analyzes the request
    ↓
Select required tool(s)
    ↓
Execute tool
    ↓
Return tool result
    ↓
Agent evaluates result
    ↓
Call additional tools if required
    ↓
Synthesize information
    ↓
Generate final response
    ↓
Optionally generate Markdown report
    ↓
Download through Streamlit
```

The agent can perform multiple tool calls when a query requires information from different sources.

---

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

---

## 🧰 Tech Stack

### AI / Agent

* **Google Gemini**
* **LangChain**
* **LangGraph**
* LangChain Google GenAI integration

### Frontend

* **Streamlit**

### Database & Storage

* **MongoDB**
* **PyMongo**
* **SQLite**

### APIs & Data Sources

* **Tavily**
* **yfinance**
* **PRAW / Reddit API**
* **YouTube Data API v3**

### Web Scraping

* **BeautifulSoup4**

### Programming Language

* **Python 3.8+**

---

## 📸 Screenshots

### 🔧 Tool Execution

Add your screenshot to the repository and update the path below:

```markdown
![Agent UI - Tool Execution](./screenshots/tool-execution.png)
```

Example:

![Agent UI - Tool Execution](./screenshots/tool-execution.png)

*Transparent tool execution showing the agent's selected tools and their outputs.*

---

### 📄 Research Report Generation

```markdown
![Agent UI - File Download](./screenshots/file-download.png)
```

Example:

![Agent UI - File Download](./screenshots/file-download.png)

*Generating a research report and providing it as a downloadable Markdown file.*

---

## 📂 Project Structure

A recommended project structure:

```text
Multi-Tool-AI-Research-Agent/
│
├── screenshots/
│   ├── tool-execution.png
│   └── file-download.png
│
├── tools/
│   ├── web_scraper.py
│   ├── tavily_search.py
│   ├── market_data.py
│   ├── reddit_tools.py
│   ├── youtube_tools.py
│   ├── mongodb_tools.py
│   └── report_generator.py
│
├── agent/
│   ├── graph.py
│   ├── state.py
│   └── prompts.py
│
├── streamlit_frontend_tool.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

> Adjust the structure above according to your actual repository files.

---

# 🚀 Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Multi-Tool-AI-Research-Agent.git
cd Multi-Tool-AI-Research-Agent
```

Replace `yourusername` with your GitHub username.

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't already have a `requirements.txt`, install the major dependencies with:

```bash
pip install streamlit
pip install langchain
pip install langgraph
pip install langchain-google-genai
pip install tavily-python
pip install yfinance
pip install praw
pip install pymongo
pip install beautifulsoup4
python-dotenv
```

---

# 🔐 Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY_TOOL=your_google_gemini_api_key

TAVILY_API_KEY=your_tavily_api_key

REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

YOUTUBE_API_KEY=your_youtube_api_key

MONGODB_URI=your_mongodb_cluster_connection_string
```

### Environment Variable Description

| Variable               | Description                      |
| ---------------------- | -------------------------------- |
| `GEMINI_API_KEY_TOOL`  | Google Gemini API key            |
| `TAVILY_API_KEY`       | Tavily web search API key        |
| `REDDIT_CLIENT_ID`     | Reddit application client ID     |
| `REDDIT_CLIENT_SECRET` | Reddit application client secret |
| `YOUTUBE_API_KEY`      | YouTube Data API key             |
| `MONGODB_URI`          | MongoDB connection string        |

### ⚠️ Important

Never commit your `.env` file to GitHub.

Add the following to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
```

---

# ▶️ Running the Application

Start the Streamlit application:

```bash
streamlit run streamlit_frontend_tool.py
```

Streamlit will provide a local URL, usually:

```text
http://localhost:8501
```

Open the URL in your browser to start using the agent.

---

# 🧪 Example Prompts

## 🔎 Web Research

```text
Search the web using Tavily for the latest news
on LangGraph AI agents from this month and
give me a quick summary.
```

---

## 📈 Finance & Report Generation

```text
Fetch the current stock market data for Apple (AAPL).
Generate a neat executive summary and save the report
to apple_stock.md.
```

---

## 🟠 Reddit Analysis

```text
What are the top 5 trending posts on the
MachineLearning subreddit right now?
```

---

## ▶️ YouTube Research

```text
Search YouTube for the most viewed recent videos
about AI agents and summarize the major topics.
```

---

## 🍃 MongoDB

```text
List all the databases currently available on my
MongoDB cluster, and then list the collections
in the Growthify_db database.
```

---

## 🌐 Web Scraping

```text
Scrape this webpage and summarize the important
information from it.
```

---

## 🔬 Multi-Tool Research

The agent can also combine multiple tools:

```text
Research the latest developments in AI agents.
Check recent web articles, Reddit discussions,
and YouTube videos. Compare the major trends
and generate a Markdown research report.
```

This demonstrates the core capability of the project: **using multiple tools within a single research workflow.**

---

# 💾 Memory & State Management

The application uses **SQLite checkpointing through LangGraph** to maintain agent state.

This allows the agent to preserve relevant state across interactions rather than treating every request as completely independent.

Conceptually:

```text
User
 │
 ▼
LangGraph
 │
 ├── Agent State
 │
 ├── Tool Results
 │
 └── Conversation State
         │
         ▼
      SQLite
```

MongoDB serves a different purpose: it is used as an external application database that the agent can query and modify through its MongoDB tools.

---

# 📄 Report Generation

The report generation workflow allows the agent to convert research findings into a structured Markdown document.

Example:

```text
User Request
     ↓
Research
     ↓
Tool Results
     ↓
Gemini Synthesis
     ↓
Formatted Markdown
     ↓
Temporary File
     ↓
Streamlit Download Button
```

Generated reports can contain sections such as:

```markdown
# Research Report

## Executive Summary

## Key Findings

## Market / Industry Trends

## Important Sources

## Analysis

## Conclusion
```

---

# 🔒 Security Considerations

Because the application interacts with external APIs and databases, security should be considered carefully.

### API Keys

Store credentials inside environment variables:

```env
GEMINI_API_KEY_TOOL=...
TAVILY_API_KEY=...
```

Never hard-code API keys inside Python files.

### MongoDB

Use a MongoDB user with only the permissions required by the application.

Avoid exposing unrestricted database credentials.

### Git

Make sure `.env` is included in `.gitignore`:

```gitignore
.env
```

If an API key is accidentally committed to GitHub, revoke and regenerate it immediately.

---

# ⚡ Why LangGraph?

Traditional chatbot workflows generally follow:

```text
User → LLM → Response
```

This project follows a more flexible architecture:

```text
User
  ↓
LLM
  ↓
Tool Selection
  ↓
Tool Execution
  ↓
Observation
  ↓
Additional Tool Calls
  ↓
LLM Synthesis
  ↓
Final Response
```

LangGraph makes it possible to represent this workflow as a stateful graph with nodes, edges, conditional routing, and checkpoints.

---

# 🧠 Why a Multi-Tool Agent?

Different information sources are useful for different research tasks.

| Requirement                 | Tool        |
| --------------------------- | ----------- |
| Latest news                 | Tavily      |
| Specific webpage content    | Web Scraper |
| Stock information           | yfinance    |
| Community discussions       | Reddit      |
| Video trends                | YouTube     |
| Persistent application data | MongoDB     |
| Final synthesis             | Gemini      |

Instead of forcing one model to answer every question from its internal knowledge, the agent can **select the appropriate external source and combine the results.**

---

# 🚧 Future Improvements

Potential improvements include:

* [ ] Streaming token-by-token responses
* [ ] More financial data providers
* [ ] Additional social media integrations
* [ ] PDF report generation
* [ ] DOCX report generation
* [ ] Citation and source tracking
* [ ] Advanced MongoDB aggregation support
* [ ] Authentication and user accounts
* [ ] Cloud deployment
* [ ] Docker support
* [ ] Background research jobs
* [ ] Research history dashboard
* [ ] Vector database integration
* [ ] RAG-based document research
* [ ] Agent performance monitoring
* [ ] Tool usage analytics

---

# 🐳 Docker Deployment

Docker support can be added to make the application easier to deploy consistently.

A future deployment architecture could look like:

```text
                    ┌───────────────┐
                    │    User       │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Streamlit   │
                    │   Container   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  LangGraph    │
                    │     Agent     │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          APIs           MongoDB        SQLite
```

---

# 🤝 Contributing

Contributions, issues, and feature requests are welcome!

### 1. Fork the repository

```bash
git fork
```

### 2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

### 3. Commit your changes

```bash
git add .
git commit -m "Add new feature"
```

### 4. Push the branch

```bash
git push origin feature/new-feature
```

### 5. Open a Pull Request

Please provide a clear description of the changes and explain how they were tested.

---

# 🐛 Issues & Feature Requests

If you encounter a bug or have an idea for improving the project, open an issue in the GitHub repository.

When reporting a bug, include:

* Operating system
* Python version
* Error message
* Steps to reproduce
* Relevant logs

---

# 📜 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute the project according to the terms of the license.

---

# ⭐ Support

If you find this project useful:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report bugs
* 💡 Suggest new features
* 🤝 Contribute improvements

---

## 👨‍💻 Author

**Aditya Singh**

Electronics & Communication Engineering
MANIT Bhopal

### Connect

* GitHub: `@thakuraditya05`
* LinkedIn: `@thakuraditya05`

---

## 🚀 Project Highlights

> **A production-oriented multi-tool AI research agent combining LLM reasoning, real-time data retrieval, database operations, social media analysis, web scraping, persistent state, and automated report generation into a single Streamlit application.**

---

### ⭐ Built with

```text
Python
   +
Google Gemini
   +
LangChain
   +
LangGraph
   +
Streamlit
   +
Tavily
   +
yfinance
   +
PRAW
   +
YouTube Data API
   +
MongoDB
   +
SQLite
```

**Built to research. Built to orchestrate. Built to automate. 🚀**
