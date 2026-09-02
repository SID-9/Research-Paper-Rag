import re

from app.core.config import settings

from app.schemas.chunk import Chunk
from app.schemas.semantic_block import (
    SemanticBlock,
    SemanticBlockType,
)


class ChunkService:
    """
    Converts semantic blocks into final RAG chunks.

    Chunking strategy:

    1. Preserve heading hierarchy.
    2. Keep blocks belonging to the same heading path together
       whenever possible.
    3. Respect a configurable maximum chunk size.
    4. Prefer splitting at paragraph boundaries.
    5. If a paragraph is too large, split it by sentences.
    6. If a sentence is still too large, fall back to a
       character-based hard split.
    7. Preserve images and tables with their surrounding
       semantic context.
    8. Preserve image paths.
    9. Preserve block types.
    10. Maintain deterministic chunk ordering.

    This service does NOT:

    - create embeddings
    - call an LLM
    - write to PostgreSQL
    - perform vector search
    """

    def build_chunks(
        self,
        document_id: int,
        semantic_blocks: list[SemanticBlock],
    ) -> list[Chunk]:

        chunks: list[Chunk] = []

        if not semantic_blocks:
            return chunks

        # -----------------------------------------------------
        # Group blocks by heading path.
        #
        # Important:
        #
        # We do NOT group the entire document by heading path
        # globally.
        #
        # We process consecutive blocks belonging to the same
        # semantic section.
        # -----------------------------------------------------

        current_group: list[SemanticBlock] = []
        current_heading_path: list[str] = []

        for block in semantic_blocks:

            if not current_group:

                current_group = [block]

                current_heading_path = (
                    block.heading_path.copy()
                )

                continue

            if block.heading_path == current_heading_path:

                current_group.append(block)

                continue

            # -------------------------------------------------
            # Heading path changed.
            #
            # Finalize previous semantic section.
            # -------------------------------------------------

            section_chunks = self._chunk_section(
                document_id=document_id,
                blocks=current_group,
                starting_index=len(chunks),
            )

            chunks.extend(section_chunks)

            # -------------------------------------------------
            # Start new semantic section.
            # -------------------------------------------------

            current_group = [block]

            current_heading_path = (
                block.heading_path.copy()
            )

        # -----------------------------------------------------
        # Final section.
        # -----------------------------------------------------

        if current_group:

            section_chunks = self._chunk_section(
                document_id=document_id,
                blocks=current_group,
                starting_index=len(chunks),
            )

            chunks.extend(section_chunks)

        return chunks

    # =========================================================
    # SECTION CHUNKING
    # =========================================================

    def _chunk_section(
        self,
        document_id: int,
        blocks: list[SemanticBlock],
        starting_index: int,
    ) -> list[Chunk]:

        if not blocks:
            return []

        heading_path = blocks[0].heading_path.copy()

        # -----------------------------------------------------
        # Convert semantic blocks into content units.
        #
        # A unit can be:
        #
        # paragraph
        # table
        # image
        # list
        # code
        # blockquote
        #
        # We intentionally do NOT flatten everything into one
        # string immediately.
        # -----------------------------------------------------

        units: list[SemanticBlock] = []

        for block in blocks:

            if self._has_content(block):
                units.append(block)

        if not units:
            return []

        final_chunks: list[Chunk] = []

        current_units: list[SemanticBlock] = []

        current_size = 0

        for unit in units:

            unit_text = self._get_block_text(unit)

            unit_size = self._estimate_size(unit_text)

            # -------------------------------------------------
            # Special blocks
            #
            # Images/tables/code are treated as semantic units.
            #
            # We don't split them internally here.
            # -------------------------------------------------

            if self._is_atomic_block(unit):

                # If adding the atomic block would exceed the
                # maximum size, finalize the current chunk first.
                if (
                    current_units
                    and current_size + unit_size
                    > settings.CHUNK_MAX_CHARACTERS
                ):

                    final_chunks.append(
                        self._create_chunk(
                            document_id=document_id,
                            chunk_index=(
                                starting_index
                                + len(final_chunks)
                            ),
                            blocks=current_units,
                        )
                    )

                    current_units = []

                    current_size = 0

                current_units.append(unit)

                current_size += unit_size

                continue

            # -------------------------------------------------
            # Normal textual content
            # -------------------------------------------------

            if (
                current_units
                and current_size + unit_size
                > settings.CHUNK_MAX_CHARACTERS
            ):

                final_chunks.append(
                    self._create_chunk(
                        document_id=document_id,
                        chunk_index=(
                            starting_index
                            + len(final_chunks)
                        ),
                        blocks=current_units,
                    )
                )

                current_units = []

                current_size = 0

            # -------------------------------------------------
            # Paragraph itself may be too large.
            # -------------------------------------------------

            if unit_size > settings.CHUNK_MAX_CHARACTERS:

                # Flush existing content first.
                if current_units:

                    final_chunks.append(
                        self._create_chunk(
                            document_id=document_id,
                            chunk_index=(
                                starting_index
                                + len(final_chunks)
                            ),
                            blocks=current_units,
                        )
                    )

                    current_units = []

                    current_size = 0

                # Split oversized paragraph.
                paragraph_chunks = (
                    self._split_large_text_block(
                        document_id=document_id,
                        block=unit,
                        starting_index=(
                            starting_index
                            + len(final_chunks)
                        ),
                    )
                )

                final_chunks.extend(
                    paragraph_chunks
                )

                continue

            current_units.append(unit)

            current_size += unit_size

        # -----------------------------------------------------
        # Final chunk in this semantic section.
        # -----------------------------------------------------

        if current_units:

            final_chunks.append(
                self._create_chunk(
                    document_id=document_id,
                    chunk_index=(
                        starting_index
                        + len(final_chunks)
                    ),
                    blocks=current_units,
                )
            )

        return final_chunks

    # =========================================================
    # OVERSIZED TEXT BLOCK
    # =========================================================

    def _split_large_text_block(
        self,
        document_id: int,
        block: SemanticBlock,
        starting_index: int,
    ) -> list[Chunk]:

        text = block.text.strip()

        if not text:
            return []

        # -----------------------------------------------------
        # First attempt:
        #
        # Split by paragraphs.
        # -----------------------------------------------------

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(
                r"\n\s*\n",
                text,
            )
            if paragraph.strip()
        ]

        # -----------------------------------------------------
        # If the entire block is one paragraph, split into
        # sentences.
        # -----------------------------------------------------

        if len(paragraphs) == 1:

            paragraphs = self._split_sentences(
                paragraphs[0]
            )

        chunks: list[Chunk] = []

        current_parts: list[str] = []

        current_size = 0

        for part in paragraphs:

            part_size = self._estimate_size(
                part
            )

            # -------------------------------------------------
            # Normal part fits.
            # -------------------------------------------------

            if (
                current_parts
                and current_size + part_size
                > settings.CHUNK_MAX_CHARACTERS
            ):

                chunks.append(
                    self._create_text_chunk(
                        document_id=document_id,
                        chunk_index=(
                            starting_index
                            + len(chunks)
                        ),
                        source_block=block,
                        text_parts=current_parts,
                    )
                )

                current_parts = []

                current_size = 0

            # -------------------------------------------------
            # Part itself is still too large.
            #
            # Hard split fallback.
            # -------------------------------------------------

            if (
                part_size
                > settings.CHUNK_MAX_CHARACTERS
            ):

                if current_parts:

                    chunks.append(
                        self._create_text_chunk(
                            document_id=document_id,
                            chunk_index=(
                                starting_index
                                + len(chunks)
                            ),
                            source_block=block,
                            text_parts=current_parts,
                        )
                    )

                    current_parts = []

                    current_size = 0

                hard_chunks = (
                    self._hard_split_text(
                        document_id=document_id,
                        block=block,
                        text=part,
                        starting_index=(
                            starting_index
                            + len(chunks)
                        ),
                    )
                )

                chunks.extend(hard_chunks)

                continue

            current_parts.append(part)

            current_size += part_size

        if current_parts:

            chunks.append(
                self._create_text_chunk(
                    document_id=document_id,
                    chunk_index=(
                        starting_index
                        + len(chunks)
                    ),
                    source_block=block,
                    text_parts=current_parts,
                )
            )

        return chunks

    # =========================================================
    # SENTENCE SPLITTING
    # =========================================================

    def _split_sentences(
        self,
        text: str,
    ) -> list[str]:

        sentences = re.split(
            r"(?<=[.!?])\s+(?=[A-Z0-9])",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    # =========================================================
    # HARD TEXT SPLIT
    # =========================================================

    def _hard_split_text(
        self,
        document_id: int,
        block: SemanticBlock,
        text: str,
        starting_index: int,
    ) -> list[Chunk]:

        max_size = settings.CHUNK_MAX_CHARACTERS

        pieces = [
            text[i:i + max_size]
            for i in range(
                0,
                len(text),
                max_size,
            )
        ]

        chunks: list[Chunk] = []

        for index, piece in enumerate(pieces):

            chunks.append(
                self._create_text_chunk(
                    document_id=document_id,
                    chunk_index=(
                        starting_index + index
                    ),
                    source_block=block,
                    text_parts=[piece.strip()],
                )
            )

        return chunks

    # =========================================================
    # CREATE TEXT CHUNK
    # =========================================================

    def _create_text_chunk(
        self,
        document_id: int,
        chunk_index: int,
        source_block: SemanticBlock,
        text_parts: list[str],
    ) -> Chunk:

        return Chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            page_number=source_block.page_number,
            heading_path=(
                source_block.heading_path.copy()
            ),
            text="\n\n".join(
                text_parts
            ).strip(),
            block_types=[
                source_block.block_type
            ],
            image_paths=(
                [source_block.image_path]
                if source_block.image_path
                else []
            ),
        )

    # =========================================================
    # CREATE NORMAL CHUNK
    # =========================================================

    def _create_chunk(
        self,
        document_id: int,
        chunk_index: int,
        blocks: list[SemanticBlock],
    ) -> Chunk:

        if not blocks:

            raise ValueError(
                "Cannot create a chunk from an empty block list."
            )

        heading_path = (
            blocks[0].heading_path.copy()
        )

        # -----------------------------------------------------
        # Combine text
        # -----------------------------------------------------

        text_parts: list[str] = []

        for block in blocks:

            block_text = self._get_block_text(
                block
            )

            if block_text:

                text_parts.append(
                    block_text
                )

        text = "\n\n".join(
            text_parts
        ).strip()

        # -----------------------------------------------------
        # Page
        #
        # Currently:
        # first page represented by the chunk.
        #
        # We will later introduce page_start/page_end.
        # -----------------------------------------------------

        page_number = next(
            (
                block.page_number
                for block in blocks
                if block.page_number is not None
            ),
            None,
        )

        # -----------------------------------------------------
        # Block types
        # -----------------------------------------------------

        block_types = list(
            dict.fromkeys(
                block.block_type
                for block in blocks
            )
        )

        # -----------------------------------------------------
        # Images
        # -----------------------------------------------------

        image_paths: list[str] = []

        for block in blocks:

            if block.image_path:

                image_paths.append(
                    block.image_path
                )

            # ---------------------------------------------
            # Fallback:
            # extract Markdown image paths.
            # ---------------------------------------------

            if block.text:

                markdown_image_paths = re.findall(
                    r"!\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)",
                    block.text,
                )

                image_paths.extend(
                    markdown_image_paths
                )

        # -----------------------------------------------------
        # Remove duplicate images.
        # -----------------------------------------------------

        image_paths = list(
            dict.fromkeys(image_paths)
        )

        return Chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            page_number=page_number,
            heading_path=heading_path,
            text=text,
            block_types=block_types,
            image_paths=image_paths,
        )

    # =========================================================
    # HELPERS
    # =========================================================

    def _has_content(
        self,
        block: SemanticBlock,
    ) -> bool:

        if block.text.strip():

            return True

        if block.image_path:

            return True

        return (
            block.block_type
            in {
                SemanticBlockType.TABLE,
                SemanticBlockType.IMAGE,
            }
        )

    def _get_block_text(
        self,
        block: SemanticBlock,
    ) -> str:

        return block.text.strip()

    def _estimate_size(
        self,
        text: str,
    ) -> int:

        return len(text)

    def _is_atomic_block(
        self,
        block: SemanticBlock,
    ) -> bool:

        return block.block_type in {
            SemanticBlockType.IMAGE,
            SemanticBlockType.TABLE,
            SemanticBlockType.CODE,
        }








#=========================== with actual chunks update above one
# import re

# from app.schemas.chunk import Chunk
# from app.schemas.semantic_block import (
#     SemanticBlock,
#     SemanticBlockType,
# )


# class ChunkService:
#     """
#     Converts semantic blocks into RAG chunks.

#     Responsibilities:

#     - Keep blocks belonging to the same heading path together.
#     - Preserve all block content.
#     - Preserve images and tables even when their text field is empty.
#     - Preserve Markdown syntax exactly as received from the parser.
#     - Track the block types contained in each chunk.
#     - Preserve image paths for downstream processing.

#     It does NOT:

#     - create embeddings
#     - write to PostgreSQL
#     - call an LLM
#     - perform token-based splitting
#     """

#     def build_chunks(
#         self,
#         document_id: int,
#         semantic_blocks: list[SemanticBlock],
#     ) -> list[Chunk]:

#         chunks: list[Chunk] = []

#         current_blocks: list[SemanticBlock] = []
#         current_heading_path: list[str] = []
        

#         for block in semantic_blocks:

#             # -------------------------------------------------
#             # First block
#             # -------------------------------------------------

#             if not current_blocks:

#                 current_blocks = [block]

#                 current_heading_path = (
#                     block.heading_path.copy()
#                 )

#                 continue

#             # -------------------------------------------------
#             # Same semantic section
#             # -------------------------------------------------

#             if block.heading_path == current_heading_path:

#                 current_blocks.append(block)

#                 continue

#             # -------------------------------------------------
#             # Heading path changed.
#             #
#             # Finalize the previous semantic group.
#             # -------------------------------------------------

#             chunk = self._create_chunk(
#                 document_id=document_id,
#                 chunk_index=len(chunks),
#                 blocks=current_blocks,
#             )

#             chunks.append(chunk)

#             # -------------------------------------------------
#             # Start a new semantic group.
#             # -------------------------------------------------

#             current_blocks = [block]

#             current_heading_path = (
#                 block.heading_path.copy()
#             )

#         # -----------------------------------------------------
#         # Final group
#         # -----------------------------------------------------

#         if current_blocks:

#             chunk = self._create_chunk(
#                 document_id=document_id,
#                 chunk_index=len(chunks),
#                 blocks=current_blocks,
#             )

#             chunks.append(chunk)

#         return chunks

#     # =========================================================
#     # CREATE CHUNK
#     # =========================================================

#     def _create_chunk(
#         self,
#         document_id: int,
#         chunk_index: int,
#         blocks: list[SemanticBlock],
#     ) -> Chunk:

#         if not blocks:
#             raise ValueError(
#                 "Cannot create a chunk from an empty block list."
#             )

#         # -----------------------------------------------------
#         # Heading path
#         # -----------------------------------------------------

#         heading_path = blocks[0].heading_path.copy()

#         # -----------------------------------------------------
#         # Combine content
#         #
#         # Do not modify Markdown syntax.
#         # -----------------------------------------------------

#         text_parts: list[str] = []

#         for block in blocks:

#             block_text = block.text.strip()

#             if block_text:
#                 text_parts.append(block_text)

#         text = "\n\n".join(text_parts).strip()

#         # -----------------------------------------------------
#         # Page number
#         # -----------------------------------------------------

#         page_number = next(
#             (
#                 block.page_number
#                 for block in blocks
#                 if block.page_number is not None
#             ),
#             None,
#         )

#         # -----------------------------------------------------
#         # Block types
#         # -----------------------------------------------------

#         block_types = list(
#             dict.fromkeys(
#                 block.block_type
#                 for block in blocks
#             )
#         )

#         # -----------------------------------------------------
#         # Image paths
#         #
#         # First use the structured image_path field.
#         #
#         # Then fall back to extracting Markdown image paths
#         # from block.text.
#         #
#         # This makes the chunk stage robust to parsers that
#         # preserve image Markdown in text but do not populate
#         # image_path.
#         # -----------------------------------------------------

#         image_paths: list[str] = []

#         for block in blocks:

#             # ---------------------------------------------
#             # Preferred source:
#             # structured image_path
#             # ---------------------------------------------

#             if (
#                 block.block_type == SemanticBlockType.IMAGE
#                 and block.image_path
#             ):
#                 image_paths.append(
#                     block.image_path
#                 )

#             # ---------------------------------------------
#             # Fallback source:
#             # Markdown image syntax
#             #
#             # ![alt text](images/figure1.png)
#             # ---------------------------------------------

#             if block.text:

#                 markdown_image_paths = re.findall(
#                     r"!\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)",
#                     block.text,
#                 )

#                 image_paths.extend(
#                     markdown_image_paths
#                 )

#         # -----------------------------------------------------
#         # Remove duplicates while preserving order.
#         # -----------------------------------------------------

#         image_paths = list(
#             dict.fromkeys(image_paths)
#         )

#         # -----------------------------------------------------
#         # Build final chunk
#         # -----------------------------------------------------

#         return Chunk(
#             document_id=document_id,
#             chunk_index=chunk_index,
#             page_number=page_number,
#             heading_path=heading_path,
#             text=text,
#             block_types=block_types,
#             image_paths=image_paths,
#         )
