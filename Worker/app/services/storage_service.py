from pathlib import Path

from app.core.config import settings
from app.schemas.processing_context import ProcessingContext


class StorageService:

    def __init__(self):

        self.storage_root = Path(settings.STORAGE_ROOT)

        self.marker_root = (
            self.storage_root /
            settings.MARKER_OUTPUT_FOLDER
        )

    def create_workspace(
            self,
            context: ProcessingContext
    ) -> ProcessingContext:

        """
        Creates the following structure

        marker_outputs/

            stored_filename/

                images/

                markdown.md

                metadata.json
        """

        folder_name = Path(
            context.stored_filename
        ).stem

        workspace = self.marker_root / folder_name

        images_directory = workspace / "images"

        workspace.mkdir(
            parents=True,
            exist_ok=True
        )

        images_directory.mkdir(
            exist_ok=True
        )

        context.workspace = workspace

        context.images_directory = images_directory

        context.markdown_file = (
            workspace /
            "markdown.md"
        )

        context.json_file = (
            workspace /
            "document.json"
        )

        return context

    # def workspace_exists(
    #         self,
    #         context: ProcessingContext
    # ) -> bool:

    #     return (
    #         context.workspace is not None
    #         and context.workspace.exists()
    #     )