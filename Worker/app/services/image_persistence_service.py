from sqlalchemy.orm import Session

from app.models.chunk import Chunk as ChunkModel
from app.models.image import Image
from app.repositories.image_repository import ImageRepository
from app.schemas.chunk import Chunk as ChunkSchema


class ImagePersistenceService:

    def persist_images(
        self,
        db: Session,
        chunk_schemas: list[ChunkSchema],
        chunk_models: list[ChunkModel],
    ) -> list[Image]:

        if not chunk_schemas:
            return []

        images: list[Image] = []

        # -----------------------------------------------------
        # The order of chunk_schemas and chunk_models is
        # preserved by ChunkPersistenceService.
        # -----------------------------------------------------

        for schema, model in zip(
            chunk_schemas,
            chunk_models,
        ):

            if not schema.image_paths:
                continue

            for image_path in schema.image_paths:

                image = Image(
                    chunk_id=model.chunk_id,
                    document_id=model.document_id,
                    page_number=model.page_number,
                    image_path=image_path,
                )

                images.append(image)

        return ImageRepository.create_many(
            db,
            images,
        )