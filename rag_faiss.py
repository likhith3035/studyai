from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Global model for efficient caching across requests.
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_index(chunks):
    """Creates a FAISS index using cosine similarity (Inner Product on normalized vectors)."""
    if not chunks:
        return None
        
    texts = [c["text"] if isinstance(c, dict) else c for c in chunks]
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype("float32")
    
    # L2-normalize embeddings so Inner Product = Cosine Similarity
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    # IndexFlatIP = Inner Product (cosine similarity on normalized vectors)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return index

import re

def compute_keyword_score(query, text):
    query_words = set(w for w in re.findall(r'\b\w+\b', query.lower()) if len(w) > 2)
    if not query_words:
        return 0.0
    
    text_words = re.findall(r'\b\w+\b', text.lower())
    match_count = sum(1 for w in query_words if w in text_words)
    
    return float(match_count / len(query_words))

def search(query, index, chunks, k=5):
    """
    Hybrid Search: Combines FAISS cosine similarity with Exact Keyword matching.
    Returns: List of (chunk_dict, hybrid_score) tuples, sorted by score descending.
    """
    if not chunks or index is None:
        return []
        
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)

    # Fetch a wider pool (top 15) to re-rank
    fetch_k = min(len(chunks), k * 3)
    if fetch_k == 0:
        return []
        
    D, I = index.search(query_embedding, fetch_k)

    hybrid_results = []
    
    # Track indices we process so we don't duplicate
    processed_indices = set()
    
    for score, idx in zip(D[0], I[0]):
        if 0 <= idx < len(chunks):
            processed_indices.add(idx)
            chunk = chunks[idx]
            text = chunk["text"] if isinstance(chunk, dict) else chunk
            
            v_score = float(max(0.0, min(1.0, score)))
            k_score = compute_keyword_score(query, text)
            
            # 70% Semantic, 30% Keyword
            final_score = (v_score * 0.70) + (k_score * 0.30)
            hybrid_results.append((chunk, final_score))
            
    # Also scan top purely keyword hits globally just in case vectors missed an acronym entirely
    for idx, chunk in enumerate(chunks):
        if idx not in processed_indices:
            text = chunk["text"] if isinstance(chunk, dict) else chunk
            k_score = compute_keyword_score(query, text)
            if k_score > 0.5: # Only include if it's a very strong exact match
                v_score = 0.15 # Baseline penalty for failing vector search
                final_score = (v_score * 0.70) + (k_score * 0.30)
                hybrid_results.append((chunk, final_score))

    hybrid_results.sort(key=lambda x: x[1], reverse=True)
    return hybrid_results[:k]

def search_legacy(query, index, chunks, k=3):
    """Legacy search that returns only chunk text (for backward compatibility with quiz/summary/etc)."""
    scored_results = search(query, index, chunks, k)
    return [chunk["text"] if isinstance(chunk, dict) else chunk for chunk, score in scored_results]