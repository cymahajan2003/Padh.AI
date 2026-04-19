import os
import json
from dotenv import load_dotenv
from google import genai
import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("MODEL")

# ==============================
# 🔹 API LOGIC (LLM ONLY)
# ==============================

# ------------------ SAFE CALL ------------------
def ask(prompt):
    try:
        res = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return res.text
    except Exception as e:
        return str(e)

# ------------------ CLEAN RESPONSE ------------------
def clean_json(res):
    return res.replace("```json", "").replace("```", "").strip()

# ------------------ GENERATE QUESTIONS ------------------
def generate_questions(topic):
    prompt = f"""
Return ONLY JSON.

{{
  "questions": ["Q1","Q2","Q3","Q4","Q5"]
}}

Generate conceptual questions on topic: {topic}
"""
    res = ask(prompt)
    res = clean_json(res)

    try:
        return json.loads(res)
    except:
        return {"questions": res.split("\n")}

# ------------------ EVALUATE ANSWER ------------------
def evaluate_answer(question, answer):
    prompt = f"""
Return ONLY JSON:

{{
  "correctness": "Correct | Partially Correct | Incorrect",
  "percentage": number,
  "wrong": "what is missing",
  "correct_answer": "best answer",
  "feedback": "short feedback"
}}

Question: {question}
Answer: {answer}
"""
    res = ask(prompt)
    res = clean_json(res)

    try:
        return json.loads(res)
    except:
        return {
            "correctness": "Error",
            "percentage": 0,
            "wrong": "Parsing failed",
            "correct_answer": "",
            "feedback": res
        }

# ------------------ REWRITE ------------------
def rewrite_answer(answer):
    prompt = f"Improve this answer:\n{answer}"
    res = ask(prompt)
    return {"rewritten": res}


# ==============================
# 🔹 RAG LOGIC (PDF BASED)
# ==============================

model = SentenceTransformer('all-MiniLM-L6-v2')
documents = []
index = None

# ------------------ Text Extraction ------------------
def extract_text(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# ------------------ Chunking ------------------
def chunk_text(text, chunk_size=300):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

# ------------------ Embedding & Vector DB ------------------
def create_vector_store(chunks):
    global index, documents
    documents = chunks

    embeddings = model.encode(chunks)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))

# ------------------ Retrieve Chunks ------------------
def retrieve_chunks(query, top_k=3):
    query_vec = model.encode([query])
    distances, indices = index.search(np.array(query_vec), top_k)
    return [documents[i] for i in indices[0]]

# ------------------ Question Generation From PDF ------------------
def generate_questions_from_pdf(file_path):
    text = extract_text(file_path)
    chunks = chunk_text(text)

    create_vector_store(chunks)

    retrieved_chunks = retrieve_chunks("generate conceptual questions")
    context = "\n".join(retrieved_chunks)

    prompt = f"""
Return ONLY JSON.

{{
  "questions": ["Q1","Q2","Q3","Q4","Q5"]
}}

Generate conceptual questions based on the following content:
{context}
"""

    res = ask(prompt)
    res = clean_json(res)

    try:
        return json.loads(res)
    except:
        return {"questions": res.split("\n")}
    
