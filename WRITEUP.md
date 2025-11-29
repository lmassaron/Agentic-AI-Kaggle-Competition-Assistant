# Agentic AI Kaggle Competition Assistant

## Subtitle
A multi-tool agent that leverages the Meta Kaggle datasets to accelerate competition research, strategy, and code discovery.

## Card and Thumbnail Image
*Suggestion: A graphic combining a brain or robot icon with the Kaggle logo, symbolizing an AI assistant for the platform.*

## Submission Track
Enterprise Agents

## Media Gallery
*Replace with your YouTube video URL*
`https://www.youtube.com/watch?v=your-video-id`

## Project Description

### The Problem: The Kaggle "Cold Start" Challenge

Kaggle competitions are a cornerstone of the data science community, but starting a new competition is often a daunting and time-consuming task. Before writing a single line of code, competitors spend hours, if not days, on preliminary research, asking questions like:
- Has a similar problem been solved before on Kaggle?
- What were the winning strategies in those competitions?
- What machine learning models and libraries are most effective for this type of problem?
- Where can I find boilerplate code for data processing, feature engineering, or model training?

This research typically involves manually searching through past competitions, discussion forums, and public notebooks, which is an inefficient and repetitive process.

### Our Solution: An Agentic AI Assistant

To address this "cold start" problem, we have developed an **Agentic AI Kaggle Competition Assistant**. This project is a multi-tool agent powered by a Large Language Model (LLM) designed to automate the research and discovery phase of a Kaggle competition.

The agent is designed to be run in two primary environments:
1.  **Locally via a Command-Line Interface (CLI)** for quick, interactive sessions.
2.  **Within a Kaggle Notebook**, providing direct access to the competition environment and datasets.

By leveraging the vast historical data in the **Meta Kaggle** and **Meta Kaggle Code** datasets, our agent provides users with actionable insights, code snippets, and strategic guidance, significantly accelerating their workflow.

### System Architecture

The agent is built on a modular Python architecture, consisting of three main components:

1.  **Core Agent (`src/agent.py`):** This is the brain of the operation. The `KaggleAgent` class manages the conversation, processes user queries, and orchestrates the use of custom tools. It also handles session management and observability.

2.  **Custom Tools (`src/tools.py`):** A suite of domain-specific functions that act as the agent's "hands." These tools are designed to perform specific tasks by querying the Meta Kaggle datasets. They bridge the gap between a user's high-level question and the structured data available.

3.  **Data Abstraction Layer (`src/kaggle_api.py`):** This module is responsible for all direct interactions with the Meta Kaggle datasets. It loads the data into pandas DataFrames and provides specific query functions that the tools can use, separating the agent's logic from the data retrieval process.

### Key Concepts Demonstrated

This project explicitly applies several key concepts from modern agentic AI development:

1.  **Custom Tools**: The agent's primary strength lies in its specialized, custom-built tools. Instead of relying on generic search, we have created five functions directly relevant to the Kaggle workflow. These tools, defined in `src/tools.py`, include:
    -   `find_similar_competitions`: Scans for past competitions based on keywords and evaluation metrics.
    -   `get_winning_solution_writeups`: Mines discussion forums for high-scoring solution write-ups.
    -   `get_top_scoring_kernels`: Identifies the most popular and successful public notebooks.
    -   `search_code_snippets`: Performs targeted searches within the source code of notebooks to find specific implementations (e.g., `StratifiedKFold`).
    -   `analyze_tech_stack`: Aggregates and reports the most commonly used libraries for a competition, revealing the dominant modeling choices.
    -   `get_competition_id_from_url`: Parses a Kaggle competition URL to extract the competition slug and retrieve its unique `CompetitionId` from the Meta Kaggle dataset.
    -   `analyze_competition_by_url`: Utilizes `web_fetch` (a built-in tool) to scrape the content of a Kaggle competition page and then orchestrates multiple other custom tools (`get_competition_id_from_url`, `get_winning_solution_writeups`, `get_top_scoring_kernels`, `analyze_tech_stack`) to provide a comprehensive summary of the competition, its top discussion topics, and top code solutions.

2.  **Sessions & Memory**:  The agent is session-aware, maintaining the state of the conversation. The `ConversationMemory` class in `src/agent.py` stores the history of user and assistant messages, and this context is used to inform the agent's subsequent responses. This implementation also includes features for explicit state management:
    -   **Session History:** The user can inspect the full conversation history at any time (e.g., via the `!history` command in the CLI).
    -   **State Reset:** The user can clear the agent's memory to start a new, clean session (`!reset` command), demonstrating direct control over the agent's state.

3.  **Observability**: To provide transparency into the agent's internal operations, we have implemented a logging and metrics system.
    -   **Logging:** The `AgentLogger` class in `src/agent.py` records key events, such as when a query is received, which tool is called, what arguments are used, and if any errors occur. This is crucial for debugging and understanding the agent's decision-making process. Logs can be exported via the `!logs` command.
    -   **Metrics:** The agent tracks key performance indicators (KPIs) for a session, including the number of queries processed, tools called, and errors encountered. These consolidated metrics, combined with memory and logger stats, are accessible via the `!stats` command, offering a complete snapshot of the agent's health and usage.

### Example Usage Scenario

User: "Analyze the competition Hull Tactical - Market Prediction at https://www.kaggle.com/competitions/hull-tactical-market-prediction"

Agent Action (Orchestration):
1.  Calls `get_competition_id_from_url` with the provided URL to extract the competition slug and find its ID.
2.  Calls `analyze_competition_by_url` (which internally uses `web_fetch`) to get a summary of the competition rules and description.
3.  Calls `get_winning_solution_writeups` with the obtained competition ID to find top discussion topics.
4.  Calls `get_top_scoring_kernels` with the competition ID to identify top code solutions.
5.  Calls `analyze_tech_stack` with the competition ID to understand prevalent technologies.

Agent Response: "For the 'Hull Tactical - Market Prediction' competition, here's a summary: [Summarized Description]. The top discussion topics include: [List of topics and URLs]. Top code solutions feature: [List of kernels and authors]. The common tech stack observed is: [Tech stack distribution]. Would you like me to dive deeper into any specific aspect?"

### Conclusion and Future Work

This project successfully demonstrates how an agentic AI, equipped with custom tools and state management, can serve as a powerful assistant in a specialized domain like Kaggle competitions. By automating research, it allows data scientists to focus more on modeling and innovation.

Future enhancements could include:
-   **Implementing a Multi-Agent System:** Introducing specialized agents for tasks like code generation or data cleaning.
-   **Long-Term Memory:** Adding a vector database to retain insights from past conversations.
-   **Proactive Analysis:** Enabling the agent to automatically analyze a new competition and provide a preliminary report without being prompted.

## Attachments

*   **GitHub Repository:** `https://github.com/your-username/kaggle-competition-assistant` (Replace with your public GitHub repo link)
*   **Kaggle Notebook:** The `kaggle_assistant.ipynb` file included in the repository is designed to be uploaded and run directly on Kaggle.
