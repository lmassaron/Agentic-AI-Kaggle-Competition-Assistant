# Agentic AI Kaggle Competition Assistant

A multi-tool agent that leverages the Meta Kaggle datasets to accelerate competition research, strategy, and code discovery.

This project is an agentic AI assistant designed to help users with Kaggle competitions. It leverages Google's Gemini models and the Kaggle API to provide insights, find similar competitions, retrieve winning solutions, and analyze code from past competitions.

The assistant can be run both as a command-line application and within a Kaggle Notebook environment.

## Features

![Kaggle Competition Assistant Demo](sample_image.png)

- **Competition Discovery**: Find similar past competitions based on keywords and metrics.
- **Solution Mining**: Retrieve winning solution write-ups and high-scoring notebooks.
- **Code Analysis**: Search for specific code snippets and analyze the technology stacks of top solutions.
- **Interactive Chat**: An interactive command-line interface to chat with the agent.
- **Kaggle Notebook Integration**: A Jupyter notebook to run the agent in a Kaggle environment.

## Key Concepts Demonstrated

This project applies several key concepts from modern agentic AI development:

1.  **Custom Tools**: The agent is equipped with a suite of custom tools that are directly relevant to the Kaggle domain. These tools (`find_similar_competitions`, `get_winning_solution_writeups`, `analyze_tech_stack`, etc.) are defined in `src/tools.py` and connected to the agent in `src/agent.py`. They enable the agent to perform specific, high-value actions by querying the Meta Kaggle datasets via the Kaggle API.

2.  **Sessions & Memory**: The agent manages the conversation state within a session. The `ConversationMemory` class in `src/agent.py` stores the history of user and assistant messages. This context is used to inform the agent's responses. The implementation includes features for session management, such as resetting the conversation history (`!reset`) and viewing the current session's message log (`!history`).

3.  **Observability**: To provide insight into the agent's internal operations, a simple but effective logging system is implemented. The `AgentLogger` class in `src/agent.py` records key events, such as when a query is received, a tool is called, or an error occurs. These logs can be inspected (`!logs`) to debug or monitor the agent's behavior. The `!stats` command provides a consolidated view of agent, memory, and logger metrics.

## Project Structure

```
.
├── src/                   # Source code
│   ├── __init__.py
│   ├── agent.py           # Core agent logic
│   ├── tools.py           # Tool function implementations
│   ├── built_in_tools.py  # Generic tools (web fetch, search)
│   └── kaggle_api.py      # Functions for interacting with Kaggle data
├── .gitignore
├── kaggle_assistant.ipynb # Jupyter Notebook for Kaggle
├── main.py                # Command-line interface
├── README.md
├── WRITEUP.md
└── requirements.txt       # Project dependencies
```

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd kaggle-competition-assistant
```

### 2. Create a Virtual Environment

It is recommended to use a virtual environment to manage the project's dependencies.

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API Keys

**For Local Development:**

1.  **Google API Key**: Create a `.env` file in the root of the project and add your Google API key:
    ```
    GOOGLE_API_KEY="your_google_api_key"
    ```
2.  **Kaggle API Key**: Ensure you have a `kaggle.json` file in your `~/.kaggle/` directory. You can download this from your Kaggle account settings.

**For Kaggle Notebooks:**

Use the "Secrets" feature in the Kaggle editor to add your `GOOGLE_API_KEY`. The `kaggle.json` credentials are automatically handled if you are logged in, or you can use `UserSecretsClient` as demonstrated in the notebook.

## How to Run

### Command-Line Interface

To run the agent from your terminal, execute the `main.py` script:

```bash
python main.py
```

This will start an interactive chat session with the Kaggle Competition Assistant.

### Kaggle Notebook

1.  Upload the `kaggle_assistant.ipynb` notebook to a new Kaggle Notebook.
2.  Upload the `src` directory as a utility script or dataset to the notebook.
3.  Add your `GOOGLE_API_KEY` as a secret.
4.  Run the cells in the notebook.

The notebook will guide you through the process of initializing and interacting with the agent.