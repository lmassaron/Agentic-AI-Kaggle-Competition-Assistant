# src/kaggle_api.py

import os
import re
import pandas as pd
from tqdm import tqdm

# In a Kaggle environment, the data is typically at /kaggle/input/
# For local development, we'll use the 'data/' directory.
BASE_PATH = "/kaggle/input/" if "KAGGLE_KERNEL_RUN_TYPE" in os.environ else "data/"
META_KAGGLE_PATH = os.path.join(BASE_PATH, "meta-kaggle")
META_KAGGLE_CODE_PATH = os.path.join(BASE_PATH, "meta-kaggle-code")


def load_data():
    """Loads the necessary Meta Kaggle CSV files into pandas DataFrames."""
    print("Loading Meta Kaggle datasets...")

    competitions_df = pd.read_csv(os.path.join(META_KAGGLE_PATH, "Competitions.csv"))
    competition_tags_df = pd.read_csv(
        os.path.join(META_KAGGLE_PATH, "CompetitionTags.csv")
    )
    tags_df = pd.read_csv(os.path.join(META_KAGGLE_PATH, "Tags.csv"))
    forum_topics_df = pd.read_csv(os.path.join(META_KAGGLE_PATH, "ForumTopics.csv"))
    forum_messages_df = pd.read_csv(os.path.join(META_KAGGLE_PATH, "ForumMessages.csv"))
    kernels_df = pd.read_csv(os.path.join(META_KAGGLE_PATH, "Kernels.csv"))
    kernel_versions_df = pd.read_csv(
        os.path.join(META_KAGGLE_PATH, "KernelVersions.csv")
    )
    users_df = pd.read_csv(os.path.join(META_KAGGLE_PATH, "Users.csv"))

    print("Datasets loaded successfully.")

    return {
        "competitions": competitions_df,
        "competition_tags": competition_tags_df,
        "tags": tags_df,
        "forum_topics": forum_topics_df,
        "forum_messages": forum_messages_df,
        "kernels": kernels_df,
        "kernel_versions": kernel_versions_df,
        "users": users_df,
    }


# --- Tool-specific query functions will be added below ---


def find_similar_competitions_query(datasets, query, metric=None):
    """
    Queries the datasets to find similar competitions.
    - query (string): Keywords to search for.
    - metric (string, optional): The evaluation metric.
    """
    competitions_df = datasets["competitions"]

    # Search in title and subtitle
    query_mask = (competitions_df["Title"].str.contains(query, case=False)) | (
        competitions_df["Subtitle"].str.contains(query, case=False)
    )

    results_df = competitions_df[query_mask]

    if metric:
        results_df = results_df[
            results_df["EvaluationAlgorithmName"].str.contains(
                metric, case=False, na=False
            )
        ]

    # Sort by the number of submissions and take top 5
    results_df = results_df.sort_values(by="TotalSubmissions", ascending=False).head(5)

    return results_df[
        ["Id", "Title", "EvaluationAlgorithmName", "TotalSubmissions"]
    ].to_dict("records")


def get_winning_solution_writeups_query(datasets, competition_id):
    """
    Queries for winning solution writeups for a given competition.
    - competition_id (int): The ID of the competition.
    """
    competitions_df = datasets["competitions"]
    forum_topics_df = datasets["forum_topics"]

    # Get the ForumId for the given competition
    forum_id = competitions_df[competitions_df["Id"] == competition_id]["ForumId"].iloc[
        0
    ]

    if pd.isna(forum_id):
        return []

    # Filter forum topics for that forum
    competition_topics_df = forum_topics_df[forum_topics_df["ForumId"] == forum_id]

    # Search for solution-related keywords
    solution_keywords = [
        "solution",
        "1st place",
        "gold",
        "winning",
        "approach",
        "write-up",
    ]
    keyword_mask = competition_topics_df["Title"].str.contains(
        "|".join(solution_keywords), case=False
    )

    solutions_df = competition_topics_df[keyword_mask]

    # Sort by score and take top 5
    solutions_df = solutions_df.sort_values(by="Score", ascending=False).head(5)

    # Add a URL for easy access
    solutions_df["URL"] = solutions_df.apply(
        lambda row: f"https://www.kaggle.com/c/{competition_id}/discussion/{row['Id']}",
        axis=1,
    )

    return solutions_df[["Title", "Score", "URL"]].to_dict("records")


def get_top_scoring_kernels_query(datasets, competition_id, language, sort_by):
    """
    Queries for top-scoring kernels.
    - competition_id (int): The competition ID.
    - language (string): "Python" or "R".
    - sort_by (string): "Votes" or "PublicScore".
    """
    kernels_df = datasets["kernels"]
    kernel_versions_df = datasets["kernel_versions"]
    users_df = datasets["users"]

    # Filter for the specific competition
    comp_kernels_df = kernels_df[kernels_df["CompetitionId"] == competition_id]

    # Merge with kernel versions to get language and other details
    merged_df = pd.merge(
        comp_kernels_df,
        kernel_versions_df,
        left_on="CurrentKernelVersionId",
        right_on="Id",
    )

    # Filter by language
    language_map = {"Python": 1, "R": 2}  # Based on KernelLanguages table
    if language in language_map:
        merged_df = merged_df[merged_df["KernelLanguageId"] == language_map[language]]

    # Merge with users to get author name
    merged_df = pd.merge(
        merged_df,
        users_df,
        left_on="AuthorUserId",
        right_on="Id",
        suffixes=("_kernel", "_user"),
    )

    # Determine sort column
    sort_column = "TotalVotes" if sort_by == "Votes" else "Medal"

    # Sort and take top 5
    top_kernels_df = merged_df.sort_values(by=sort_column, ascending=False).head(5)

    return top_kernels_df[["Title", "DisplayName", sort_column]].to_dict("records")


def search_code_snippets_query(datasets, keywords, competition_id=None):
    """
    Searches for code snippets in kernels.
    - keywords (string): The code to search for.
    - competition_id (int, optional): The competition to search within.
    """
    kernels_df = datasets["kernels"]
    kernel_versions_df = datasets["kernel_versions"]

    if competition_id:
        target_kernels_df = kernels_df[kernels_df["CompetitionId"] == competition_id]
    else:
        target_kernels_df = kernels_df

    # Limit search to the top 20 most voted kernels for performance
    top_kernels = target_kernels_df.sort_values(by="TotalVotes", ascending=False).head(
        20
    )

    # Get the source file info
    kernel_info = pd.merge(
        top_kernels, kernel_versions_df, left_on="CurrentKernelVersionId", right_on="Id"
    )

    found_snippets = []

    for _, row in tqdm(
        kernel_info.iterrows(), total=kernel_info.shape[0], desc="Searching snippets"
    ):
        slug = row["Slug"]
        file_extension = row["SourceFileExtension"]
        kernel_path = os.path.join(META_KAGGLE_CODE_PATH, f"{slug}.{file_extension}")

        try:
            with open(kernel_path, "r", encoding="utf-8") as f:
                content = f.read()
                if keywords in content:
                    # Basic snippet extraction: find the line and a few lines around it
                    lines = content.split("\\n")
                    for i, line in enumerate(lines):
                        if keywords in line:
                            snippet = "\\n".join(lines[max(0, i - 2) : i + 3])
                            found_snippets.append(
                                {
                                    "Title": row["Title"],
                                    "URL": f"https://www.kaggle.com/{row['UserName']}/{slug}",
                                    "Snippet": snippet,
                                }
                            )
                            if len(found_snippets) >= 5:  # Limit to 5 snippets
                                return found_snippets
                            break
        except FileNotFoundError:
            continue  # Not all kernels might be available

    return found_snippets


def get_competition_id_from_slug_query(datasets, slug):
    """Finds a competition ID from its slug."""
    competitions_df = datasets["competitions"]
    comp = competitions_df[competitions_df["Slug"].str.lower() == slug.lower()]
    if not comp.empty:
        return comp.iloc[0]["Id"]
    return None


def analyze_tech_stack_query(datasets, competition_id):
    """
    Analyzes the technology stack of top kernels in a competition.
    - competition_id (int): The competition to analyze.
    """
    kernels_df = datasets["kernels"]
    kernel_versions_df = datasets["kernel_versions"]

    # Get top 20 kernels for the competition
    comp_kernels_df = kernels_df[kernels_df["CompetitionId"] == competition_id]
    top_kernels = comp_kernels_df.sort_values(by="TotalVotes", ascending=False).head(20)
    kernel_info = pd.merge(
        top_kernels, kernel_versions_df, left_on="CurrentKernelVersionId", right_on="Id"
    )

    library_counts = {}

    for _, row in tqdm(
        kernel_info.iterrows(), total=kernel_info.shape[0], desc="Analyzing tech stack"
    ):
        slug = row["Slug"]
        file_extension = row["SourceFileExtension"]
        kernel_path = os.path.join(META_KAGGLE_CODE_PATH, f"{slug}.{file_extension}")

        try:
            with open(kernel_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Find all imports using regex
                imports = re.findall(
                    r"^import\\s+(\\w+)|^from\\s+(\\w+)", content, re.MULTILINE
                )
                # Flatten the list of tuples and filter out empty strings
                libs = [item for t in imports for item in t if item]

                for lib in set(
                    libs
                ):  # Use set to count each library only once per kernel
                    library_counts[lib] = library_counts.get(lib, 0) + 1
        except FileNotFoundError:
            continue

    # Calculate frequency
    total_kernels = len(kernel_info)
    if total_kernels == 0:
        return {}

    return {lib: count / total_kernels for lib, count in library_counts.items()}
