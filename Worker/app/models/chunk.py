from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Text,
    ForeignKey,
    JSON
)

from pgvector.sqlalchemy import Vector
from app.core.database import Base
from app.core.config import settings

class Chunk(Base):
    
    __tablename__ = "chunks"
    
    # PK in table
    chunk_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )
    
    # document relationship
    document_id = Column(
        BigInteger,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True
    )
    
    # original ordering inside the document
    
    chunk_index = Column(
        Integer,
        nullable=False,
    )
    
    # page informatin
    page_number = Column(
        Integer,
        nullable=True
    )

    # heading hierarchy
    heading_path = Column(
        JSON,
        nullable=False,
    )


    #chunk text
    
    text = Column(
        Text,
        nullable=False
    )
    
    # embedding : for now we will keep it nullable since we are not generating
#     We're deliberately not specifying the dimension yet.
# Once we select our embedding model, for example a 768-dimensional model, we'll change this to something like:Vector(768)
    embedding = Column(
        Vector(settings.EMBEDDING_DIMENSION),
        nullable=True
    )