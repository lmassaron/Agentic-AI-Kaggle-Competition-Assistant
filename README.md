# Agentic AI Kaggle Competition Assistant

A multi-tool agent that leverages the Meta Kaggle datasets to accelerate competition research, strategy, and code discovery.

This project is an agentic AI assistant designed to help users with Kaggle competitions. It leverages Google's Gemini models and the Meta Kaggle datasets to provide insights, find similar competitions, retrieve winning solutions, and analyze code from past competitions.

The assistant can be run both as a command-line application and within a Kaggle Notebook environment.

## Features

- **Competition Discovery**: Find similar past competitions based on keywords and metrics.
- **Solution Mining**: Retrieve winning solution write-ups and high-scoring notebooks.
- **Code Analysis**: Search for specific code snippets and analyze the technology stacks of top solutions.
- **Interactive Chat**: An interactive command-line interface to chat with the agent.
- **Kaggle Notebook Integration**: A Jupyter notebook to run the agent in a Kaggle environment.

## Key Concepts Demonstrated

This project applies several key concepts from modern agentic AI development:

1.  **Custom Tools**: The agent is equipped with a suite of five custom tools that are directly relevant to the Kaggle domain. These tools (`find_similar_competitions`, `get_winning_solution_writeups`, etc.) are defined in `src/tools.py` and connected to the agent in `src/agent.py`. They enable the agent to perform specific, high-value actions by querying the Meta Kaggle datasets.

2.  **Sessions & Memory**: The agent manages the conversation state within a session. The `ConversationMemory` class in `src/agent.py` stores the history of user and assistant messages. This context is used to inform the agent's responses. The implementation includes features for session management, such as resetting the conversation history (`!reset`) and viewing the current session's message log (`!history`).

3.  **Observability**: To provide insight into the agent's internal operations, a simple but effective logging system is implemented. The `AgentLogger` class in `src/agent.py` records key events, such as when a query is received, a tool is called, or an error occurs. These logs can be inspected (`!logs`) to debug or monitor the agent's behavior. The `!stats` command provides a consolidated view of agent, memory, and logger metrics.

## Project Structure

```
.
├── data/                  # Directory for Meta Kaggle datasets
├── src/                   # Source code
│   ├── __init__.py
│   ├── agent.py           # Core agent logic
│   ├── tools.py           # Tool function implementations
│   └── kaggle_api.py      # Functions for interacting with Kaggle data
├── .gitignore
├── kaggle_assistant.ipynb # Jupyter Notebook for Kaggle
├── main.py                # Command-line interface
├── README.md
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

Create a `.env` file in the root of the project and add your Google API key:

```
GOOGLE_API_KEY="your_google_api_key"
```

**For Kaggle Notebooks:**

Use the "Secrets" feature in the Kaggle editor to add your `GOOGLE_API_KEY`.

### 5. Download the Meta Kaggle Datasets

The `install.sh` script *does not* automatically download the Meta Kaggle datasets due to their size. If you wish to use the agent with real data, you will need to manually download them.

First, make sure you have your `kaggle.json` API token set up. See the [Kaggle API documentation](https://www.kaggle.com/docs/api) for instructions.

Then, run the following commands to download the datasets into the `data/` directory:

```bash
kaggle datasets download -d kaggle/meta-kaggle -p data/meta-kaggle --unzip
kaggle datasets download -d kaggle/meta-kaggle-code -p data/meta-kaggle-code --unzip
```

## How to Run

### Command-Line Interface

To run the agent from your terminal, execute the `main.py` script:

```bash
python main.py
```

This will start an interactive chat session with the Kaggle Competition Assistant.

### Kaggle Notebook

1.  Upload the `kaggle_assistant.ipynb` notebook to a new Kaggle Notebook.
2.  Upload the `src` directory as a utility script to the notebook.
3.  Add the "Meta Kaggle" and "Meta Kaggle Code" datasets to the notebook's input data.
4.  Add your `GOOGLE_API_KEY` as a secret.
5.  Run the cells in the notebook.

The notebook will guide you through the process of initializing and interacting with the agent.
