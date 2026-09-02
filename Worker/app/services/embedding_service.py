from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    """
    Generates embeddings using a local Sentence Transformer model.

    The model is loaded once when the service is created and then
    reused for all embedding requests.

    Current model:
        BAAI/bge-base-en-v1.5

    Dimension:
        768
    """

    def __init__(self):

        print(
            f"Loading embedding model: "
            f"{settings.EMBEDDING_MODEL}"
        )

        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        print(
            "Embedding model loaded successfully"
        )

    # =========================================================
    # Single text
    # =========================================================

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    # =========================================================
    # Multiple texts
    # =========================================================

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        for text in texts:

            if not text or not text.strip():
                raise ValueError(
                    "Cannot generate embedding for empty text."
                )

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()
    

#----------------------------------
    
"""
Why load the model in __init__?

Because we do not want:

chunk 1 → load model
chunk 2 → load model
chunk 3 → load model
...

That would be horrible.

Instead:

FastAPI worker starts
       ↓
Load model ONCE
       ↓
chunk 1
chunk 2
chunk 3
chunk 4
...
"""