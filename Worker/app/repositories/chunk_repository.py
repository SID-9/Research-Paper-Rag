from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk


class ChunkRepository:

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def create(
        db: Session,
        chunk: Chunk,
    ) -> Chunk:

        db.add(chunk)

        db.flush()

        return chunk

    # =========================================================
    # CREATE MANY
    # =========================================================

    @staticmethod
    def create_many(
        db: Session,
        chunks: list[Chunk],
    ) -> list[Chunk]:

        if not chunks:
            return []

        db.add_all(chunks)

        db.flush()

        return chunks

    # =========================================================
    # VECTOR SEARCH
    # =========================================================

    @staticmethod
    def similarity_search(
        db: Session,
        query_embedding: list[float],
        document_id: int | None = None,
        top_k: int = 10,
    ) -> list[tuple[Chunk, float]]:

        similarity = (
            1 - Chunk.embedding.cosine_distance(
                query_embedding
            )
        ).label("similarity")

        statement = (
            select(
                Chunk,
                similarity,
            )
            .where(
                Chunk.embedding.is_not(None)
            )
        )

        # -----------------------------------------------------
        # Optional document filtering
        #
        # If document_id is provided:
        #
        # search only that research paper.
        # -----------------------------------------------------

        if document_id is not None:

            statement = statement.where(
                Chunk.document_id == document_id
            )

        statement = (
            statement
            .order_by(
                similarity.desc()
            )
            .limit(top_k)
        )

        results = db.execute(
            statement
        ).all()

        return [
            (chunk, float(score))
            for chunk, score in results
        ]









# from sqlalchemy.orm import Session
# from app.models.chunk import Chunk

# class ChunkRepository:
    
#     @staticmethod
#     def create(
#         db: Session,
#         chunk: Chunk
#     ) -> Chunk:
        
#         db.add(chunk)
#         db.flush()
        
#         return chunk
    
#     @staticmethod
#     def create_many(
#         db: Session,
#         chunks: list[Chunk],
#     )-> list[Chunk]:
        
#         if not chunks:
#             return []
        
#         db.add_all(chunks)
#         db.flush()
        
#         return chunks











# """ 
# Why flush() instead of commit()?

# This is important.

# The repository should not decide the transaction boundary.

# The service should.

# flush() sends the INSERT to PostgreSQL so generated IDs become available, but the transaction remains open.

# That means we can do:

# create chunks
#       ↓
# flush
#       ↓
# get chunk IDs
#       ↓
# create images
#       ↓
# commit everything together

# If something fails:

# ROLLBACK

# and we don't end up with half a document persisted.

# That's a much better production pattern.

# """