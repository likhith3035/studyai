def chunk_text(docs, chunk_size=500, overlap=50):
    chunks = []
    if not docs:
        return chunks

    for doc in docs:
        text = doc.get("text", "")
        if not text:
            continue
            
        words = text.split()
        
        current_chunk = []
        current_length = 0
        overlap_words = []
        
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1 # +1 for space
            
            if current_length >= chunk_size:
                chunks.append({
                    "text": " ".join(current_chunk),
                    "metadata": doc.get("metadata", {})
                })
                # Calculate overlap dynamically
                overlap_words = current_chunk[-max(1, overlap // 5):]
                current_chunk = overlap_words.copy()
                current_length = sum(len(w) + 1 for w in current_chunk)
                
        if current_chunk and len(current_chunk) > len(overlap_words):
            chunks.append({
                "text": " ".join(current_chunk),
                "metadata": doc.get("metadata", {})
            })

    return chunks