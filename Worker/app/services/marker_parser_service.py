from pathlib import Path

from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

from app.schemas.processing_context import ProcessingContext


class MarkerParserService:

    def __init__(self):

        print("Loading Marker models...")

        config = {
            # Output Markdown
            "output_format": "markdown",

            # IMPORTANT:
            # Add page numbers/page boundaries to the Markdown output.
            "paginate_output": True,
            "page_range": "0-4",
        }

        config_parser = ConfigParser(config)

        self.converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service(),
        )

    def parse(
        self,
        context: ProcessingContext
    ) -> ProcessingContext:

        pdf = Path(context.file_path)

        if not pdf.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf}"
            )

        print()
        print("=" * 60)
        print("RUNNING MARKER")
        print("=" * 60)

        rendered = self.converter(str(pdf))

        markdown, _, images = text_from_rendered(rendered)

        # ---------------------------------------------------------
        # Optional: normalize Marker page separators
        # into your own RAG-friendly format.
        # ---------------------------------------------------------
        markdown = self._normalize_page_markers(markdown)

        # Save Markdown
        context.markdown_file.write_text(
            markdown,
            encoding="utf-8"
        )

        # Save images
        for name, image in images.items():
            image.save(
                context.images_directory / name
            )

        # Save Marker JSON
        context.json_file.write_text(
            rendered.model_dump_json(
                exclude={"images"},
                indent=4,
            ),
            encoding="utf-8",
        )

        print(f"Markdown : {context.markdown_file}")
        print(f"Images   : {len(images)}")
        print(f"JSON     : {context.json_file}")

        print("=" * 60)

        return context

    @staticmethod
    def _normalize_page_markers(markdown: str) -> str:
        """
        Convert Marker page separators into a consistent format.

        Keep this function isolated so the Marker configuration
        remains independent from your downstream RAG format.
        """

        return markdown

#===============================
# use this one too below this is my orignal old one

# from pathlib import Path

# from marker.config.parser import ConfigParser
# from marker.converters.pdf import PdfConverter
# from marker.models import create_model_dict
# from marker.output import text_from_rendered

# from app.schemas.processing_context import ProcessingContext


# class MarkerParserService:

#     def __init__(self):

#         print("Loading Marker models...")

#         # ---------------------------------------------------------
#         # Marker configuration
#         # ---------------------------------------------------------
#         config = {
#             # Output format
#             "output_format": "markdown",

#             # -----------------------------------------------------
#             # IMPORTANT:
#             # Add page numbers/page boundaries to Markdown output.
#             # -----------------------------------------------------
#             "paginate_output": True,

#             # -----------------------------------------------------
#             # Customize the page separator.
#             #
#             # Example output:
#             #
#             # <!-- PAGE 1 -->
#             #
#             # Content from page 1...
#             #
#             # <!-- PAGE 2 -->
#             #
#             # Content from page 2...
#             # -----------------------------------------------------
#             "page_separator": "\n\n<!-- PAGE {page_number} -->\n\n",
#         }

#         # Marker converts the config into the objects required by
#         # PdfConverter.
#         config_parser = ConfigParser(config)

#         self.converter = PdfConverter(
#             config=config_parser.generate_config_dict(),
#             artifact_dict=create_model_dict(),
#             processor_list=config_parser.get_processors(),
#             renderer=config_parser.get_renderer(),
#             llm_service=config_parser.get_llm_service(),
#         )

#     def parse(
#         self,
#         context: ProcessingContext
#     ) -> ProcessingContext:

#         pdf = Path(context.file_path)

#         if not pdf.exists():
#             raise FileNotFoundError(
#                 f"PDF not found: {pdf}"
#             )

#         print()
#         print("=" * 60)
#         print("RUNNING MARKER")
#         print("=" * 60)

#         # ---------------------------------------------------------
#         # Run Marker
#         # ---------------------------------------------------------
#         rendered = self.converter(str(pdf))

#         # ---------------------------------------------------------
#         # Extract Markdown + images
#         # ---------------------------------------------------------
#         markdown, _, images = text_from_rendered(rendered)

#         # ---------------------------------------------------------
#         # Save Markdown
#         # ---------------------------------------------------------
#         context.markdown_file.write_text(
#             markdown,
#             encoding="utf-8"
#         )

#         # ---------------------------------------------------------
#         # Save extracted images
#         # ---------------------------------------------------------
#         for name, image in images.items():
#             image.save(
#                 context.images_directory / name
#             )

#         # ---------------------------------------------------------
#         # Save Marker JSON
#         #
#         # Keep this because it contains structured information
#         # that can be useful for page-aware RAG/chunking.
#         # ---------------------------------------------------------
#         context.json_file.write_text(
#             rendered.model_dump_json(
#                 exclude={"images"},
#                 indent=4,
#             ),
#             encoding="utf-8",
#         )

#         print(f"Markdown : {context.markdown_file}")
#         print(f"Images   : {len(images)}")
#         print(f"JSON     : {context.json_file}")

#         print("=" * 60)

#         return context

#===================

            
            
        
        # from pprint import pprint

        # print(type(rendered))

        # data = rendered.model_dump()

        # print("=" * 60)
        # print("TOP LEVEL KEYS")
        # print("=" * 60)
        # pprint(data.keys())

        # for key, value in data.items():
        #     print(f"{key}: {type(value)}")
            
            
            
                
        # save the json 
        # context.json_file.write_text(
        #     rendered.model_dump_json(
        #         indent=4
        #     ),
        #     encoding="utf-8"
        # )
