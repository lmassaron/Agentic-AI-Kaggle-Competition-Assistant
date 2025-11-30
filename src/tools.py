# src/tools.py

from urllib.parse import urlparse
from src.kaggle_api import (
    find_similar_competitions_query,
    get_winning_solution_writeups_query,
    get_top_scoring_kernels_query,
    search_code_snippets_query,
    analyze_tech_stack_query,
    get_competition_id_from_slug_query,
)
from src.built_in_tools import web_fetch  # Import web_fetch
import re


def find_similar_competitions(query: str, metric: str = None):
    """
    Searches the Competitions table to find past challenges with similar titles,
    descriptions, or tags.
    """
    if metric == "None":
        metric = None

    print(f"Finding similar competitions for query: '{query}', metric: '{metric}'")
    result = find_similar_competitions_query(query, metric)

    if not result:
        return f"No similar competitions found for query: '{query}'"

    return f"Found similar competitions: {result}"


def get_winning_solution_writeups(competition_slug: str):
    """
    Retrieves 'Solution' posts (or kernels) from a specific competition.
    """

    print(f"Getting winning solution write-ups for competition: {competition_slug}")
    result = get_winning_solution_writeups_query(competition_slug)

    if not result:
        return (
            f"No winning solution write-ups found for competition: {competition_slug}"
        )

    return f"Found winning solution write-ups: {result}"


def get_top_scoring_kernels(
    competition_slug: str, language: str = "Python", sort_by: str = "Votes"
):
    """
    Finds the highest-voted or best-performing public notebooks for a given competition.
    """

    print(
        f"Getting top scoring kernels for competition: {competition_slug}, language: '{language}', sort_by: '{sort_by}'"
    )
    result = get_top_scoring_kernels_query(competition_slug, language, sort_by)

    if not result:
        return f"No top scoring kernels found for competition: {competition_slug}"

    return f"Found top scoring kernels: {result}"


def search_code_snippets(keywords: str, competition_slug: str = None):
    """
    Searches the actual source code of notebooks to find how specific libraries or
    techniques were implemented.
    """

    print(
        f"Searching for code snippets with keywords: '{keywords}', in competition: {competition_slug}"
    )
    result = search_code_snippets_query(keywords, competition_slug)

    if not result:
        return f"No code snippets found for keywords: '{keywords}'"

    return f"Found code snippets: {result}"


def get_competition_id_from_url(url: str):
    """Parses a Kaggle competition URL to find its Slug/ID."""

    try:
        path = urlparse(url).path
        # Expected path format: /c/{slug} or /competitions/{slug}
        parts = path.strip("/").split("/")
        if parts[0] in ["c", "competitions"] and len(parts) > 1:
            slug = parts[1]
            print(f"Extracted slug: {slug}")
            verified_slug = get_competition_id_from_slug_query(slug)
            if verified_slug:
                return f"The competition slug for {slug} is {verified_slug}."
            else:
                return f"Could not verify competition slug: {slug}."
        else:
            return "Invalid Kaggle competition URL format."
    except Exception as e:
        return f"An error occurred while parsing the URL: {e}"


def analyze_tech_stack(competition_slug: str):
    """
    Analyzes the import statements of top kernels to determine the most popular libraries.
    """

    print(f"Analyzing tech stack for competition: {competition_slug}")
    result = analyze_tech_stack_query(competition_slug)

    if not result:
        return f"Could not analyze tech stack for competition: {competition_slug}"

    # Sort by frequency for better readability
    sorted_stack = sorted(result.items(), key=lambda item: item[1], reverse=True)
    return f"Tech stack analysis (library: usage_frequency): {sorted_stack}"

def summarize_url_content(url: str):
    """Fetches and summarizes the content of a URL. If it's a Kaggle competition URL, it will use specialized tools."""
    print(f"Fetching and summarizing URL: {url}")
    
    # Check if it's a Kaggle competition URL
    if "kaggle.com/c/" in url or "kaggle.com/competitions/" in url:
        print("Kaggle URL detected. Using specialized tools for a detailed summary.")
        
        # Extract slug directly here instead of calling the other tool and parsing NL
        try:
            path = urlparse(url).path
            parts = path.strip("/").split("/")
            if len(parts) > 1 and parts[0] in ["c", "competitions"]:
                comp_slug = parts[1]
                
                # Orchestrate the other tools to build a summary
                solutions = get_winning_solution_writeups(comp_slug)
                kernels = get_top_scoring_kernels(comp_slug)
                tech_stack = analyze_tech_stack(comp_slug)
                
                summary = (
                    f"Summary for competition {comp_slug}:\n"
                    f"Top Solutions: {solutions}\n"
                    f"Top Kernels: {kernels}\n"
                    f"Tech Stack: {tech_stack}"
                )
                return summary
        except Exception as e:
            print(f"Error extracting slug or summarizing specialized content: {e}")
            # Fallback to general search below
            pass
            
    # Fallback/General logic
    print("Using generic web fetch or search.")
    
    # Try generic web fetch first
    content = web_fetch(prompt=f"Get the content of {url}")
    
    if "Error" not in content and len(content) > 100:
        return content
    else:
        # Fallback to Google Search if direct fetch fails (common for protected pages like Kaggle)
        print("Direct fetch failed or content is protected. Falling back to Google Search.")
        from src.built_in_tools import google_web_search # Local import to avoid circular dependency
        
        query = f"site:{url} summary"
        if "kaggle.com" in url:
             # Make the query more specific for Kaggle competitions
             query = f"{url} winning solutions top kernels approach"
             
        search_results = google_web_search(query=query)
        return f"Direct access to the page was restricted. Here is what I found via search:\n{search_results}"