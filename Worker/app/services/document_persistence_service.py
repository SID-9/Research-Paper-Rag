from sqlalchemy.orm import Session

from app.schemas.chunk import Chunk

from app.services.chunk_persistence_service import (
    ChunkPersistenceService,
)

from app.services.image_persistence_service import (
    ImagePersistenceService,
)


class DocumentPersistenceService:

    def __init__(self):

        self.chunk_service = (
            ChunkPersistenceService()
        )

        self.image_service = (
            ImagePersistenceService()
        )

    def persist(
        self,
        db: Session,
        chunks: list[Chunk],
        embeddings: list[list[float]],
    ):
        """
        Persist all processed document data
        inside one database transaction.

        Persistence flow:

            chunks + embeddings
                    ↓
            ChunkPersistenceService
                    ↓
                  flush
                    ↓
              chunk IDs available
                    ↓
            ImagePersistenceService
                    ↓
                  commit

        If anything fails, the entire transaction
        is rolled back.
        """

        if not chunks:
            return {
                "chunks": [],
                "images": [],
            }

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of embeddings must match "
                "number of chunks."
            )

        try:

            # =================================================
            # STEP 1
            # Persist chunks + embeddings
            # =================================================

            chunk_models = (
                self.chunk_service.persist_chunks(
                    db=db,
                    chunks=chunks,
                    embeddings=embeddings,
                )
            )

            # =================================================
            # STEP 2
            # Persist images
            #
            # ChunkPersistenceService uses flush(),
            # therefore chunk IDs already exist here.
            # =================================================

            image_models = (
                self.image_service.persist_images(
                    db=db,
                    chunk_schemas=chunks,
                    chunk_models=chunk_models,
                )
            )

            # =================================================
            # STEP 3
            # Commit entire document transaction
            # =================================================

            db.commit()

            return {
                "chunks": chunk_models,
                "images": image_models,
            }

        except Exception:

            db.rollback()

            raise





# ==================== without embeddings version ==================
# from sqlalchemy.orm import Session

# from app.schemas.chunk import Chunk

# from app.services.chunk_persistence_service import (
#     ChunkPersistenceService,
# )

# from app.services.image_persistence_service import (
#     ImagePersistenceService,
# )


# class DocumentPersistenceService:

#     def __init__(self):

#         self.chunk_service = (
#             ChunkPersistenceService()
#         )

#         self.image_service = (
#             ImagePersistenceService()
#         )

#     def persist(
#         self,
#         db: Session,
#         chunks: list[Chunk],
#     ):

#         if not chunks:
#             return {
#                 "chunks": [],
#                 "images": [],
#             }

#         try:

#             # -------------------------------------------------
#             # Persist chunks
#             # -------------------------------------------------

#             chunk_models = (
#                 self.chunk_service.persist_chunks(
#                     db,
#                     chunks,
#                 )
#             )

#             # -------------------------------------------------
#             # Persist images
#             #
#             # Chunk IDs now exist because repository.flush()
#             # was called.
#             # -------------------------------------------------

#             image_models = (
#                 self.image_service.persist_images(
#                     db,
#                     chunks,
#                     chunk_models,
#                 )
#             )

#             # -------------------------------------------------
#             # Commit entire document transaction
#             # -------------------------------------------------

#             db.commit()

#             return {
#                 "chunks": chunk_models,
#                 "images": image_models,
#             }

#         except Exception:

#             db.rollback()

#             raise