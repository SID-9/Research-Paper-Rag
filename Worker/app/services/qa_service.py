from sqlalchemy.orm import Session

from app.schemas.qa import (
    QARequest,
    QAResponse,
    QASource,
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


class QAService:

    def __init__(
        self,
        retrieval_service: RetrievalService,
        context_builder: ContextBuilderService,
        llm_service: LLMService,
    ):

        self.retrieval_service = (
            retrieval_service
        )

        self.context_builder = (
            context_builder
        )

        self.llm_service = (
            llm_service
        )

    # =========================================================
    # ASK
    # =========================================================

    def ask(
        self,
        db: Session,
        request: QARequest,
    ) -> QAResponse:

        # -----------------------------------------------------
        # 1. Retrieve relevant chunks
        # -----------------------------------------------------

        retrieval_request = (
            self._build_retrieval_request(
                request
            )
        )

        retrieval_results = (
            self.retrieval_service.search(
                db=db,
                request=retrieval_request,
            )
        )

        # -----------------------------------------------------
        # 2. Handle no retrieval results
        # -----------------------------------------------------

        if not retrieval_results:

            return QAResponse(
                answer=(
                    "I could not find enough "
                    "information in the provided "
                    "document to answer this question."
                ),
                sources=[],
            )

        # -----------------------------------------------------
        # 3. Build context
        # -----------------------------------------------------

        context = (
            self.context_builder.build_context(
                retrieval_results
            )
        )

        # -----------------------------------------------------
        # 4. Build grounded prompt
        # -----------------------------------------------------

        prompt = self._build_prompt(
            question=request.query,
            context=context,
        )

        # -----------------------------------------------------
        # 5. Generate answer
        # -----------------------------------------------------

        answer = (
            self.llm_service.generate(
                prompt
            )
        )

        # -----------------------------------------------------
        # 6. Build source metadata
        # -----------------------------------------------------

        sources = [

            QASource(

                chunk_id=result.chunk_id,

                document_id=result.document_id,

                chunk_index=result.chunk_index,

                page_number=result.page_number,

                heading_path=result.heading_path,

                vector_similarity=result.vector_similarity,

                rerank_score=result.rerank_score,

            )

            for result in retrieval_results
        ]

        # -----------------------------------------------------
        # 7. Return final response
        # -----------------------------------------------------

        return QAResponse(
            answer=answer,
            sources=sources,
        )

    # =========================================================
    # RETRIEVAL REQUEST
    # =========================================================

    @staticmethod
    def _build_retrieval_request(
        request: QARequest,
    ):

        from app.schemas.retrieval import (
            RetrievalRequest,
        )

        return RetrievalRequest(

            query=request.query,

            document_id=request.document_id,

            # -------------------------------------------------
            # We retrieve more candidates than we ultimately
            # need so the reranker has enough candidates.
            # -------------------------------------------------

            top_k=10,
        )

    # =========================================================
    # PROMPT
    # =========================================================

    @staticmethod
    def _build_prompt(
        question: str,
        context: str,
    ) -> str:

        return f"""
Answer the user's question using ONLY the
information contained in the context below.

Rules:

1. Do not use outside knowledge.
2. Do not invent or assume information.
3. If the context does not contain enough
   information to answer the question,
   clearly state that the answer cannot be
   determined from the provided document.
4. Give a concise but sufficiently detailed
   answer.
5. When useful, explain the answer using the
   terminology used in the research paper.

Context:

{context}

---

Question:

{question}
""".strip()