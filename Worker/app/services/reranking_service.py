from sentence_transformers import CrossEncoder


class RerankingService:

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
    ):

        self.model = CrossEncoder(
            model_name
        )

    # =========================================================
    # RERANK
    # =========================================================

    def rerank(
        self,
        query: str,
        candidates: list,
        top_k: int,
    ) -> list:

        if not candidates:
            return []

        pairs = [
            (
                query,
                candidate.text,
            )
            for candidate in candidates
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = sorted(
            zip(candidates, scores),
            key=lambda x: float(x[1]),
            reverse=True,
        )

        return ranked[:top_k]