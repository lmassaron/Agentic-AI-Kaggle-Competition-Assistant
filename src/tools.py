# src/tools.py

from urllib.parse import urlparse
from src.kaggle_api import (
    find_similar_competitions_query,
    get_winning_solution_writeups_query,
    get_top_scoring_kernels_query,
    search_code_snippets_query,
    analyze_tech_stack_query,
    get_competition_id_from_slug_query,
    load_data,
)
from src.built_in_tools import web_fetch  # Import web_fetch

# Load the datasets once when the module is imported
try:
    datasets = load_data()
except Exception as e:
    print(f"Warning: Could not load Kaggle datasets. Tools will not work. Error: {e}")
    datasets = None


def find_similar_competitions(query: str, metric: str = None):
    """
    Searches the Competitions table to find past challenges with similar titles,
    descriptions, or tags.
    """
    if not datasets:
        return "Kaggle datasets are not loaded."

    print(f"Finding similar competitions for query: '{query}', metric: '{metric}'")
    result = find_similar_competitions_query(datasets, query, metric)

    if not result:
        return f"No similar competitions found for query: '{query}'"

    return f"Found similar competitions: {result}"


def get_winning_solution_writeups(competition_id: int):
    """
    Retrieves 'Solution' posts from the discussion forums of a specific competition.
    """
    if not datasets:
        return "Kaggle datasets are not loaded."

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
    if not datasets:
        return "Kaggle datasets are not loaded."

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
    if not datasets:
        return "Kaggle datasets are not loaded."

    print(
        f"Searching for code snippets with keywords: '{keywords}', in competition ID: {competition_id}"
    )
    result = search_code_snippets_query(datasets, keywords, competition_id)

    if not result:
        return f"No code snippets found for keywords: '{keywords}'"

    return f"Found code snippets: {result}"


def get_competition_id_from_url(url: str):
    """Parses a Kaggle competition URL to find its ID."""
    if not datasets:
        return "Kaggle datasets are not loaded."

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
    if not datasets:
        return "Kaggle datasets are not loaded."

    print(f"Analyzing tech stack for competition ID: {competition_id}")
    result = analyze_tech_stack_query(datasets, competition_id)

    if not result:
        return f"Could not analyze tech stack for competition ID: {competition_id}"

    # Sort by frequency for better readability
    sorted_stack = sorted(result.items(), key=lambda item: item[1], reverse=True)
    return f"Tech stack analysis (library: usage_frequency): {sorted_stack}"


def analyze_competition_by_url(url: str):
    """
    Analyzes a Kaggle competition page by its URL to provide a summary.
    """
    print(f"Analyzing competition at URL: {url}")

    # Use the web_fetch tool to get the content of the page
    # This assumes web_fetch is available in the agent's context
    page_content = web_fetch(prompt=f"Get the content of {url}")

    if "Error" in page_content:
        return f"Could not fetch the content of the URL: {page_content}"

    # Here, you would typically use another LLM call to summarize the content,
    # but for now, we'll return a placeholder analysis.
    return f"Successfully fetched content from {url}. Analysis would go here."
