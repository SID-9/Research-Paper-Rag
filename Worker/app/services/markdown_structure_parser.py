import re
from pathlib import Path

from markdown_it import MarkdownIt

from app.schemas.parsed_document import (
    BlockType,
    MarkdownBlock,
    ParsedDocument,
)


class MarkdownStructureParser:
    """
    Parses cleaned Marker Markdown into structural blocks.

    Responsibilities:
        - Parse Markdown into structural blocks
        - Detect headings
        - Detect paragraphs
        - Detect images
        - Detect tables
        - Detect lists
        - Detect code blocks
        - Detect blockquotes
        - Track page markers

    Does NOT:
        - create final chunks
        - generate embeddings
        - write to PostgreSQL
        - call an LLM
    """

    NUMBERED_HEADING_PATTERN = re.compile(
        r"^\s*"
        r"(\d+(?:\.\d+)*)"
        r"\s+"
        r"(.+?)"
        r"\s*$"
    )

    PAGE_PATTERN = re.compile(
        r"<!--\s*page\s*:\s*(\d+)\s*-->",
        flags=re.IGNORECASE,
    )

    IMAGE_PATH_PATTERN = re.compile(
        r"^_page_\d+_[^\s]+\.(?:jpeg|jpg|png|webp|gif)$",
        flags=re.IGNORECASE,
    )

    def __init__(self):
        # IMPORTANT:
        # CommonMark does not enable GFM tables by default.
        self.md = MarkdownIt("commonmark")
        self.md.enable("table")

    # =========================================================
    # PUBLIC API
    # =========================================================

    def parse(
        self,
        markdown_path: str,
        document_id: int,
        stored_filename: str,
    ) -> ParsedDocument:

        path = Path(markdown_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Markdown file not found: {markdown_path}"
            )

        markdown_text = path.read_text(
            encoding="utf-8"
        )

        blocks = self._parse_markdown(
            markdown_text
        )

        return ParsedDocument(
            document_id=document_id,
            stored_filename=stored_filename,
            markdown_path=str(path),
            blocks=blocks,
            total_blocks=len(blocks),
        )

    # =========================================================
    # MAIN PARSER
    # =========================================================

    def _parse_markdown(
        self,
        markdown_text: str,
    ) -> list[MarkdownBlock]:

        tokens = self.md.parse(markdown_text)

        blocks: list[MarkdownBlock] = []

        current_page: int | None = None
        block_index = 0
        index = 0

        while index < len(tokens):

            token = tokens[index]

            # =================================================
            # PAGE MARKER
            # =================================================

            page_number = self._extract_page_number(
                token.content
            )

            if page_number is not None:
                current_page = page_number
                index += 1
                continue

            # =================================================
            # HEADING
            # =================================================

            if token.type == "heading_open":

                marker_heading_level = int(
                    token.tag[1:]
                )

                heading_text = ""

                if index + 1 < len(tokens):

                    inline_token = tokens[index + 1]

                    heading_text = (
                        self._clean_inline_text(
                            inline_token.content
                        )
                    )

                (
                    semantic_level,
                    heading_number,
                ) = self._determine_heading_hierarchy(
                    heading_text=heading_text,
                    block_index=block_index,
                )

                blocks.append(
                    MarkdownBlock(
                        block_index=block_index,
                        block_type=BlockType.HEADING,
                        text=heading_text,
                        heading_level=semantic_level,
                        heading_text=heading_text,
                        marker_heading_level=marker_heading_level,
                        heading_number=heading_number,
                        page_number=current_page,
                    )
                )

                block_index += 1

                # Skip:
                # heading_open
                # inline
                # heading_close
                index += 3

                continue

            # =================================================
            # PARAGRAPH
            # =================================================

            if token.type == "paragraph_open":

                if index + 1 < len(tokens):

                    inline_token = tokens[index + 1]

                    inline_blocks = (
                        self._parse_inline_content(
                            inline_token=inline_token,
                            current_page=current_page,
                            starting_block_index=block_index,
                        )
                    )

                    blocks.extend(inline_blocks)

                    block_index += len(inline_blocks)

                # Skip:
                # paragraph_open
                # inline
                # paragraph_close
                index += 3

                continue

            # =================================================
            # TABLE
            # =================================================

            if token.type == "table_open":

                table_text, next_index = (
                    self._collect_table_content(
                        tokens=tokens,
                        start_index=index,
                    )
                )

                if table_text.strip():

                    blocks.append(
                        MarkdownBlock(
                            block_index=block_index,
                            block_type=BlockType.TABLE,
                            text=table_text.strip(),
                            page_number=current_page,
                        )
                    )

                    block_index += 1

                index = next_index
                continue

            # =================================================
            # LIST
            # =================================================

            if token.type in {
                "bullet_list_open",
                "ordered_list_open",
            }:

                closing_type = (
                    "bullet_list_close"
                    if token.type == "bullet_list_open"
                    else "ordered_list_close"
                )

                list_text, next_index = (
                    self._collect_container_content(
                        tokens=tokens,
                        start_index=index,
                        closing_type=closing_type,
                    )
                )

                if list_text.strip():

                    blocks.append(
                        MarkdownBlock(
                            block_index=block_index,
                            block_type=BlockType.LIST,
                            text=list_text.strip(),
                            page_number=current_page,
                        )
                    )

                    block_index += 1

                index = next_index
                continue

            # =================================================
            # CODE
            # =================================================

            if token.type in {
                "fence",
                "code_block",
            }:

                if token.content.strip():

                    blocks.append(
                        MarkdownBlock(
                            block_index=block_index,
                            block_type=BlockType.CODE,
                            text=token.content.strip(),
                            page_number=current_page,
                        )
                    )

                    block_index += 1

                index += 1
                continue

            # =================================================
            # BLOCKQUOTE
            # =================================================

            if token.type == "blockquote_open":

                quote_text, next_index = (
                    self._collect_container_content(
                        tokens=tokens,
                        start_index=index,
                        closing_type="blockquote_close",
                    )
                )

                if quote_text.strip():

                    blocks.append(
                        MarkdownBlock(
                            block_index=block_index,
                            block_type=BlockType.BLOCKQUOTE,
                            text=quote_text.strip(),
                            page_number=current_page,
                        )
                    )

                    block_index += 1

                index = next_index
                continue

            # =================================================
            # UNKNOWN TOKEN
            # =================================================

            index += 1

        return blocks

    # =========================================================
    # INLINE CONTENT
    # =========================================================

    def _parse_inline_content(
        self,
        inline_token,
        current_page: int | None,
        starting_block_index: int,
    ) -> list[MarkdownBlock]:

        """
        Converts an inline Markdown token into blocks.

        Example:

            Some text ![](_page_2_Diagram_0.jpeg) more text

        becomes:

            PARAGRAPH:
                Some text

            IMAGE:
                _page_2_Diagram_0.jpeg

            PARAGRAPH:
                more text
        """

        blocks: list[MarkdownBlock] = []

        block_index = starting_block_index

        text_parts: list[str] = []

        children = inline_token.children or []

        def flush_text() -> None:
            nonlocal block_index

            if not text_parts:
                return

            text = " ".join(
                part.strip()
                for part in text_parts
                if part.strip()
            ).strip()

            text_parts.clear()

            if not text:
                return

            blocks.append(
                MarkdownBlock(
                    block_index=block_index,
                    block_type=BlockType.PARAGRAPH,
                    text=text,
                    page_number=current_page,
                )
            )

            block_index += 1

        # =====================================================
        # IMPORTANT:
        #
        # This loop MUST be outside flush_text().
        # =====================================================

        for child in children:

            # -------------------------------------------------
            # IMAGE
            # -------------------------------------------------

            if child.type == "image":

                # Flush text before image.
                flush_text()

                image_path = child.attrGet("src")
                image_alt = child.content or ""

                if image_path:

                    blocks.append(
                        MarkdownBlock(
                            block_index=block_index,
                            block_type=BlockType.IMAGE,
                            text=image_alt,
                            image_path=image_path,
                            image_alt_text=image_alt,
                            page_number=current_page,
                        )
                    )

                    block_index += 1

                continue

            # -------------------------------------------------
            # NORMAL TEXT
            # -------------------------------------------------

            if child.type == "text":

                text_parts.append(
                    child.content
                )

                continue

            # -------------------------------------------------
            # INLINE CODE
            # -------------------------------------------------

            if child.type == "code_inline":

                text_parts.append(
                    child.content
                )

                continue

            # -------------------------------------------------
            # SOFT BREAK
            # -------------------------------------------------

            if child.type == "softbreak":

                text_parts.append(" ")

                continue

            # -------------------------------------------------
            # HARD BREAK
            # -------------------------------------------------

            if child.type == "hardbreak":

                text_parts.append(" ")

                continue

            # -------------------------------------------------
            # HTML INLINE
            # -------------------------------------------------

            if child.type == "html_inline":

                # Usually generated by Marker around
                # mathematical fragments or HTML.
                #
                # Do not blindly append the raw HTML
                # because it can pollute paragraph text.
                continue

            # -------------------------------------------------
            # OTHER INLINE CONTENT
            # -------------------------------------------------

            if child.content:

                text_parts.append(
                    child.content
                )

        # Flush text after the final image.
        flush_text()

        return blocks

    # =========================================================
    # HEADING HIERARCHY
    # =========================================================

    def _determine_heading_hierarchy(
        self,
        heading_text: str,
        block_index: int,
    ) -> tuple[int, str | None]:

        text = heading_text.strip()

        match = (
            self.NUMBERED_HEADING_PATTERN.match(
                text
            )
        )

        if match:

            number = match.group(1)

            depth = (
                number.count(".") + 1
            )

            return depth, number

        # First heading = document title
        if block_index == 0:
            return 0, None

        # Unnumbered structural heading
        return 1, None

    # =========================================================
    # PAGE NUMBER
    # =========================================================

    def _extract_page_number(
        self,
        content: str,
    ) -> int | None:

        if not content:
            return None

        match = self.PAGE_PATTERN.search(
            content
        )

        if match:
            return int(match.group(1))

        return None

    # =========================================================
    # TEXT CLEANING
    # =========================================================

    def _clean_inline_text(
        self,
        text: str,
    ) -> str:

        if not text:
            return ""

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # =========================================================
    # CONTAINER CONTENT
    # =========================================================

    def _collect_container_content(
        self,
        tokens,
        start_index: int,
        closing_type: str,
    ) -> tuple[str, int]:

        contents: list[str] = []

        depth = 0

        index = start_index

        while index < len(tokens):

            token = tokens[index]

            if token.type.endswith("_open"):
                depth += 1

            elif token.type.endswith("_close"):

                depth -= 1

                if (
                    depth == 0
                    and token.type == closing_type
                ):
                    return (
                        "\n".join(contents),
                        index + 1,
                    )

            if token.content:
                contents.append(
                    token.content
                )

            index += 1

        return (
            "\n".join(contents),
            index,
        )

    # =========================================================
    # TABLE CONTENT
    # =========================================================

    def _collect_table_content(
        self,
        tokens,
        start_index: int,
    ) -> tuple[str, int]:

        """
        Reconstruct a Markdown table from markdown-it tokens.

        Returns:
            (table_text, index_after_table)
        """

        rows: list[list[str]] = []

        current_row: list[str] | None = None

        index = start_index

        while index < len(tokens):

            token = tokens[index]

            # ---------------------------------------------
            # End of table
            # ---------------------------------------------

            if token.type == "table_close":

                return (
                    self._format_table(rows),
                    index + 1,
                )

            # ---------------------------------------------
            # New row
            # ---------------------------------------------

            if token.type == "tr_open":

                current_row = []

            elif token.type == "tr_close":

                if current_row is not None:
                    rows.append(current_row)

                current_row = None

            # ---------------------------------------------
            # Cell
            # ---------------------------------------------

            elif token.type == "inline":

                if current_row is not None:

                    current_row.append(
                        self._clean_inline_text(
                            token.content
                        )
                    )

            index += 1

        return (
            self._format_table(rows),
            index,
        )

    # =========================================================
    # FORMAT TABLE
    # =========================================================

    def _format_table(
        self,
        rows: list[list[str]],
    ) -> str:

        if not rows:
            return ""

        # Normalize row lengths.
        column_count = max(
            len(row)
            for row in rows
        )

        normalized_rows = []

        for row in rows:

            normalized_rows.append(
                row
                + [""] * (
                    column_count
                    - len(row)
                )
            )

        header = normalized_rows[0]

        separator = [
            "---"
            for _ in range(column_count)
        ]

        output = [
            "| "
            + " | ".join(header)
            + " |",
            "| "
            + " | ".join(separator)
            + " |",
        ]

        for row in normalized_rows[1:]:

            output.append(
                "| "
                + " | ".join(row)
                + " |"
            )

        return "\n".join(output)







# old version image path not visible=================================================

# import re
# from pathlib import Path

# from markdown_it import MarkdownIt

# from app.schemas.parsed_document import (
#     BlockType,
#     MarkdownBlock,
#     ParsedDocument,
# )


# class MarkdownStructureParser:
#     """
#     Parses cleaned Marker Markdown into structural blocks.

#     Important design decisions:

#     1. Marker heading levels are NOT trusted.

#     2. Numbered research-paper headings determine semantic hierarchy.

#        Example:

#            3       -> level 1
#            3.1     -> level 2
#            3.1.1   -> level 3

#     3. Unnumbered major sections such as Abstract, Introduction,
#        Conclusion and References are treated as level 1.

#     4. Page markers are read from:

#            <!-- page: N -->

#     5. Images are recognized in their cleaned form:

#            _page_2_Diagram_0.jpeg

#     6. This service does NOT:
#            - create final chunks
#            - generate embeddings
#            - write to PostgreSQL
#            - call an LLM
#     """

#     # ---------------------------------------------------------
#     # Numbered heading
#     #
#     # Examples:
#     #
#     # 3
#     # 3.1
#     # 3.2.1
#     # 3.2.1.4
#     #
#     # The number itself determines semantic depth.
#     # ---------------------------------------------------------

#     NUMBERED_HEADING_PATTERN = re.compile(
#         r"^\s*"
#         r"(\d+(?:\.\d+)*)"
#         r"\s+"
#         r"(.+?)"
#         r"\s*$"
#     )

#     # ---------------------------------------------------------
#     # Canonical page marker created by MarkdownCleanerService
#     #
#     # <!-- page: 5 -->
#     # ---------------------------------------------------------

#     PAGE_PATTERN = re.compile(
#         r"<!--\s*page\s*:\s*(\d+)\s*-->",
#         flags=re.IGNORECASE,
#     )

#     # ---------------------------------------------------------
#     # Cleaned image path
#     #
#     # Example:
#     #
#     # _page_2_Diagram_0.jpeg
#     # _page_5_Table_1.png
#     #
#     # We intentionally support several common image formats.
#     # ---------------------------------------------------------

#     IMAGE_PATH_PATTERN = re.compile(
#         r"^\s*"
#         r"(_page_\d+_[^\s]+"
#         r"\.(?:jpeg|jpg|png|webp|gif))"
#         r"\s*$",
#         flags=re.IGNORECASE,
#     )
    
#     def __init__(self):

#         self.md = MarkdownIt(
#             "commonmark"
#         )

#     # =========================================================
#     # PUBLIC API
#     # =========================================================

#     def parse(
#         self,
#         markdown_path: str,
#         document_id: int,
#         stored_filename: str,
#     ) -> ParsedDocument:

#         path = Path(markdown_path)

#         if not path.exists():

#             raise FileNotFoundError(
#                 f"Markdown file not found: {markdown_path}"
#             )

#         markdown_text = path.read_text(
#             encoding="utf-8"
#         )

#         blocks = self._parse_markdown(
#             markdown_text
#         )

#         return ParsedDocument(
#             document_id=document_id,
#             stored_filename=stored_filename,
#             markdown_path=str(path),
#             blocks=blocks,
#             total_blocks=len(blocks),
#         )

#     # =========================================================
#     # MAIN PARSER
#     # =========================================================

#     def _parse_markdown(
#         self,
#         markdown_text: str,
#     ) -> list[MarkdownBlock]:

#         tokens = self.md.parse(
#             markdown_text
#         )
        

#         blocks: list[MarkdownBlock] = []

#         current_page: int | None = None

#         block_index = 0

#         index = 0

#         while index < len(tokens):

#             token = tokens[index]

#             # -------------------------------------------------
#             # PAGE MARKER
#             # -------------------------------------------------

#             page_number = self._extract_page_number(
#                 token.content
#             )

#             if page_number is not None:

#                 current_page = page_number

#                 index += 1

#                 continue

#             # -------------------------------------------------
#             # HEADING
#             # -------------------------------------------------

#             if token.type == "heading_open":

#                 marker_heading_level = int(
#                     token.tag[1]
#                 )

#                 heading_text = ""

#                 if index + 1 < len(tokens):

#                     heading_token = tokens[
#                         index + 1
#                     ]

#                     heading_text = (
#                         self._clean_inline_text(
#                             heading_token.content
#                         )
#                     )

#                 (
#                     semantic_level,
#                     heading_number,
#                 ) = self._determine_heading_hierarchy(
#                     heading_text=heading_text,
#                     block_index=block_index,
#                 )

#                 blocks.append(
#                     MarkdownBlock(
#                         block_index=block_index,
#                         block_type=BlockType.HEADING,
#                         text=heading_text,
#                         heading_level=semantic_level,
#                         heading_text=heading_text,
#                         marker_heading_level=(
#                             marker_heading_level
#                         ),
#                         heading_number=heading_number,
#                         page_number=current_page,
#                     )
#                 )

#                 block_index += 1

#                 index += 1

#                 continue

#             # -------------------------------------------------
#             # PARAGRAPH
#             # -------------------------------------------------

#             if token.type == "paragraph_open":

#                 if index + 1 < len(tokens):

#                     inline_token = tokens[
#                         index + 1
#                     ]

#                     raw_content = (
#                         inline_token.content
#                     )

#                     text = (
#                         self._clean_inline_text(
#                             raw_content
#                         )
#                     )

#                     # -------------------------------------------------
#                     # A cleaned image may now appear as a standalone
#                     # paragraph.
#                     # -------------------------------------------------

#                     image_match = (
#                         self.IMAGE_PATH_PATTERN.match(
#                             raw_content
#                         )
#                     )

#                     if image_match:

#                         image_path = (
#                             image_match.group(1)
#                         )

#                         blocks.append(
#                             MarkdownBlock(
#                                 block_index=block_index,
#                                 block_type=(
#                                     BlockType.IMAGE
#                                 ),
#                                 text="",
#                                 image_path=image_path,
#                                 image_alt_text=None,
#                                 page_number=current_page,
#                             )
#                         )

#                         block_index += 1

#                     elif text.strip():

#                         blocks.append(
#                             MarkdownBlock(
#                                 block_index=block_index,
#                                 block_type=(
#                                     BlockType.PARAGRAPH
#                                 ),
#                                 text=text.strip(),
#                                 page_number=current_page,
#                             )
#                         )

#                         block_index += 1

#                 index += 1

#                 continue

            
#             # -------------------------------------------------
#             # IMAGE TOKEN
#             #
#             # Kept for safety in case some documents still
#             # contain normal Markdown image syntax.
#             # -------------------------------------------------

#             if token.type == "image":

#                 image_path = token.attrGet(
#                     "src"
#                 )

#                 image_alt = (
#                     token.content or ""
#                 )

#                 if image_path:

#                     blocks.append(
#                         MarkdownBlock(
#                             block_index=block_index,
#                             block_type=(
#                                 BlockType.IMAGE
#                             ),
#                             text=image_alt,
#                             image_path=image_path,
#                             image_alt_text=image_alt,
#                             page_number=current_page,
#                         )
#                     )

#                     block_index += 1

#                 index += 1

#                 continue

#             # -------------------------------------------------
#             # TABLE
#             # -------------------------------------------------

#             if token.type == "table_open":

#                 table_text = (
#                     self._collect_table_content(
#                         tokens,
#                         index,
#                     )
#                 )

#                 if table_text.strip():

#                     blocks.append(
#                         MarkdownBlock(
#                             block_index=block_index,
#                             block_type=(
#                                 BlockType.TABLE
#                             ),
#                             text=table_text.strip(),
#                             page_number=current_page,
#                         )
#                     )

#                     block_index += 1

#                 index += 1

#                 continue

#             # -------------------------------------------------
#             # LIST
#             # -------------------------------------------------

#             if token.type in {
#                 "bullet_list_open",
#                 "ordered_list_open",
#             }:

#                 list_text = (
#                     self._collect_container_content(
#                         tokens,
#                         index,
#                         {
#                             "bullet_list_close",
#                             "ordered_list_close",
#                         },
#                     )
#                 )

#                 if list_text.strip():

#                     blocks.append(
#                         MarkdownBlock(
#                             block_index=block_index,
#                             block_type=(
#                                 BlockType.LIST
#                             ),
#                             text=list_text.strip(),
#                             page_number=current_page,
#                         )
#                     )

#                     block_index += 1

#                 index += 1

#                 continue

#             # -------------------------------------------------
#             # CODE
#             # -------------------------------------------------

#             if token.type in {
#                 "fence",
#                 "code_block",
#             }:

#                 blocks.append(
#                     MarkdownBlock(
#                         block_index=block_index,
#                         block_type=BlockType.CODE,
#                         text=token.content.strip(),
#                         page_number=current_page,
#                     )
#                 )

#                 block_index += 1

#                 index += 1

#                 continue

#             # -------------------------------------------------
#             # BLOCKQUOTE
#             # -------------------------------------------------

#             if token.type == "blockquote_open":

#                 quote_text = (
#                     self._collect_container_content(
#                         tokens,
#                         index,
#                         {"blockquote_close"},
#                     )
#                 )

#                 if quote_text.strip():

#                     blocks.append(
#                         MarkdownBlock(
#                             block_index=block_index,
#                             block_type=(
#                                 BlockType.BLOCKQUOTE
#                             ),
#                             text=quote_text.strip(),
#                             page_number=current_page,
#                         )
#                     )

#                     block_index += 1

#                 index += 1

#                 continue

#             index += 1

#         return blocks

        
#     # =========================================================
#     # HEADING HIERARCHY
#     # =========================================================

#     def _determine_heading_hierarchy(
#         self,
#         heading_text: str,
#         block_index: int,
#     ) -> tuple[int, str | None]:

#         text = heading_text.strip()

#         # -----------------------------------------------------
#         # Numbered heading
#         #
#         # 3
#         # 3.1
#         # 3.2.1
#         # -----------------------------------------------------

#         match = (
#             self.NUMBERED_HEADING_PATTERN.match(
#                 text
#             )
#         )

#         if match:

#             number = match.group(1)

#             depth = (
#                 number.count(".") + 1
#             )

#             return depth, number

#         # -----------------------------------------------------
#         # First heading without numbering is probably the
#         # document title.
#         #
#         # Example:
#         #
#         # Attention Is All You Need
#         # -----------------------------------------------------

#         if block_index == 0:

#             return 0, None

#         # -----------------------------------------------------
#         # Unnumbered structural heading.
#         #
#         # Examples:
#         #
#         # Abstract
#         # Introduction
#         # Conclusion
#         # References
#         #
#         # We treat these as major sections.
#         # -----------------------------------------------------

#         return 1, None

#     # =========================================================
#     # PAGE NUMBER
#     # =========================================================

#     def _extract_page_number(
#         self,
#         content: str,
#     ) -> int | None:

#         if not content:

#             return None

#         match = (
#             self.PAGE_PATTERN.search(
#                 content
#             )
#         )

#         if match:

#             return int(
#                 match.group(1)
#             )

#         return None

#     # =========================================================
#     # TEXT CLEANING
#     # =========================================================

#     def _clean_inline_text(
#         self,
#         text: str,
#     ) -> str:

#         if not text:

#             return ""

#         # Remove any old-style image syntax
#         # in case cleaner wasn't applied.
#         text = re.sub(
#             r"!\[([^\]]*)\]\(([^)]+)\)",
#             "",
#             text,
#         )

#         text = re.sub(
#             r"\s+",
#             " ",
#             text,
#         )

#         return text.strip()


#     # =========================================================
#     # CONTAINER CONTENT
#     # =========================================================

#     def _collect_container_content(
#         self,
#         tokens,
#         start_index: int,
#         closing_types: set[str],
#     ) -> str:

#         contents = []

#         depth = 0

#         for index in range(
#             start_index,
#             len(tokens),
#         ):

#             token = tokens[index]

#             if token.type.endswith(
#                 "_open"
#             ):

#                 depth += 1

#             elif token.type.endswith(
#                 "_close"
#             ):

#                 depth -= 1

#                 if (
#                     depth <= 0
#                     and token.type
#                     in closing_types
#                 ):

#                     break

#             if token.content:

#                 contents.append(
#                     token.content
#                 )

#         return "\n".join(
#             contents
#         )

#     # =========================================================
#     # TABLE CONTENT
#     # =========================================================

#     def _collect_table_content(
#         self,
#         tokens,
#         start_index: int,
#     ) -> str:

#         contents = []

#         depth = 0

#         for index in range(
#             start_index,
#             len(tokens),
#         ):

#             token = tokens[index]

#             if token.type == "table_open":

#                 depth += 1

#             elif token.type == "table_close":

#                 depth -= 1

#                 if depth <= 0:

#                     break

#             if token.content:

#                 contents.append(
#                     token.content
#                 )

#         return "\n".join(
#             contents
#         )