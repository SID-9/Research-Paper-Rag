import re

from app.schemas.chunk import Chunk


class ChunkRefinementService:
    """
    Performs post-processing on chunks created by ChunkService.

    Current responsibility:

    - Detect front matter appearing before the Abstract.
    - Consolidate meaningful front-matter chunks into one chunk.
    - Keep the Abstract and all normal paper content untouched.

    This service intentionally does NOT:

    - perform semantic similarity checks
    - merge arbitrary small chunks
    - split chunks
    - create embeddings
    - access the database
    """

    ABSTRACT_PATTERN = re.compile(
        r"^\s*(?:abstract)\s*$",
        re.IGNORECASE,
    )

    FRONT_MATTER_KEYWORDS = (
        "copyright",
        "doi",
        "published",
        "publication",
        "journal",
        "conference",
        "manuscript",
        "accepted manuscript",
        "preprint",
        "available online",
        "received",
        "revised",
        "author",
        "authors",
        "affiliation",
    )

    def refine(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:

        if not chunks:
            return []

        front_matter_chunks: list[Chunk] = []
        remaining_chunks: list[Chunk] = []

        front_matter_phase = True
        abstract_found = False

        for chunk in chunks:

            # -------------------------------------------------
            # Once we have encountered Abstract, front matter
            # processing is permanently finished.
            # -------------------------------------------------

            if front_matter_phase:

                if self._is_abstract_chunk(chunk):
                    abstract_found = True
                    front_matter_phase = False

                    remaining_chunks.append(chunk)

                    continue

                if self._is_front_matter_chunk(chunk):
                    front_matter_chunks.append(chunk)

                    continue

                # -------------------------------------------------
                # This is content before Abstract that does not
                # confidently look like front matter.
                #
                # Preserve it rather than accidentally destroying
                # useful paper content.
                # -------------------------------------------------

                front_matter_phase = False

                remaining_chunks.append(chunk)

                continue

            remaining_chunks.append(chunk)

        # -----------------------------------------------------
        # No front matter found.
        # -----------------------------------------------------

        if not front_matter_chunks:
            return self._reindex_chunks(
                remaining_chunks
            )

        # -----------------------------------------------------
        # Build one consolidated front-matter chunk.
        # -----------------------------------------------------

        front_matter_chunk = self._merge_front_matter(
            front_matter_chunks
        )

        # -----------------------------------------------------
        # Put front matter before the rest of the document.
        # -----------------------------------------------------

        refined_chunks = [
            front_matter_chunk,
            *remaining_chunks,
        ]

        return self._reindex_chunks(
            refined_chunks
        )

    # =========================================================
    # ABSTRACT DETECTION
    # =========================================================

    def _is_abstract_chunk(
        self,
        chunk: Chunk,
    ) -> bool:

        if not chunk.heading_path:
            return False

        last_heading = (
            chunk.heading_path[-1]
            .strip()
        )

        return bool(
            self.ABSTRACT_PATTERN.fullmatch(
                last_heading
            )
        )

    # =========================================================
    # FRONT MATTER DETECTION
    # =========================================================

    def _is_front_matter_chunk(
        self,
        chunk: Chunk,
    ) -> bool:

        text = chunk.text.strip()

        if not text:
            return False

        # -----------------------------------------------------
        # Empty heading path:
        #
        # Commonly contains:
        # - authors
        # - affiliations
        # - title metadata
        # - publication information
        #
        # We consider it front matter only when it occurs
        # before Abstract.
        # -----------------------------------------------------

        if not chunk.heading_path:
            return True

        heading_text = " ".join(
            chunk.heading_path
        ).lower()

        text_lower = text.lower()

        # -----------------------------------------------------
        # Explicit bibliographic / publication indicators.
        # -----------------------------------------------------

        for keyword in self.FRONT_MATTER_KEYWORDS:

            if keyword in heading_text:
                return True

            if keyword in text_lower:
                return True

        # -----------------------------------------------------
        # DOI pattern
        # -----------------------------------------------------

        if re.search(
            r"\b10\.\d{4,9}/[-._;()/:a-z0-9]+\b",
            text_lower,
        ):
            return True

        # -----------------------------------------------------
        # Email addresses.
        #
        # Useful for author / affiliation blocks.
        # -----------------------------------------------------

        if re.search(
            r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
            text,
            flags=re.IGNORECASE,
        ):
            return True

        return False

    # =========================================================
    # MERGE FRONT MATTER
    # =========================================================

    def _merge_front_matter(
        self,
        chunks: list[Chunk],
    ) -> Chunk:

        if not chunks:
            raise ValueError(
                "Cannot merge empty front matter."
            )

        text_parts: list[str] = []
        block_types = []
        image_paths: list[str] = []

        first_page = None

        for chunk in chunks:

            # -------------------------------------------------
            # Page
            # -------------------------------------------------

            if (
                first_page is None
                and chunk.page_number is not None
            ):
                first_page = chunk.page_number

            # -------------------------------------------------
            # Text
            # -------------------------------------------------

            if chunk.text.strip():

                text_parts.append(
                    chunk.text.strip()
                )

            # -------------------------------------------------
            # Block types
            # -------------------------------------------------

            for block_type in chunk.block_types:

                if block_type not in block_types:
                    block_types.append(
                        block_type
                    )

            # -------------------------------------------------
            # Images
            # -------------------------------------------------

            for image_path in chunk.image_paths:

                if image_path not in image_paths:
                    image_paths.append(
                        image_path
                    )

        return Chunk(
            document_id=chunks[0].document_id,
            chunk_index=0,
            page_number=first_page,
            heading_path=[],
            text="\n\n".join(
                text_parts
            ).strip(),
            block_types=block_types,
            image_paths=image_paths,
        )

    # =========================================================
    # REINDEX
    # =========================================================

    def _reindex_chunks(
        self,
        chunks: list[Chunk],
    ) -> list[Chunk]:

        for index, chunk in enumerate(chunks):

            chunk.chunk_index = index

        return chunks