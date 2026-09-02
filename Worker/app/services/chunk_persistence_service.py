from sqlalchemy.orm import Session

from app.models.chunk import Chunk as ChunkModel

from app.repositories.chunk_repository import (
    ChunkRepository,
)

from app.schemas.chunk import Chunk as ChunkSchema


class ChunkPersistenceService:

    def persist_chunks(
        self,
        db: Session,
        chunks: list[ChunkSchema],
        embeddings: list[list[float]],
    ) -> list[ChunkModel]:

        if not chunks:
            return []

        if len(chunks) != len(embeddings):

            raise ValueError(
                "Number of chunks and embeddings "
                "must be identical."
            )

        chunk_models: list[ChunkModel] = []

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            chunk_model = ChunkModel(

                document_id=chunk.document_id,

                chunk_index=chunk.chunk_index,

                page_number=chunk.page_number,

                heading_path=chunk.heading_path,

                text=chunk.text,

                embedding=embedding,
            )

            chunk_models.append(
                chunk_model
            )

        return ChunkRepository.create_many(
            db,
            chunk_models,
        )




#========== without embeddings one==================

# from sqlalchemy.orm import Session

# from app.models.chunk import Chunk as ChunkModel
# from app.repositories.chunk_repository import ChunkRepository
# from app.schemas.chunk import Chunk as ChunkSchema


# class ChunkPersistenceService:

#     def persist_chunks(
#         self,
#         db: Session,
#         chunks: list[ChunkSchema],
#     ) -> list[ChunkModel]:

#         if not chunks:
#             return []

#         chunk_models: list[ChunkModel] = []

#         for chunk in chunks:

#             chunk_model = ChunkModel(
#                 document_id=chunk.document_id,
#                 chunk_index=chunk.chunk_index,
#                 page_number=chunk.page_number,
#                 heading_path=chunk.heading_path,
#                 text=chunk.text,
#             )

#             chunk_models.append(
#                 chunk_model
#             )

#         return ChunkRepository.create_many(
#             db,
#             chunk_models,
#         )