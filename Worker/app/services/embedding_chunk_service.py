from app.schemas.chunk import Chunk
from app.services.embedding_service import EmbeddingService


class ChunkEmbeddingService:
    """
    Adds embeddings to Chunk objects.

    This service connects the application's Chunk schema
    with the generic EmbeddingService.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
    ):

        self.embedding_service = (
            embedding_service
        )

    # =========================================================
    # Embed chunks
    # =========================================================

    def embed_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[list[float]]:

        if not chunks:
            return []

        texts = [
            chunk.text
            for chunk in chunks
        ]

        return self.embedding_service.embed_texts(
            texts
        )