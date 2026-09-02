from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BlockType(str, Enum):
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    IMAGE = "image"
    TABLE = "table"
    LIST = "list"
    CODE = "code"
    BLOCKQUOTE = "blockquote"
    HORIZONTAL_RULE = "horizontal_rule"
    PAGE_MARKER = "page_marker"
    OTHER = "other"


class MarkdownBlock(BaseModel):
    """
    Represents one structural block extracted from cleaned Markdown.

    This is NOT a final RAG chunk.

    It is a structural unit that later stages will use to
    construct semantically meaningful chunks.
    """

    block_index: int

    block_type: BlockType

    text: str = ""

    # ---------------------------------------------------------
    # Heading information
    # ---------------------------------------------------------

    heading_level: Optional[int] = None

    heading_text: Optional[str] = None

    # The heading level originally produced by Marker.
    # Useful for debugging, but NOT trusted for hierarchy.
    marker_heading_level: Optional[int] = None

    # Example:
    #
    # "3"
    # "3.1"
    # "3.2.1"
    #
    heading_number: Optional[str] = None

    # ---------------------------------------------------------
    # Image information
    # ---------------------------------------------------------

    image_path: Optional[str] = None

    image_alt_text: Optional[str] = None

    # ---------------------------------------------------------
    # Page information
    # ---------------------------------------------------------

    page_number: Optional[int] = None


class ParsedDocument(BaseModel):
    """
    Structural representation of a complete cleaned Markdown document.
    """

    document_id: int

    stored_filename: str

    markdown_path: str

    blocks: list[MarkdownBlock] = Field(
        default_factory=list
    )

    total_blocks: int = 0