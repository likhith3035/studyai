from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Global model for efficient caching across requests.
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_index(chunks):
    """Creates a FAISS index using cosine similarity (Inner Product on normalized vectors)."""
    if not chunks:
        return None
        
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")
    
    # L2-normalize embeddings so Inner Product = Cosine Similarity
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]

    # IndexFlatIP = Inner Product (cosine similarity on normalized vectors)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return index

def search(query, index, chunks, k=5):
    """
    Search for relevant chunks and return results with cosine similarity scores.
    Returns: List of (chunk_text, similarity_score) tuples, sorted by score descending.
    Scores are 0.0 to 1.0 where 1.0 = perfect match.
    """
    if not chunks or index is None:
        return []
        
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)

    D, I = index.search(query_embedding, k)

    results = []
    for score, idx in zip(D[0], I[0]):
        if 0 <= idx < len(chunks):
            # Clamp score to [0, 1] range
            clamped_score = float(max(0.0, min(1.0, score)))
            results.append((chunks[idx], clamped_score))

    return results

def search_legacy(query, index, chunks, k=3):
    """Legacy search that returns only chunk text (for backward compatibility with quiz/summary/etc)."""
    scored_results = search(query, index, chunks, k)
    return [chunk for chunk, score in scored_results]