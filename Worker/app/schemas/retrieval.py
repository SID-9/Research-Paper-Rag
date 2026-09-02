from typing import Optional

from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):

    query: str = Field(
        min_length=1,
        description="User's natural language question.",
    )

    document_id: Optional[int] = Field(
        default=None,
        description=(
            "Optional document ID. "
            "If provided, retrieval is restricted "
            "to that document."
        ),
    )

    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
    )

class RetrievalResult(BaseModel):

    chunk_id: int

    document_id: int

    chunk_index: int

    page_number: Optional[int]

    heading_path: list[str]

    text: str

    vector_similarity: float

    rerank_score: float