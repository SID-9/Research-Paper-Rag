from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    ForeignKey,
)

from app.core.database import Base


class Image(Base):

    __tablename__ = "images"

    # ---------------------------------------------------------
    # Primary Key
    # ---------------------------------------------------------

    image_id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    # ---------------------------------------------------------
    # Chunk relationship
    # ---------------------------------------------------------

    chunk_id = Column(
        BigInteger,
        ForeignKey(
            "chunks.chunk_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------
    # Document relationship
    # ---------------------------------------------------------

    document_id = Column(
        BigInteger,
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------
    # Page information
    # ---------------------------------------------------------

    page_number = Column(
        Integer,
        nullable=True,
    )

    # ---------------------------------------------------------
    # Image path
    #
    # Example:
    #
    # _page_3_Diagram_0.jpeg
    # ---------------------------------------------------------

    image_path = Column(
        String,
        nullable=False,
    )