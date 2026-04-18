from typing import Optional

from pydantic import BaseModel


class QuizRequest(BaseModel):
    topic: Optional[str] = None
    document_name: Optional[str] = None
    content: Optional[str] = None
