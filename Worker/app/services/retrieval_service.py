from sqlalchemy.orm import Session

from app.repositories.chunk_repository import (
    ChunkRepository,
)

from app.schemas.retrieval import (
    RetrievalRequest,
    RetrievalResult,
)

from app.services.embedding_service import (
    EmbeddingService,
)

from app.services.reranking_service import (
    RerankingService,
)


class RetrievalService:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        reranking_service: RerankingService,
    ):

        self.embedding_service = (
            embedding_service
        )

        self.reranking_service = (
            reranking_service
        )

    # =========================================================
    # SEARCH
    # =========================================================

    def search(
        self,
        db: Session,
        request: RetrievalRequest,
    ) -> list[RetrievalResult]:

        # -----------------------------------------------------
        # 1. Query embedding
        # -----------------------------------------------------

        query_embedding = (
            self.embedding_service.embed_text(
                request.query
            )
        )

        # -----------------------------------------------------
        # 2. Candidate generation
        # -----------------------------------------------------

        candidate_k = min(
            request.top_k * 4,
            50,
        )

        candidates = (
            ChunkRepository.similarity_search(
                db=db,
                query_embedding=query_embedding,
                document_id=request.document_id,
                top_k=candidate_k,
            )
        )

        if not candidates:
            return []

        # -----------------------------------------------------
        # 3. Reranking
        # -----------------------------------------------------

        ranked_candidates = (
            self.reranking_service.rerank(
                query=request.query,
                candidates=[
                    chunk
                    for chunk, _ in candidates
                ],
                top_k=request.top_k,
            )
        )

        # -----------------------------------------------------
        # 4. Convert to API response
        # -----------------------------------------------------

        return [
            RetrievalResult(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                heading_path=chunk.heading_path,
                text=chunk.text,
                vector_similarity=(
                    self._get_vector_similarity(
                        chunk,
                        candidates,
                    )
                ),
                rerank_score=float(
                    rerank_score
                ),
            )
            for chunk, rerank_score
            in ranked_candidates
        ]

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _get_vector_similarity(
        chunk,
        candidates,
    ):

        for candidate, similarity in candidates:

            if candidate.chunk_id == chunk.chunk_id:
                return float(similarity)

        return 0.0



# ================ without reranking version ==================

# from sqlalchemy.orm import Session

# from app.repositories.chunk_repository import (
#     ChunkRepository,
# )

# from app.schemas.retrieval import (
#     RetrievalRequest,
#     RetrievalResult,
# )

# from app.services.embedding_service import (
#     EmbeddingService,
# )


# class RetrievalService:
#     """
#     Performs semantic vector retrieval.

#     Current retrieval pipeline:

#         Query
#           ↓
#         Query embedding
#           ↓
#         pgvector cosine similarity
#           ↓
#         Top-K chunks
#     """

#     def __init__(
#         self,
#         embedding_service: EmbeddingService,
#     ):

#         self.embedding_service = (
#             embedding_service
#         )

#     # =========================================================
#     # SEARCH
#     # =========================================================

#     def search(
#         self,
#         db: Session,
#         request: RetrievalRequest,
#     ) -> list[RetrievalResult]:

#         # -----------------------------------------------------
#         # Generate query embedding
#         # -----------------------------------------------------

#         query_embedding = (
#             self.embedding_service.embed_text(
#                 request.query
#             )
#         )

#         # -----------------------------------------------------
#         # Vector search
#         # -----------------------------------------------------

#         results = (
#             ChunkRepository.similarity_search(
#                 db=db,
#                 query_embedding=query_embedding,
#                 document_id=request.document_id,
#                 top_k=request.top_k,
#             )
#         )

#         # -----------------------------------------------------
#         # Convert DB results into API schemas
#         # -----------------------------------------------------

#         return [

#             RetrievalResult(

#                 chunk_id=chunk.chunk_id,

#                 document_id=chunk.document_id,

#                 chunk_index=chunk.chunk_index,

#                 page_number=chunk.page_number,

#                 heading_path=chunk.heading_path,

#                 text=chunk.text,

#                 similarity=similarity,
#             )

#             for chunk, similarity in results
#         ]