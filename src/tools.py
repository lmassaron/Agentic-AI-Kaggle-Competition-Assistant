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
        # It's a Kaggle URL, so use the specialized tools
        print("Kaggle URL detected. Using specialized tools for a detailed summary.")
        
        comp_id_str = get_competition_id_from_url(url) # Returns string message
        
        # We need to extract the actual slug from the message or just re-parse
        # The message is "The competition slug for {slug} is {verified_slug}."
        match = re.search(r"is ([^.]+)\\.$", comp_id_str)
        if match:
            comp_slug = match.group(1)
            
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
        else:
            return f"Could not extract a valid competition slug from URL: {url}"
            
    else:
        # Fallback to generic web_fetch for non-Kaggle URLs
        print("Non-Kaggle URL detected. Using generic web fetch.")
        content = web_fetch(prompt=f"Get the content of {url}")
        
        if "Error" in content:
            return f"Could not fetch valid content from the URL: {url}"
            
        return content