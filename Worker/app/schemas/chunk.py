
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.semantic_block import (
    SemanticBlockType,
)


class Chunk(BaseModel):
    """
    Represents a final semantic RAG chunk.

    This object is created before embedding and database persistence.
    """

    document_id: int

    chunk_index: int

    page_number: Optional[int] = None

    heading_path: list[str] = Field(
        default_factory=list
    )

    text: str

    block_types: list[SemanticBlockType] = Field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Image information
    # ---------------------------------------------------------

    image_paths: list[str] = Field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Future fields
    # ---------------------------------------------------------

    # embedding will be added later.





# images issue old version ========================

# from typing import Optional

# from pydantic import BaseModel, Field

# from app.schemas.semantic_block import (
#     SemanticBlockType,
# )


# class Chunk(BaseModel):
#     """
#     Represents a final semantic RAG chunk.

#     This object is created before embedding and database persistence.
#     """

#     document_id: int

#     chunk_index: int

#     page_number: Optional[int] = None

#     heading_path: list[str] = Field(
#         default_factory=list
#     )

#     text: str

#     block_types: list[SemanticBlockType] = Field(
#         default_factory=list
#     )
    
#     # ---------------------------------------------------------
#     # Future fields
#     # ---------------------------------------------------------

#     # embedding will be added later.

#     # We deliberately do not put:
#     #
#     # embedding: list[float]
#     #
#     # here yet because embedding generation is another stage.