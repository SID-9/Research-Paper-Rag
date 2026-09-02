from multiprocessing import context
import re

from app.schemas.processing_context import ProcessingContext


class MarkdownCleanerService:

    # ---------------------------------------------------------
    # Marker page separator
    #
    # Example:
    #
    # {0}------------------------------------------------
    # {2}------------------------------------------------
    # {15}------------------------------------------------
    #
    # We convert these into:
    #
    # <!-- page: 0 -->
    # <!-- page: 2 -->
    # <!-- page: 15 -->
    # ---------------------------------------------------------

    PAGE_SEPARATOR_PATTERN = re.compile(
        r"^\{(\d+)\}\s*-{3,}\s*$",
        flags=re.MULTILINE,
    )

   
    def clean(
        self,
        context: ProcessingContext,
    ) -> ProcessingContext:

        if context.markdown_file is None:

            raise RuntimeError(
                "MarkdownCleanerService received no "
                "markdown_file. MarkerParserService must "
                "run successfully before the markdown "
                "cleaner."
            )

        if not context.markdown_file.exists():

            raise FileNotFoundError(
                "Marker markdown output does not exist: "
                f"{context.markdown_file}"
            )
        
        # -----------------------------------------------------
        # Read Marker markdown
        # -----------------------------------------------------

        
        markdown = context.markdown_file.read_text(
            encoding="utf-8"
        )

        # -----------------------------------------------------
        # Normalize line endings
        # -----------------------------------------------------

        markdown = markdown.replace(
            "\r\n",
            "\n",
        )

        markdown = markdown.replace(
            "\r",
            "\n",
        )

        # -----------------------------------------------------
        # Preserve page information
        #
        # {2}----------------------
        #
        # becomes
        #
        # <!-- page: 2 -->
        # -----------------------------------------------------

        markdown = self.PAGE_SEPARATOR_PATTERN.sub(
            lambda match: (
                f"<!-- page: {match.group(1)} -->"
            ),
            markdown,
        )

        
        # -----------------------------------------------------
        # Remove trailing whitespace
        # -----------------------------------------------------

        markdown = "\n".join(
            line.rstrip()
            for line in markdown.splitlines()
        )

        # -----------------------------------------------------
        # Collapse excessive blank lines
        # -----------------------------------------------------

        markdown = re.sub(
            r"\n{3,}",
            "\n\n",
            markdown,
        )

        # -----------------------------------------------------
        # Normalize heading spacing
        #
        # ###Heading
        #
        # ->
        #
        # ### Heading
        # -----------------------------------------------------

        markdown = re.sub(
            r"^(#+)([^\s#])",
            r"\1 \2",
            markdown,
            flags=re.MULTILINE,
        )

        # -----------------------------------------------------
        # Remove empty headings
        # -----------------------------------------------------

        markdown = re.sub(
            r"^#+\s*$",
            "",
            markdown,
            flags=re.MULTILINE,
        )

        # -----------------------------------------------------
        # Final cleanup
        # -----------------------------------------------------

        markdown = markdown.strip()

        context.markdown_file.write_text(
            markdown,
            encoding="utf-8",
        )

        return context
    
    
    #===============================
     # ---------------------------------------------------------
        # Marker image syntax
        #
        # Example:
        #
        # ![](_page_2_Diagram_0.jpeg)
        #
        # becomes:
        #
        # _page_2_Diagram_0.jpeg
        #
        # We also support alt text just in case Marker produces it.
        # ---------------------------------------------------------
    
        # IMAGE_PATTERN = re.compile(
        #     r"!\[([^\]]*)\]\(([^)]+)\)"
        # )
        
        
        # -----------------------------------------------------
                # Convert Markdown image links into raw filenames
                #
                # ![](_page_2_Diagram_0.jpeg)
                #
                # ->
                #
                # _page_2_Diagram_0.jpeg
                # -----------------------------------------------------
        
                # markdown = self.IMAGE_PATTERN.sub(
                #     lambda match: match.group(2).strip(),
                #     markdown,
                # )
        
    