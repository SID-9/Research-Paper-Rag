from sqlalchemy import BigInteger,Column,Enum,String

from app.core.database import Base
import enum

class DocumentStatus(enum.Enum):
    UPLOADED = "UPLOADED"
    QUEUED = "QUEUED"
    PARSING = "PARSING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    READY = "READY"
    FAILED = "FAILED"

class Document(Base):
    
    __tablename__="documents"
    
    id = Column(BigInteger, primary_key=True)
    
    status = Column(
        Enum(DocumentStatus),
        nullable=False
    )


