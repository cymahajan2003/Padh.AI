from pydantic import BaseModel


class SummaryRequest(BaseModel):
    document_name: str
    content: str
