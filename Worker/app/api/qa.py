from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.schemas.qa import (
    QARequest,
    QAResponse,
)

from app.services.embedding_service import (
    EmbeddingService,
)

from app.services.retrieval_service import (
    RetrievalService,
)

from app.services.context_builder_service import (
    ContextBuilderService,
)

from app.services.llm_service import (
    LLMService,
)

from app.services.qa_service import (
    QAService,
)
from app.services.reranking_service import(
    RerankingService
)


router = APIRouter(
    prefix="/qa",
    tags=["Q&A"],
)


# =========================================================
# Shared services
# =========================================================

_embedding_service = EmbeddingService()
_reranking_service = RerankingService()

_retrieval_service = RetrievalService(
    embedding_service=_embedding_service,
    reranking_service=_reranking_service
)

_context_builder_service = (
    ContextBuilderService()
)

_llm_service = LLMService()


# =========================================================
# Database dependency
# =========================================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# =========================================================
# QA SERVICE DEPENDENCY
# =========================================================

def get_qa_service():

    return QAService(

        retrieval_service=(
            _retrieval_service
        ),

        context_builder=(
            _context_builder_service
        ),

        llm_service=(
            _llm_service
        ),
    )


# =========================================================
# ASK QUESTION
# =========================================================

@router.post(
    "/ask",
    response_model=QAResponse,
)
def ask_question(

    request: QARequest,

    db: Session = Depends(
        get_db
    ),

    qa_service: QAService = Depends(
        get_qa_service
    ),
):

    return qa_service.ask(
        db=db,
        request=request,
    )