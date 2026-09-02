from app.schemas.parsed_document import (
    BlockType,
    MarkdownBlock,
    ParsedDocument,
)

from app.schemas.semantic_block import (
    SemanticBlock,
    SemanticBlockType,
)


class SemanticBlockService:
    """
    Converts structural Markdown blocks into semantic blocks.

    Responsibilities:

    - Maintain heading hierarchy
    - Attach each content block to the correct heading path
    - Preserve page information
    - Preserve image/table/list information

    It does NOT:

    - create embeddings
    - write to PostgreSQL
    - call an LLM
    - perform chunk-size splitting
    """

    def build(
        self,
        document: ParsedDocument,
    ) -> list[SemanticBlock]:

        semantic_blocks: list[SemanticBlock] = []

        # -----------------------------------------------------
        # Current heading hierarchy
        #
        # Example:
        #
        # level 1 → "3 Method"
        # level 2 → "3.1 Dataset"
        # level 3 → "3.1.1 Preprocessing"
        #
        # represented as:
        #
        # {
        #     1: "3 Method",
        #     2: "3.1 Dataset",
        #     3: "3.1.1 Preprocessing"
        # }
        # -----------------------------------------------------

        heading_stack: dict[int, str] = {}
        
        document_title: str | None = None

        for block in document.blocks:

            # =================================================
            # HEADING
            # =================================================

            if block.block_type == BlockType.HEADING:

                if block.heading_level is None:
                    continue

                current_level = block.heading_level

                heading_text = (
                    block.heading_text
                    or block.text
                ).strip()
                
                # -------------------------------------------------
                # First heading is the document title.
                #
                # We intentionally treat it as the document title
                # regardless of whether Marker extracted it as:
                #
                # # Title
                # ## Title
                # ### Title
                #
                # This prevents the title from entering the
                # semantic heading path.
                # -------------------------------------------------

                if document_title is None:
                    document_title = heading_text
                    continue

                # -------------------------------------------------
                # Remove headings that belong to deeper levels.
                #
                # Example:
                #
                # currently:
                #
                # 1 → Method
                # 2 → Architecture
                # 3 → Encoder
                #
                # now we encounter:
                #
                # 2 → Dataset
                #
                # remove level 3.
                # -------------------------------------------------

                levels_to_remove = [
                    level
                    for level in heading_stack
                    if level >= current_level
                ]

                for level in levels_to_remove:
                    del heading_stack[level]

                # -------------------------------------------------
                # Add current heading
                # -------------------------------------------------

                heading_stack[current_level] = heading_text

                continue

            # =================================================
            # CONTENT
            # =================================================

            block_type = self._map_block_type(
                block.block_type
            )

            heading_path = [
                heading_stack[level]
                for level in sorted(
                    heading_stack.keys()
                )
            ]

            semantic_blocks.append(
                SemanticBlock(
                    block_index=block.block_index,
                    block_type=block_type,
                    text=block.text,
                    heading_path=heading_path,
                    page_number=block.page_number,
                    image_path=block.image_path,
                    image_alt_text=block.image_alt_text,
                )
            )

        return semantic_blocks

    # =========================================================
    # BLOCK TYPE MAPPING
    # =========================================================

    def _map_block_type(
        self,
        block_type: BlockType,
    ) -> SemanticBlockType:

        mapping = {
            BlockType.PARAGRAPH:
                SemanticBlockType.PARAGRAPH,
            
            # BlockType.TEXT:
            #                 SemanticBlockType.TEXT,

            BlockType.TABLE:
                SemanticBlockType.TABLE,

            BlockType.IMAGE:
                SemanticBlockType.IMAGE,

            BlockType.LIST:
                SemanticBlockType.LIST,

            BlockType.CODE:
                SemanticBlockType.CODE,

            BlockType.BLOCKQUOTE:
                SemanticBlockType.BLOCKQUOTE,
        }

        return mapping.get(
            block_type,
            SemanticBlockType.PARAGRAPH,
        )