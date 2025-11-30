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


def find_similar_competitions(query: str, metric: str = None):
    """
    Searches the Competitions table to find past challenges with similar titles,
    descriptions, or tags.
    """

    print(f"Finding similar competitions for query: '{query}', metric: '{metric}'")
    result = find_similar_competitions_query(datasets, query, metric)

    if not result:
        return f"No similar competitions found for query: '{query}'"

    return f"Found similar competitions: {result}"


def get_winning_solution_writeups(competition_id: int):
    """
    Retrieves 'Solution' posts from the discussion forums of a specific competition.
    """

    print(f"Getting winning solution write-ups for competition ID: {competition_id}")
    result = get_winning_solution_writeups_query(datasets, competition_id)

    if not result:
        return (
            f"No winning solution write-ups found for competition ID: {competition_id}"
        )

    return f"Found winning solution write-ups: {result}"


def get_top_scoring_kernels(
    competition_id: int, language: str = "Python", sort_by: str = "Votes"
):
    """
    Finds the highest-voted or best-performing public notebooks for a given competition.
    """

    print(
        f"Getting top scoring kernels for competition ID: {competition_id}, language: '{language}', sort_by: '{sort_by}'"
    )
    result = get_top_scoring_kernels_query(datasets, competition_id, language, sort_by)

    if not result:
        return f"No top scoring kernels found for competition ID: {competition_id}"

    return f"Found top scoring kernels: {result}"


def search_code_snippets(keywords: str, competition_id: int = None):
    """
    Searches the actual source code of notebooks to find how specific libraries or
    techniques were implemented.
    """

    print(
        f"Searching for code snippets with keywords: '{keywords}', in competition ID: {competition_id}"
    )
    result = search_code_snippets_query(datasets, keywords, competition_id)

    if not result:
        return f"No code snippets found for keywords: '{keywords}'"

    return f"Found code snippets: {result}"


def get_competition_id_from_url(url: str):
    """Parses a Kaggle competition URL to find its ID."""

    try:
        path = urlparse(url).path
        # Expected path format: /c/{slug} or /competitions/{slug}
        parts = path.strip("/").split("/")
        if parts[0] in ["c", "competitions"] and len(parts) > 1:
            slug = parts[1]
            print(f"Extracted slug: {slug}")
            comp_id = get_competition_id_from_slug_query(datasets, slug)
            if comp_id:
                return f"The competition ID for {slug} is {comp_id}."
            else:
                return f"Could not find a competition ID for slug: {slug}."
        else:
            return "Invalid Kaggle competition URL format."
    except Exception as e:
        return f"An error occurred while parsing the URL: {e}"


def analyze_tech_stack(competition_id: int):
    """
    Analyzes the import statements of top kernels to determine the most popular libraries.
    """

    print(f"Analyzing tech stack for competition ID: {competition_id}")
    result = analyze_tech_stack_query(datasets, competition_id)

    if not result:
        return f"Could not analyze tech stack for competition ID: {competition_id}"

    # Sort by frequency for better readability
    sorted_stack = sorted(result.items(), key=lambda item: item[1], reverse=True)
    return f"Tech stack analysis (library: usage_frequency): {sorted_stack}"


import google.generativeai as genai


def summarize_url_content(url: str):
    """Fetches and summarizes the content of a URL."""
    print(f"Fetching and summarizing URL: {url}")
    content = web_fetch(prompt=f"Get the content of {url}")

    if "Error" in content or "Simulated content" not in content:
        return f"Could not fetch valid content from the URL: {url}"

    try:
        summarizer_model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = summarizer_model.generate_content(
            f"Please summarize the following content from a Kaggle competition page, focusing on the competition's objective, evaluation metric, and timeline:\\n\\n{content}"
        )
        return response.text
    except Exception as e:
        return f"An error occurred during summarization: {e}"
