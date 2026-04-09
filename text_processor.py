def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    if not text:
        return chunks

    # A simple word-based chunker instead of raw characters to preserve words.
    words = text.split()
    
    current_chunk = []
    current_length = 0
    overlap_words = []
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1 # +1 for space
        
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            # Calculate overlap dynamically
            overlap_words = current_chunk[-max(1, overlap // 5):]
            current_chunk = overlap_words.copy()
            current_length = sum(len(w) + 1 for w in current_chunk)
            
    if current_chunk and len(current_chunk) > len(overlap_words):
        chunks.append(" ".join(current_chunk))

    return chunks