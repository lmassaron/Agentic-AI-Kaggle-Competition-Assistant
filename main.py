# main.py

import os
import json
from dotenv import load_dotenv
from src.agent import KaggleAgent


def main():
    """
    Main function to run the Kaggle Competition Assistant CLI.
    """
    # Load .env file if it exists, but don't override existing env vars
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if not google_api_key:
        print("Error: GOOGLE_API_KEY not found.")
        print(
            "Please set the GOOGLE_API_KEY environment variable or create a .env file with its value."
        )
        return

    print("Initializing Kaggle Competition Assistant...")
    agent = KaggleAgent(api_key=google_api_key)
    print("Assistant is ready. Type 'exit' to quit.")
    print("Available commands: !stats, !history, !logs, !reset")
    print("-" * 50)

    while True:
        try:
            user_query = input("You: ")
            if not user_query:
                continue

            if user_query.lower() == "exit":
                print("Goodbye!")
                break

            # Handle special commands
            if user_query == "!stats":
                print(json.dumps(agent.get_session_stats(), indent=2))
            elif user_query == "!history":
                print(json.dumps(agent.memory.get_full_history(), indent=2))
            elif user_query == "!logs":
                print(json.dumps(agent.logger.export_logs(), indent=2))
            elif user_query == "!reset":
                agent.reset_session()
                print("Agent session has been reset.")
            else:
                response = agent.run(user_query)
                print(f"Assistant: {response}")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
