# Agentic AI Kaggle Competition Assistant

## Subtitle
A specialized AI agent that orchestrates custom tools to automate Kaggle competition research, accelerating the "cold start" phase for data scientists.

## Card and Thumbnail Image

![Kaggle Competition Assistant Demo](sample_image.png)

## Submission Track
Concierge Agents

## Media Gallery
*TODO*

## Project Description

### The Problem: The "Cold Start" in Data Science Competitions

Every Kaggle competition begins with a blank notebook and a daunting question: *"Where do I start?"*

Before a single model is trained, data scientists spend hours—often days—performing manual reconnaissance. They scour past competitions for similar problems, hunt for "winning solutions" buried in years-old discussion threads, and try to identify the state-of-the-art libraries for the specific task at hand. This process is manual, repetitive, and inefficient. Valuable insights are often missed simply because they are buried in the vast ocean of Kaggle's historical data.

### Our Solution: The Agentic Kaggle Assistant

We have built an **Agentic AI Assistant** specifically designed to solve this "cold start" problem. Unlike a generic chatbot that hallucinates answers, our agent is a **tool-using system** grounded in real-time data. It acts as a research partner that can autonomously explore the Kaggle platform to provide evidence-based strategies.

The agent is powered by **Google's Gemini 2.5 Flash** model and orchestrated via a custom Python framework. It connects directly to the **Kaggle API** to query live competition data, ensuring its advice is always up-to-date.

### Key Features & Capabilities

Our agent goes beyond simple Q&A. It performs complex workflows by chaining together specialized tools:

1.  **Smart Competition Discovery**: Instead of just keyword matching, the agent finds competitions that are *strategically* similar (e.g., "Find me other image segmentation challenges that used the Dice coefficient").
2.  **Automated Solution Mining**: It hunts down "winning solution" write-ups from discussion forums, filtering for high-scoring posts to extract gold-standard approaches.
3.  **Tech Stack Analysis**: By analyzing the import statements of top-scoring kernels (even inside Jupyter Notebooks!), the agent empirically determines the best libraries for the job (e.g., "Use `polars` and `lightgbm` for this dataset").
4.  **Code Snippet Search**: It performs semantic searches *inside* the source code of top notebooks to find implementation details for specific techniques (e.g., "Show me how `StratifiedKFold` was implemented in the Titanic competition").
5.  **Comprehensive Summarization**: Given a competition URL, the agent can autonomously scrape the page, identify key details, and then recursively call its own tools to generate a full "briefing document" covering rules, data, and top strategies.

### System Architecture

The project follows a modular, production-ready architecture:

*   **`src/agent.py` (The Brain)**: Implements the **ReAct (Reasoning + Acting)** loop. It manages the conversation history (`ConversationMemory`), decides which tool to call based on the user's intent, and synthesizes the tool outputs into a coherent response. It also features a robust `AgentLogger` for observability.
*   **`src/kaggle_api.py` (The Hands)**: A low-level interface that wraps the official Kaggle API. It handles authentication, data retrieval, and complex parsing logic (like extracting Python code from JSON-formatted `.ipynb` files).
*   **`src/tools.py` (The Skills)**: High-level functions exposed to the LLM. Each tool corresponds to a specific research capability (e.g., `find_similar_competitions`, `analyze_tech_stack`).
*   **Fallback Mechanisms**: If the Kaggle API is unreachable or a page is protected, the agent seamlessly falls back to a custom **web search tool** (powered by DuckDuckGo) to ensure the user always gets an answer.

### Key Concepts Demonstrated

This project is a practical showcase of the **Google AI Agents** curriculum concepts:

1.  **Tool Use & Function Calling**: The core of the agent is its ability to recognize when it needs external data and to call the appropriate Python function with the correct arguments.
2.  **Reasoning Loops**: The agent doesn't just execute one command. It reasons through a problem. For example, if asked to "Summarize the Titanic competition," it first identifies the competition slug, then decides to fetch winning solutions, then fetches top kernels, and finally combines everything into a summary.
3.  **State Management**: The `ConversationMemory` ensures the agent remembers context. You can ask "What about the Titanic?" and then follow up with "Show me code for that," and it understands "that" refers to the Titanic competition.
4.  **Observability**: We implemented a logging system that tracks every thought, tool call, and result, allowing developers to "debug" the agent's reasoning process.

### Impact and Future Work

This assistant transforms the Kaggle experience from a solo struggle into a supported journey. By automating the tedious research phase, it frees up data scientists to focus on what matters: feature engineering, model architecture, and creative problem-solving.

Future iterations will focus on:
*   **Code Generation**: Using the retrieved snippets to automatically generate a "starter notebook" for the user.
*   **Multi-Agent Collaboration**: Splitting the "Researcher" and "Coder" roles into separate specialized agents for deeper analysis.

## Attachments

*   **GitHub Repository**: `https://github.com/lmassaron/Agentic-AI-Kaggle-Competition-Assistant`
*   **Kaggle Notebook**: `https://www.kaggle.com/code/lucamassaron/agentic-ai-kaggle-competition-assistant/` (Also included in the repo, ready to run on Kaggle)