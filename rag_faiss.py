from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Let's keep it global so it caches effectively across requests.
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_index(chunks):
    if not chunks:
        return None
        
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index

def search(query, index, chunks, k=3):
    if not chunks or index is None:
        return []
        
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")

    D, I = index.search(query_embedding, k)

    results = []
    for i in I[0]:
        if 0 <= i < len(chunks):
            results.append(chunks[i])

    return results