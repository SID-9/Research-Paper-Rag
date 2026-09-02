from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal

from app.schemas.retrieval import (
    RetrievalRequest,
    RetrievalResult,
)

from app.services.embedding_service import (
    EmbeddingService,
)

from app.services.retrieval_service import (
    RetrievalService,
)

from app.services.reranking_service import(
    RerankingService
)


router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"],
)


# =========================================================
# Dependencies
# =========================================================

_embedding_service = EmbeddingService()
_reranking_service = RerankingService()


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


def get_retrieval_service():

    return RetrievalService(
        embedding_service=_embedding_service,
        reranking_service=_reranking_service
    )


# =========================================================
# SEARCH
# =========================================================

@router.post(
    "/search",
    response_model=list[RetrievalResult],
)
def search(
    request: RetrievalRequest,
    db: Session = Depends(get_db),
    retrieval_service: RetrievalService = Depends(
        get_retrieval_service
    ),
):

    return retrieval_service.search(
        db=db,
        request=request,
    )