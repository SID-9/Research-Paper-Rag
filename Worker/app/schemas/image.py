from typing import Optional

from pydantic import BaseModel


class ImageCreate(BaseModel):

    chunk_id: int

    document_id: int

    page_number: Optional[int] = None

    image_path: str