from services.groqService import groq_chat

SUMMARY_SYSTEM = """You are an expert document summarizer for a student learning platform called Padh.AI. \
Generate a well-structured, comprehensive summary of the provided document. \
Format your response using this exact structure:

## Summary
A 2-4 sentence summary of what the document is about.

## Key Points
- Point 1
- Point 2
- Point 3
(list all important points)

Keep the language clear, concise, and student-friendly. Do NOT include any other sections."""


async def summarize_document(document_name: str, content: str) -> str:
    """Return a markdown-formatted summary for the given document content."""
    if len(content) > 12000:
        content = content[:12000] + "\n\n[Content truncated for processing...]"

    user = f'Please summarize the following document titled "{document_name}":\n\n{content}'
    return await groq_chat(
        [
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=2048,
    )
