from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus

class DocumentService:
    
    @staticmethod
    def update_status(
        db: Session,
        document_id: int,
        status: DocumentStatus
    ) -> None:
        
        document = db.get(Document,document_id)
        
        if document is None:
            raise Exception(
                f"Document {document_id} not found"
            )
        
        document.status = status
        db.commit()


