from sqlalchemy.orm import Session

from app.models.image import Image


class ImageRepository:

    @staticmethod
    def create_many(
        db: Session,
        images: list[Image],
    ) -> list[Image]:

        if not images:
            return []

        db.add_all(images)

        db.flush()

        return images