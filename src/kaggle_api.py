import os
import re
import glob
import tempfile
from kaggle.api.kaggle_api_extended import KaggleApi

# Initialize API
api = KaggleApi()
api.authenticate()

def get_slug_from_ref(ref_or_url):
    """Extracts slug from a reference or URL."""
    # If it's a full URL, extract the last part
    if "kaggle.com/competitions/" in ref_or_url or "kaggle.com/c/" in ref_or_url:
        return ref_or_url.rstrip('/').split('/')[-1]
    # If it is a ref like 'titanic', return it
    return ref_or_url

def find_similar_competitions_query(query, metric=None):
    """
    Queries the Kaggle API for competitions matching the query.
    """
    try:
        competitions_response = api.competitions_list(search=query)
        competitions = competitions_response.competitions if hasattr(competitions_response, 'competitions') else []
    except Exception as e:
        print(f"Error searching competitions: {e}")
        return []
    
    results = []
    for comp in competitions:
        # Filter by metric if provided
        if metric and metric.lower() not in (getattr(comp, 'evaluation_metric', '') or '').lower():
            continue
            
        # Extract slug. comp.ref might be URL or slug.
        slug = get_slug_from_ref(comp.ref)
        
        results.append({
            "Id": getattr(comp, 'id', None),
            "Slug": slug,
            "Title": comp.title,
            "EvaluationAlgorithmName": getattr(comp, 'evaluation_metric', 'Unknown'),
            "TotalTeams": getattr(comp, 'team_count', 0),
            "URL": getattr(comp, 'url', f"https://www.kaggle.com/c/{slug}")
        })
    
    # Sort by team count (proxy for popularity)
    results = sorted(results, key=lambda x: x['TotalTeams'], reverse=True)[:5]
    return results

def get_winning_solution_writeups_query(competition_slug):
    """
    Searches for kernels with 'solution' in the title for a given competition.
    Note: The API does not support searching forum topics directly.
    """
    try:
        # Search for kernels with "solution" in the title
        kernels = api.kernels_list(competition=competition_slug, search="solution", sort_by="voteCount", page_size=10)
    except Exception as e:
        print(f"Error searching winning solutions: {e}")
        return []
    
    solutions = []
    for k in kernels:
        solutions.append({
            "Title": k.title,
            "Score": k.total_votes,
            "URL": f"https://www.kaggle.com/{k.ref}",
            "Author": k.author
        })
    
    return solutions[:5]

def get_top_scoring_kernels_query(competition_slug, language, sort_by):
    """
    Queries for top-scoring kernels.
    """
    # Map sort_by to API values
    # API values: 'voteCount', 'score', 'dateRun', 'viewCount'
    api_sort = "voteCount"
    if sort_by == "PublicScore":
        api_sort = "score"
        
    try:
        kernels = api.kernels_list(competition=competition_slug, language=language.lower(), sort_by=api_sort, page_size=5)
    except Exception as e:
        print(f"Error searching top kernels: {e}")
        return []
    
    results = []
    for k in kernels:
        results.append({
            "Title": k.title,
            "DisplayName": k.author,
            "Score": k.total_votes if api_sort == "voteCount" else getattr(k, 'score', 'N/A'),
            "URL": f"https://www.kaggle.com/{k.ref}"
        })
    return results

def search_code_snippets_query(keywords, competition_slug=None):
    """
    Searches for code snippets in top kernels.
    """
    try:
        if competition_slug:
            kernels = api.kernels_list(competition=competition_slug, sort_by="voteCount", page_size=10)
        else:
            kernels = api.kernels_list(search=keywords, sort_by="voteCount", page_size=5)
    except Exception as e:
        print(f"Error searching kernels for snippets: {e}")
        return []
        
    found_snippets = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for k in kernels:
            try:
                # Download kernel code
                api.kernels_pull(k.ref, path=temp_dir, metadata=False, quiet=True)
                
                files = glob.glob(os.path.join(temp_dir, "*"))
                for file_path in files:
                    if os.path.isfile(file_path):
                        with open(file_path, 'r', errors='ignore') as f:
                            content = f.read()
                            if keywords in content:
                                # Extract snippet
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    if keywords in line:
                                        snippet = "\n".join(lines[max(0, i - 2) : i + 3])
                                        found_snippets.append({
                                            "Title": k.title,
                                            "URL": f"https://www.kaggle.com/{k.ref}",
                                            "Snippet": snippet
                                        })
                                        break
                        os.remove(file_path)
                        
            except Exception as e:
                # print(f"Error processing kernel {k.ref}: {e}")
                continue
                
            if len(found_snippets) >= 5:
                break
                
    return found_snippets

def analyze_tech_stack_query(competition_slug):
    """
    Analyzes the tech stack of top kernels.
    """
    try:
        kernels = api.kernels_list(competition=competition_slug, sort_by="voteCount", page_size=10)
    except Exception as e:
        print(f"Error fetching kernels for tech stack: {e}")
        return {}
        
    library_counts = {}
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for k in kernels:
            try:
                api.kernels_pull(k.ref, path=temp_dir, metadata=False, quiet=True)
                files = glob.glob(os.path.join(temp_dir, "*"))
                
                for file_path in files:
                    if os.path.isfile(file_path):
                         with open(file_path, 'r', errors='ignore') as f:
                            content = f.read()
                            imports = re.findall(
                                r"^import\s+(\w+)|^from\s+(\w+)", content, re.MULTILINE
                            )
                            libs = [item for t in imports for item in t if item]
                            for lib in set(libs):
                                library_counts[lib] = library_counts.get(lib, 0) + 1
                         os.remove(file_path)
            except Exception:
                continue

    total_kernels = len(kernels)
    if total_kernels == 0:
        return {}

    return {lib: count / total_kernels for lib, count in library_counts.items()}

def get_competition_id_from_slug_query(slug):
    """
    Verifies if a competition slug exists and returns it.
    """
    try:
        # Try to list kernels for this slug to verify it exists and is accessible
        # api.competitions_list(search=slug) is unreliable for exact match
        api.kernels_list(competition=slug, page_size=1)
        return slug
    except Exception:
        # If listing kernels fails, it might not exist or we can't access it.
        # Fallback: check competitions list
        try:
             comps_response = api.competitions_list(search=slug)
             comps = comps_response.competitions if hasattr(comps_response, 'competitions') else []
             for c in comps:
                 if get_slug_from_ref(c.ref).lower() == slug.lower():
                     return slug
        except Exception:
            pass
        return None