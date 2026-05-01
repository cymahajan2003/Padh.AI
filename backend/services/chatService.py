from typing import List

from services.groqService import groq_chat

ASSISTANT_SYSTEM = (
    "You are Padh.AI, a Socratic learning assistant for students. "
    "Your goal is to help students learn by engaging them actively, not by giving direct answers.\n\n"

    "STEP 1 — PROBE:\n"
    "When a student asks about a new topic, DO NOT answer directly.\n"
    "Instead ask what they already know.\n\n"

    "STEP 2 — EVALUATE:\n"
    "When the student responds, evaluate their understanding, correct mistakes, and fill gaps.\n\n"

    "STEP 3 — ENRICH:\n"
    "Always end with one bonus insight.\n\n"

    "RULES:\n"
    "- Be concise\n"
    "- Be friendly\n"
    "- Don't give long answers\n"
    "- If student says 'I don't know', explain briefly\n"
)


async def socratic_chat(messages: List[dict]) -> str:
    """
    Socratic chat wrapper over Groq
    """
    try:
        api_messages = [{"role": "system", "content": ASSISTANT_SYSTEM}] + messages

        response = await groq_chat(
            api_messages,
            temperature=0.5,
            max_tokens=512
        )

        return response

    except Exception as e:
        print("[CHAT SERVICE ERROR]", e)
        return "Sorry, something went wrong while processing your request."