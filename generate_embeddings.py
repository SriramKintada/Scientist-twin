"""
Generate vector embeddings for all scientists
Uses sentence-transformers for high-quality embeddings
"""

import json
import os
from typing import List, Dict
import numpy as np

# Try to import sentence_transformers, fallback to simple TF-IDF if not available
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDER = SentenceTransformer('all-MiniLM-L6-v2')  # 384-dim embeddings
    USE_TRANSFORMERS = True
    print("[Embeddings] Using sentence-transformers (high quality)")
except ImportError:
    USE_TRANSFORMERS = False
    print("[Embeddings] sentence-transformers not available, using TF-IDF fallback")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD


def create_scientist_text(scientist: Dict) -> str:
    """Create rich text representation of a scientist for embedding"""
    parts = []

    # Name and field
    parts.append(f"{scientist.get('name', '')} is a {scientist.get('field', '')} scientist")

    # Subfield
    if scientist.get('subfield'):
        parts.append(f"specializing in {scientist['subfield']}")

    # Era
    if scientist.get('era'):
        parts.append(f"from the {scientist['era']} era")

    # Archetype
    if scientist.get('archetype'):
        parts.append(f"known as a {scientist['archetype']}")

    # Summary (key info)
    if scientist.get('summary'):
        # Take first 500 chars of summary
        parts.append(scientist['summary'][:500])

    # Achievements
    if scientist.get('achievements'):
        parts.append(f"Achievements: {scientist['achievements'][:300]}")

    # Working style
    if scientist.get('working_style'):
        parts.append(f"Working style: {scientist['working_style'][:200]}")

    # Traits (convert to natural language)
    traits = scientist.get('traits', {})
    if traits:
        trait_text = []
        trait_descriptions = {
            'approach': {'theoretical': 'theoretical thinker', 'experimental': 'experimentalist', 'applied': 'applied researcher', 'observational': 'keen observer'},
            'collaboration': {'solo': 'independent worker', 'small_team': 'team collaborator', 'large_team': 'team leader', 'mentor': 'dedicated mentor'},
            'risk': {'conservative': 'methodical', 'calculated': 'strategic', 'bold': 'bold risk-taker', 'hedged': 'balanced'},
            'motivation': {'curiosity': 'curiosity-driven', 'impact': 'impact-focused', 'recognition': 'excellence-seeking', 'duty': 'duty-bound'},
            'adversity': {'persist': 'persistent', 'pivot': 'adaptable', 'fight': 'fighter', 'accept': 'resilient'}
        }
        for dim, value in traits.items():
            if dim in trait_descriptions and value in trait_descriptions[dim]:
                trait_text.append(trait_descriptions[dim][value])
        if trait_text:
            parts.append(f"Personality: {', '.join(trait_text)}")

    # Key moments
    moments = scientist.get('moments', [])
    if moments and len(moments) > 0:
        parts.append(f"Key moment: {moments[0][:200]}")

    return ". ".join(parts)


def generate_embeddings_transformers(texts: List[str]) -> np.ndarray:
    """Generate embeddings using sentence-transformers"""
    embeddings = EMBEDDER.encode(texts, show_progress_bar=True)
    return embeddings


def generate_embeddings_tfidf(texts: List[str], dim: int = 384) -> np.ndarray:
    """Fallback: Generate embeddings using TF-IDF + SVD"""
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)

    # Reduce to target dimensions
    svd = TruncatedSVD(n_components=min(dim, tfidf_matrix.shape[1] - 1))
    embeddings = svd.fit_transform(tfidf_matrix)

    # Pad if needed
    if embeddings.shape[1] < dim:
        padding = np.zeros((embeddings.shape[0], dim - embeddings.shape[1]))
        embeddings = np.hstack([embeddings, padding])

    return embeddings


def generate_all_embeddings(database_path: str = 'scientist_db_rich.json') -> Dict[str, List[float]]:
    """Generate embeddings for all scientists in database"""
    print(f"[Embeddings] Loading scientists from {database_path}...")

    with open(database_path, 'r', encoding='utf-8') as f:
        scientists = json.load(f)

    print(f"[Embeddings] Found {len(scientists)} scientists")

    # Create text representations
    texts = []
    names = []
    for scientist in scientists:
        text = create_scientist_text(scientist)
        texts.append(text)
        names.append(scientist['name'])
        print(f"  - {scientist['name']}: {len(text)} chars")

    # Generate embeddings
    print(f"\n[Embeddings] Generating embeddings...")
    if USE_TRANSFORMERS:
        embeddings = generate_embeddings_transformers(texts)
    else:
        embeddings = generate_embeddings_tfidf(texts)

    print(f"[Embeddings] Generated {embeddings.shape[0]} embeddings of dimension {embeddings.shape[1]}")

    # Create name -> embedding mapping
    result = {}
    for i, name in enumerate(names):
        result[name] = embeddings[i].tolist()

    return result


def save_embeddings(embeddings: Dict[str, List[float]], output_path: str = 'scientist_embeddings.json'):
    """Save embeddings to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(embeddings, f)
    print(f"[Embeddings] Saved to {output_path}")


def upload_embeddings_to_supabase(embeddings: Dict[str, List[float]]):
    """Upload embeddings to Supabase"""
    try:
        from supabase_client import update_scientist_embedding, is_connected

        if not is_connected():
            print("[Embeddings] Supabase not connected. Skipping upload.")
            return

        print("[Embeddings] Uploading to Supabase...")
        success = 0
        for name, embedding in embeddings.items():
            if update_scientist_embedding(name, embedding):
                success += 1
                print(f"  - Updated: {name}")

        print(f"[Embeddings] Uploaded {success}/{len(embeddings)} embeddings")

    except ImportError:
        print("[Embeddings] Supabase client not available. Skipping upload.")


if __name__ == "__main__":
    # Generate embeddings
    embeddings = generate_all_embeddings()

    # Save locally
    save_embeddings(embeddings)

    # Optionally upload to Supabase
    upload_embeddings_to_supabase(embeddings)

    print("\n[Embeddings] Done!")
