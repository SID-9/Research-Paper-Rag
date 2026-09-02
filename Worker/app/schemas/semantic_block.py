from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SemanticBlockType(str, Enum):
    """
    Represents the semantic role of a block inside a research paper.
    """

    # TEXT = "text"
    PARAGRAPH="paragraph"
    TABLE = "table"
    IMAGE = "image"
    LIST = "list"
    CODE = "code"
    BLOCKQUOTE = "blockquote"


class SemanticBlock(BaseModel):
    """
    Represents content associated with a particular heading path.

    This is still NOT the final RAG chunk.

    A semantic block is an intermediate representation that
    groups related content before chunk construction.
    """

    block_index: int

    block_type: SemanticBlockType

    text: str = ""

    # ---------------------------------------------------------
    # Heading hierarchy
    # ---------------------------------------------------------

    heading_path: list[str] = Field(
        default_factory=list
    )

    # Example:
    #
    # [
    #     "3 Method",
    #     "3.2 Architecture",
    #     "3.2.1 Encoder"
    # ]

    # ---------------------------------------------------------
    # Page information
    # ---------------------------------------------------------

    page_number: Optional[int] = None

    # ---------------------------------------------------------
    # Image information
    # ---------------------------------------------------------

    image_path: Optional[str] = None

    image_alt_text: Optional[str] = None