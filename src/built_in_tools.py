# src/built_in_tools.py

import requests
import re
from bs4 import BeautifulSoup

def web_fetch(prompt: str) -> str:
    """
    Fetches the text content of a URL found within the prompt.
    It cleans the HTML to return only readable text, stripping scripts and styles.

    Args:
        prompt (str): A string containing a URL (e.g., "Get the content of https://kaggle.com")

    Returns:
        str: The clean text content of the page, or an error message.
    """
    # 1. Extract the URL using Regex (finds http or https links)
    url_match = re.search(r"(https?://[^\s]+)", prompt)

    if not url_match:
        return "Error: No valid URL found in the prompt."

    url = url_match.group(0)

    # 2. Set headers to mimic a real browser (prevents 403 blocks from sites like Wikipedia/Kaggle)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        # 3. Make the request with a timeout (don't let the agent hang forever)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raises an error for 4xx or 5xx status codes

        # 4. Parse the HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # 5. Remove 'junk' elements (scripts, styles, navbars, footers often add noise)
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.decompose()

        # 6. Extract text and clean whitespace
        text = soup.get_text()

        # Collapse multiple newlines into one and strip leading/trailing whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        # Optional: Limit length to prevent overflowing the AI's context window
        return clean_text[:10000]  # Returns first 10k chars

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP Error fetching {url}: {http_err}"
    except requests.exceptions.ConnectionError:
        return f"Connection Error: Could not reach {url}."
    except requests.exceptions.Timeout:
        return f"Timeout Error: {url} took too long to respond."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def google_web_search(query: str) -> str:
    """
    Performs a web search using DuckDuckGo (via duckduckgo_search package).
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
        if not results:
            return f"No results found for query: {query}"
            
        formatted_results = ""
        for i, res in enumerate(results, 1):
            formatted_results += f"{i}. {res.get('title', 'No Title')}\n   URL: {res.get('href', 'No URL')}\n   Snippet: {res.get('body', 'No Snippet')}\n\n"
            
        return formatted_results
        
    except ImportError:
        return "Error: duckduckgo-search package is not installed. Please run 'pip install duckduckgo-search'."
    except Exception as e:
        return f"Error performing search: {e}"