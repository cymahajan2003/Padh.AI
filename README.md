# Padh.AI – AI-Powered Academic Resource Hub (RAG-Based Learning Assistant)

Padh.AI is an AI-powered academic learning platform that helps students transform unstructured academic resources into structured, personalized, and interactive study material.

The system allows students to upload academic documents such as PDFs, notes, and study materials, and then uses a **Retrieval-Augmented Generation (RAG)** pipeline to generate meaningful learning outputs such as:

- Smart Summaries
- Concept Explanations
- Previous Year Question (PYQ)-style Questions
- Interactive Quizzes
- Personalized Academic Assistance

The core idea behind Padh.AI is to build a practical, scalable academic assistant that can understand student-provided content and generate useful outputs **grounded in the uploaded documents**, rather than relying only on generic LLM responses.

---

## 🚀 Problem Statement

Students often face major challenges while studying from academic documents:

- Large PDFs and notes are difficult to revise quickly
- Important concepts are buried inside lengthy material
- Students struggle to identify exam-relevant questions
- Generic AI tools often give answers not grounded in the actual study material
- Manual preparation of summaries, PYQs, and quizzes is time-consuming

Padh.AI solves this by using a **RAG-based document understanding pipeline** that extracts relevant content from uploaded documents and generates academically useful outputs based on the retrieved context.

---

## 🎯 Project Objectives

- Build an academic AI assistant that works on student-uploaded documents
- Generate **context-aware** outputs grounded in uploaded study material
- Reduce time spent on manual summarization and question preparation
- Improve self-assessment using generated quizzes
- Provide a scalable architecture using **RAG instead of training a custom LLM**
- Make the solution practical for college-level deployment and future productization

---
## 🏗️ High-Level System Architecture

Padh.AI follows a modular pipeline:

1. **Document Upload**
2. **Text Extraction / OCR**
3. **Preprocessing & Cleaning**
4. **Chunking**
5. **Embedding Generation**
6. **Vector Storage**
7. **Similarity Retrieval**
8. **Prompt Construction with Retrieved Context**
9. **LLM Response Generation**
10. **Feature Output Layer**
   - Summary
   - PYQs
   - Quiz
   - Concept Q&A

This architecture makes the platform scalable and modular.


## 🧠 Simple Flow Representation

```text
Upload Document
   ↓
Text Extraction / OCR
   ↓
Preprocessing & Cleaning
   ↓
Chunking
   ↓
Embedding Generation
   ↓
Vector Storage
   ↓
User Request (Summary / PYQ / Quiz / Q&A)
   ↓
Similarity Retrieval
   ↓
Prompt Construction
   ↓
LLM Response Generation
   ↓
Frontend Output
```

---

## 🛠️Tools / Technologies

This project can be implemented using the following technologies:

### Frontend

- **React.js** – for building the user interface
- **Vite** – for fast frontend development
- **CSS / Tailwind CSS** – for styling the application

### Backend

- **Python**
- **FastAPI** – for creating backend APIs

### Document Processing

- **PyMuPDF / PyPDF2 / pdfplumber** – for extracting text from PDF files
- **Tesseract OCR / EasyOCR** – for extracting text from scanned or image-based documents

### RAG / AI Processing

- **LangChain / LlamaIndex** – optional frameworks for managing the RAG pipeline
- **Sentence Transformers / Embedding APIs** – for converting text chunks into embeddings
- **FAISS / ChromaDB** – for storing and retrieving document embeddings
- **Gemini / OpenAI / Groq** – for generating summaries, PYQs, quizzes, and explanations

### Storage

- **Supabase** – for user authentication, storing progress, and dashboard data
- **PostgreSQL** – for storing metadata and analytics


## ▶️ How to Run the Project

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend will run on:

```bash
http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on:

```bash
http://localhost:5173
```
---

## 🏁 Conclusion

Padh.AI is a practical RAG-based academic assistant that helps students turn static study material into interactive learning resources.

By combining document upload, text extraction, retrieval, and AI generation, the platform can provide:

- Summaries
- Concept explanations
- PYQs
- Quizzes
- Future personalized learning support

This makes studying more efficient, interactive, and student-friendly.

---

## 📄 License

This project is for academic and educational purposes.
