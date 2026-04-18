from pydantic import BaseModel


class PlagiarismCheckRequest(BaseModel):
    content: str
