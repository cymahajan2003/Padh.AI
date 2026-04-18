import json

from fastapi import APIRouter, HTTPException

from schemas.quiz import QuizRequest
from services.groq import groq_chat
from services.quiz import QUIZ_SYSTEM_PROMPT, clean_quiz_response, retrieve_relevant_sections

router = APIRouter()


@router.post("/api/quiz")
async def quiz(req: QuizRequest):
    if req.topic and req.topic.strip():
        prompt = (
            "Generate 5 conceptual multiple-choice quiz questions about the topic: "
            f'"{req.topic.strip()}". Make them educational, testing understanding of '
            "key concepts, and progressively challenging."
        )
        raw = await groq_chat(
            [
                {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
    elif req.content and req.content.strip():
        name = req.document_name or "Document"
        content = req.content[:15000] if len(req.content) > 15000 else req.content
        retrieved = await retrieve_relevant_sections(content, name, max_chars=10000)
        context = retrieved[:6000] if len(retrieved) > 6000 else retrieved
        prompt = (
            "Generate 5 multiple-choice quiz questions based ONLY on the following "
            f'retrieved sections from the document "{name}". Questions must be directly '
            f"related to this material:\n\n{context}"
        )
        raw = await groq_chat(
            [
                {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
    else:
        raise HTTPException(status_code=400, detail="Provide either topic or content")

    try:
        parsed = json.loads(clean_quiz_response(raw))
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=502, detail=f"Invalid quiz response from AI: {exc}")

    if not isinstance(parsed, list) or not parsed:
        raise HTTPException(status_code=502, detail="Invalid quiz format received")

    questions = []
    for index, question in enumerate(parsed[:5]):
        questions.append(
            {
                "id": question.get("id", index + 1),
                "question": question.get("question", ""),
                "options": question.get("options", []),
                "correct": (
                    int(question.get("correct", 0))
                    if isinstance(question.get("correct"), (int, float))
                    else 0
                ),
            }
        )
    return {"questions": questions}
