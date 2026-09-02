from pydantic import BaseModel

class DocumentProcessingJob(BaseModel):
    documentId: int

    userId: int

    filePath: str

    originalFilename: str

    storedFilename: str
    
    
    

