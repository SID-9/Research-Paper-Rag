from pathlib import Path
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.chunk import Chunk
from app.schemas.parsed_document import ParsedDocument
from app.schemas.semantic_block import SemanticBlock


class ProcessingContext(BaseModel):

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    # =========================================================
    # Workspace
    # =========================================================

    workspace: Optional[Path] = None

    # =========================================================
    # Document information
    # =========================================================

    document_id: int

    user_id: int

    stored_filename: str

    original_filename: str

    file_path: Path

    # =========================================================
    # Marker output
    # =========================================================

    marker_output_directory: Optional[Path] = None

    markdown_file: Optional[Path] = None

    images_directory: Optional[Path] = None

    # =========================================================
    # Parsed representation
    # =========================================================

    parsed_document: Optional[
        ParsedDocument
    ] = None

    cleaned_markdown_file: Optional[Path] = None

    json_file: Optional[Path] = None

    processing_error: Optional[str] = None

    # =========================================================
    # Semantic representation
    # =========================================================

    semantic_blocks: list[
        SemanticBlock
    ] = Field(
        default_factory=list
    )

    # =========================================================
    # Final chunks
    # =========================================================

    chunks: list[Chunk] = Field(
        default_factory=list
    )



#=============================
# from pathlib import Path
# from typing import Optional

# from pydantic import BaseModel

# from app.schemas.parsed_document import ParsedDocument

# class ProcessingContext(BaseModel):
    
#     # job information
    
#     document_id: int 
#     user_id: int 
    
#     original_filename: str 
#     stored_filename: str 
#     file_path: str
    
#     #workspace
    
#     workspace: Optional[Path] = None
    
#     marker_output_directory: Optional[Path] = None

#     images_directory: Optional[Path] = None

#     markdown_file: Optional[Path] = None
    
#     parsed_document: Optional[ParsedDocument] = None
    
#     cleaned_markdown_file: Optional[Path] =  None

#     json_file: Optional[Path] = None
    
#     processing_error: Optional[str] = None


