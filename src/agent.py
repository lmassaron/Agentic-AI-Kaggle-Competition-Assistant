# src/agent.py

import json
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

from src.tools import (
    find_similar_competitions,
    get_winning_solution_writeups,
    get_top_scoring_kernels,
    search_code_snippets,
    analyze_tech_stack,
    summarize_url_content,
    get_competition_id_from_url,
)


@dataclass
class ConversationMemory:
    """Manages conversation history and state for a session."""

    messages: List[Dict[str, str]] = field(default_factory=list)
    max_history: int = 20

    def add_message(self, role: str, content: str):
        """Adds a message to the conversation history."""
        self.messages.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )
        # Trim history if it exceeds the maximum length
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

    def get_context(self) -> str:
        """Returns the recent conversation history as a JSON string."""
        return json.dumps(self.messages[-5:])  # Return last 5 for concise context

    def get_full_history(self) -> List[Dict[str, str]]:
        """Returns the full conversation history."""
        return self.messages

    def clear(self):
        """Clears the conversation history, effectively resetting the session."""
        self.messages.clear()

    def get_stats(self) -> Dict[str, int]:
        """Returns statistics about the conversation."""
        return {
            "total_messages": len(self.messages),
            "user_messages": sum(1 for m in self.messages if m["role"] == "user"),
            "assistant_messages": sum(
                1 for m in self.messages if m["role"] == "assistant"
            ),
        }


@dataclass
class AgentLogger:
    """Provides observability into agent operations through logging."""

    logs: List[Dict[str, Any]] = field(default_factory=list)

    def log(self, level: str, event: str, details: Dict[str, Any] = None):
        """Records a log entry."""
        self.logs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "event": event,
                "details": details or {},
            }
        )

    def info(self, event: str, **kwargs):
        self.log("INFO", event, kwargs)

    def error(self, event: str, **kwargs):
        self.log("ERROR", event, kwargs)

    def get_stats(self) -> Dict[str, int]:
        """Returns statistics about the logs."""
        return {
            "total_logs": len(self.logs),
            "info_count": sum(1 for log in self.logs if log["level"] == "INFO"),
            "error_count": sum(1 for log in self.logs if log["level"] == "ERROR"),
        }

    def export_logs(self) -> List[Dict[str, Any]]:
        """Returns all log entries."""
        return self.logs


class KaggleAgent:
    """The main agent for assisting with Kaggle competitions."""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.memory = ConversationMemory()
        self.logger = AgentLogger()
        self.stats = {"queries_processed": 0, "tools_called": 0, "errors": 0}

        self.function_declarations = [
            FunctionDeclaration(
                name="find_similar_competitions",
                description="Searches for similar competitions.",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keywords to search for."},
                        "metric": {"type": "string", "description": "Evaluation metric to filter by (optional)."}
                    },
                    "required": ["query"]
                }
            ),
            FunctionDeclaration(
                name="get_winning_solution_writeups",
                description="Retrieves winning solution writeups (kernels) for a competition.",
                parameters={
                    "type": "object",
                    "properties": {
                        "competition_slug": {"type": "string", "description": "The slug of the competition."}
                    },
                    "required": ["competition_slug"]
                }
            ),
            FunctionDeclaration(
                name="get_top_scoring_kernels",
                description="Finds top scoring kernels for a competition.",
                parameters={
                    "type": "object",
                    "properties": {
                        "competition_slug": {"type": "string", "description": "The slug of the competition."},
                        "language": {"type": "string", "description": "Python or R."},
                        "sort_by": {"type": "string", "description": "Votes or PublicScore."}
                    },
                    "required": ["competition_slug"]
                }
            ),
            FunctionDeclaration(
                name="search_code_snippets",
                description="Searches for specific code snippets in kernels.",
                parameters={
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "string", "description": "Code or text to search for."},
                        "competition_slug": {"type": "string", "description": "Competition slug to limit search (optional)."}
                    },
                    "required": ["keywords"]
                }
            ),
            FunctionDeclaration(
                name="analyze_tech_stack",
                description="Analyzes the technology stack (libraries) used in top kernels.",
                parameters={
                    "type": "object",
                    "properties": {
                        "competition_slug": {"type": "string", "description": "The slug of the competition."}
                    },
                    "required": ["competition_slug"]
                }
            ),
            FunctionDeclaration(
                name="summarize_url_content",
                description="Fetches and summarizes the content of a URL.",
                parameters={
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"]
                },
            ),
            FunctionDeclaration(
                name="get_competition_id_from_url",
                description="Parses a Kaggle competition URL to find its competition Slug.",
                parameters={
                    "type": "object",
                    "properties": {"url": {"type": "string"}},
                    "required": ["url"]
                },
            ),
        ]

        self.tools = Tool(function_declarations=self.function_declarations)
        self.model = genai.GenerativeModel(
            model_name="models/gemini-2.5-flash", tools=[self.tools]
        )
        self.logger.info("Agent initialized")

    def _call_function(self, function_call) -> str:
        function_map = {
            "find_similar_competitions": find_similar_competitions,
            "get_winning_solution_writeups": get_winning_solution_writeups,
            "get_top_scoring_kernels": get_top_scoring_kernels,
            "search_code_snippets": search_code_snippets,
            "analyze_tech_stack": analyze_tech_stack,
            "summarize_url_content": summarize_url_content,
            "get_competition_id_from_url": get_competition_id_from_url,
        }
        
        func_name = function_call.name
        func_args = function_call.args
        
        if func_name in function_map:
            try:
                # Convert args to dict to ensure compatibility
                args_dict = dict(func_args)
                self.logger.info("Tool execution started", tool=func_name, args=args_dict)
                self.stats["tools_called"] += 1
                result = function_map[func_name](**args_dict)
                self.logger.info("Tool execution successful", tool=func_name)
                return str(result)
            except Exception as e:
                self.logger.error("Tool execution failed", tool=func_name, error=str(e))
                return f"Error executing {func_name}: {e}"
        return f"Unknown function: {func_name}"

    def run(self, user_query: str) -> str:
        self.logger.info("Query received", query=user_query)
        self.stats["queries_processed"] += 1
        self.memory.add_message("user", user_query)

        chat = self.model.start_chat()
        prompt = f"Based on the conversation so far: {self.memory.get_context()}, process the following query: {user_query}"

        # ReAct Loop
        while True:
            response = chat.send_message(prompt)
            try:
                # Handle possible empty response or safety blocks
                if not response.candidates:
                     response_text = "I'm sorry, I couldn't generate a response."
                     break
                     
                part = response.candidates[0].content.parts[0]

                if part.function_call:
                    function_call = part.function_call
                    print(f"Tool call: {function_call.name}({function_call.args})")

                    result = self._call_function(function_call)

                    prompt = f"Function {function_call.name} returned: {result}. What is the next step? If you have a final answer for the user, provide it directly."
                else:
                    response_text = part.text
                    break
            except (ValueError, IndexError) as e:
                response_text = (
                    response.text
                    if hasattr(response, "text")
                    else f"No valid response found. Error: {e}"
                )
                self.logger.error("Response parsing failed", response=str(response))
                self.stats["errors"] += 1
                break

        self.memory.add_message("assistant", response_text)
        self.logger.info("Query completed")
        return response_text

    def reset_session(self):
        """Resets the agent's memory and stats for a new session."""
        self.memory.clear()
        self.stats = {"queries_processed": 0, "tools_called": 0, "errors": 0}
        self.logger.info("Agent session has been reset.")

    def get_session_stats(self) -> Dict[str, Any]:
        """Returns combined statistics for the current session."""
        return {
            "agent_stats": self.stats,
            "memory_stats": self.memory.get_stats(),
            "logger_stats": self.logger.get_stats(),
        }