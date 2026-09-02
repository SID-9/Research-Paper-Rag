from typing import Optional

from pydantic import BaseModel, Field


class QARequest(BaseModel):

    query: str = Field(
        min_length=1,
        description="User's natural language question.",
    )

    document_id: Optional[int] = Field(
        default=None,
        description=(
            "Optional document ID. "
            "If provided, the question is restricted "
            "to that document."
        ),
    )


class QASource(BaseModel):

    chunk_id: int

    document_id: int

    chunk_index: int

    page_number: Optional[int]

    heading_path: list[str]

    vector_similarity: float

    rerank_score: float


class QAResponse(BaseModel):

    answer: str

    sources: list[QASource]