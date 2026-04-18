import re
from typing import List

QUIZ_SYSTEM_PROMPT = """You are a quiz generator for a student learning platform called Padh.AI. Generate exactly 5 multiple-choice questions based on the given topic or retrieved document content.

CRITICAL: You MUST respond with ONLY a valid JSON array, no markdown, no explanation, no code fences. The response must start with [ and end with ].

Each question object must have exactly this structure:
{"id":1,"question":"...","options":["A","B","C","D"],"correct":0}

Rules:
- "correct" is the 0-based index of the correct option (0, 1, 2, or 3)
- Each question must have exactly 4 options
- Questions should be educational, clear, and progressively challenging
- Cover different aspects of the topic or retrieved content
- Keep questions concise and student-friendly"""

_EMBEDDER_MODEL_NAME = "all-MiniLM-L6-v2"
_EMBEDDER = None


def get_embedder():
    global _EMBEDDER
    if _EMBEDDER is None:
        from sentence_transformers import SentenceTransformer

        _EMBEDDER = SentenceTransformer(_EMBEDDER_MODEL_NAME)
    return _EMBEDDER


def chunk_text(
    text: str, chunk_size: int = 900, overlap: int = 150, max_chunks: int = 80
) -> List[str]:
    text = (text or "").replace("\r\n", "\n").strip()
    if not text:
        return []

    chunks: List[str] = []
    start = 0
    text_length = len(text)

    while start < text_length and len(chunks) < max_chunks:
        end = min(text_length, start + chunk_size)
        if end < text_length:
            newline = text.rfind("\n", start, end)
            if newline != -1 and newline > start + int(chunk_size * 0.5):
                end = newline

        chunk = text[start:end].strip()
        if len(chunk) >= 120:
            chunks.append(chunk)

        if end >= text_length:
            break
        start = max(0, end - overlap)

    return chunks


async def retrieve_relevant_sections(
    content: str, document_name: str, max_chars: int = 12000
) -> str:
    if not content or not content.strip():
        return ""
    if len(content) <= max_chars:
        return content

    chunks = chunk_text(content, chunk_size=900, overlap=150, max_chunks=80)
    if not chunks:
        return content[:max_chars]

    import faiss
    import numpy as np

    embedder = get_embedder()
    chunk_vectors = embedder.encode(
        chunks, convert_to_numpy=True, normalize_embeddings=True
    )
    chunk_vectors = np.asarray(chunk_vectors, dtype="float32")

    index = faiss.IndexFlatIP(chunk_vectors.shape[1])
    index.add(chunk_vectors)

    query = f"Key concepts and definitions for quiz questions from: {document_name}"
    query_vector = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    query_vector = np.asarray(query_vector, dtype="float32")

    top_k = min(8, len(chunks))
    _, indices = index.search(query_vector, top_k)
    selected_indices = sorted(set(indices[0].tolist()))
    context = "\n\n".join(chunks[index] for index in selected_indices)
    return context[:max_chars]


def clean_quiz_response(raw: str) -> str:
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()
