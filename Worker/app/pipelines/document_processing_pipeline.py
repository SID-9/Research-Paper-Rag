from sqlalchemy.orm import Session

from app.schemas.processing_context import (
    ProcessingContext,
)

from app.services.marker_parser_service import (
    MarkerParserService,
)

from app.services.markdown_cleaner_service import (
    MarkdownCleanerService,
)

from app.services.document_service import (
    DocumentService,
)

from app.models.document import (
    DocumentStatus,
)

from app.services.markdown_structure_parser import (
    MarkdownStructureParser,
)

from app.services.semantic_block_service import (
    SemanticBlockService,
)

from app.services.chunk_service import (
    ChunkService,
)

from app.services.embedding_service import (
    EmbeddingService,
)

from app.services.storage_service import (
    StorageService,
)

from app.services.document_persistence_service import (
    DocumentPersistenceService,
)

from app.services.embedding_chunk_service import (
    ChunkEmbeddingService,
)


class DocumentProcessingPipeline:

    def __init__(self):

        # =================================================
        # PROCESSING SERVICES
        # =================================================

        self.storage_service = (
            StorageService()
        )

        # Marker MUST run before MarkdownCleanerService.
        self.marker_parser = (
            MarkerParserService()
        )

        self.cleaner = (
            MarkdownCleanerService()
        )

        self.parser = (
            MarkdownStructureParser()
        )

        self.semantic_block_service = (
            SemanticBlockService()
        )

        self.chunk_service = (
            ChunkService()
        )

        # =================================================
        # EMBEDDING
        # =================================================
        
        self.embedding_service = (
            EmbeddingService()
        )
        self.chunk_embedding_service = (
            ChunkEmbeddingService(
                embedding_service=self.embedding_service
            )
        )

        # =================================================
        # PERSISTENCE
        #
        # This service internally coordinates:
        #
        # ChunkPersistenceService
        # ImagePersistenceService
        #
        # and the database transaction.
        # =================================================

        self.document_persistence_service = (
            DocumentPersistenceService()
        )

    def process(
        self,
        db: Session,
        context: ProcessingContext,
    ) -> ProcessingContext:

        print()
        print("=" * 60)
        print("DOCUMENT PROCESSING PIPELINE")
        print("=" * 60)

        # =================================================
        # STEP 0
        # Update document status
        # =================================================

        DocumentService.update_status(
            db,
            context.document_id,
            DocumentStatus.PARSING,
        )

        print(
            "Status Updated -> PARSING"
        )

        # =================================================
        # STEP 1
        # Create workspace
        # =================================================

        context = (
            self.storage_service.create_workspace(
                context
            )
        )

        print(
            "Workspace Created"
        )

        # =================================================
        # STEP 2
        # Run Marker
        #
        # Marker generates:
        #
        # marker_outputs/
        #     <stored_filename>/
        #         markdown.md
        #         images/
        #         ...
        #
        # It also populates:
        #
        # context.markdown_file
        # =================================================

        print(
            "Running Marker...",
            flush=True,
        )

        print(
            "BEFORE MARKER PARSE",
            flush=True,
        )

        context = (
            self.marker_parser.parse(
                context
            )
        )

        print(
            "AFTER MARKER PARSE",
            flush=True,
        )

        print(
            "Marker Processing Completed",
            flush=True,
        )

        # =================================================
        # STEP 3
        # Clean Marker Markdown
        # =================================================

        context = (
            self.cleaner.clean(
                context
            )
        )

        print(
            "Markdown Cleaned"
        )

        # =================================================
        # STEP 4
        # Parse Markdown Structure
        # =================================================

        parsed_document = (
            self.parser.parse(
                markdown_path=str(
                    context.markdown_file
                ),
                document_id=(
                    context.document_id
                ),
                stored_filename=(
                    context.stored_filename
                ),
            )
        )

        context.parsed_document = (
            parsed_document
        )

        print(
            "Markdown Structure Parsed"
        )

        # =================================================
        # STEP 5
        # Build Semantic Blocks
        # =================================================

        semantic_blocks = (
            self.semantic_block_service.build(
                parsed_document
            )
        )

        context.semantic_blocks = (
            semantic_blocks
        )

        print(
            f"Semantic Blocks Created: "
            f"{len(semantic_blocks)}"
        )

        # =================================================
        # STEP 6
        # Update status -> CHUNKING
        # =================================================

        DocumentService.update_status(
            db,
            context.document_id,
            DocumentStatus.CHUNKING,
        )

        print(
            "Status Updated -> CHUNKING"
        )

        # =================================================
        # STEP 7
        # Build Chunks
        # =================================================

        chunks = (
            self.chunk_service.build_chunks(
                document_id=(
                    context.document_id
                ),
                semantic_blocks=(
                    semantic_blocks
                ),
            )
        )

        context.chunks = chunks

        print(
            f"Chunks Created: "
            f"{len(chunks)}"
        )

        # =================================================
        # STEP 8
        # Save chunks.md
        #
        # This is a debugging / inspection artifact.
        # =================================================

        chunks_md_path = (
            context.workspace / "chunks.md"
        )

        with open(
            chunks_md_path,
            "w",
            encoding="utf-8",
        ) as f:

            for chunk in context.chunks:

                f.write(
                    f"# Chunk "
                    f"{chunk.chunk_index}\n\n"
                )

                f.write(
                    f"**Document ID:** "
                    f"{chunk.document_id}\n\n"
                )

                f.write(
                    f"**Page:** "
                    f"{chunk.page_number}\n\n"
                )

                # -----------------------------------------
                # Heading Path
                # -----------------------------------------

                f.write(
                    "## Heading Path\n\n"
                )

                if chunk.heading_path:

                    for heading in (
                        chunk.heading_path
                    ):
                        f.write(
                            f"- {heading}\n"
                        )

                else:

                    f.write(
                        "_No heading path_\n"
                    )

                f.write("\n")

                # -----------------------------------------
                # Block Types
                # -----------------------------------------

                f.write(
                    "## Block Types\n\n"
                )

                for block_type in (
                    chunk.block_types
                ):
                    f.write(
                        f"- {block_type}\n"
                    )

                f.write("\n")

                # -----------------------------------------
                # Image Paths
                # -----------------------------------------

                f.write(
                    "## Image Paths\n\n"
                )

                if chunk.image_paths:

                    for image_path in (
                        chunk.image_paths
                    ):
                        f.write(
                            f"- {image_path}\n"
                        )

                else:

                    f.write(
                        "_No images_\n"
                    )

                f.write("\n")

                # -----------------------------------------
                # Text
                # -----------------------------------------

                f.write(
                    "## Text\n\n"
                )

                f.write(
                    chunk.text.strip()
                )

                f.write(
                    "\n\n---\n\n"
                )

        print(
            f"Chunks written to: "
            f"{chunks_md_path}"
        )

        # =================================================
        # STEP 9
        # Generate Embeddings
        # =================================================

        print(
            "Generating embeddings..."
        )

        embeddings = (
            self.chunk_embedding_service.embed_chunks(
                chunks
            )
        )

        print(
            f"Embeddings Created: "
            f"{len(embeddings)}"
        )

        # =================================================
        # STEP 10
        # Persist EVERYTHING
        #
        # DocumentPersistenceService internally handles:
        #
        #     chunks
        #        +
        #     embeddings
        #        ↓
        #     ChunkPersistenceService
        #        ↓
        #     flush()
        #        ↓
        #     ImagePersistenceService
        #        ↓
        #     commit()
        # =================================================

        persisted_data = (
            self.document_persistence_service.persist(
                db=db,
                chunks=chunks,
                embeddings=embeddings,
            )
        )

        print(
            f"Chunks persisted: "
            f"{len(persisted_data['chunks'])}"
        )

        print(
            f"Images persisted: "
            f"{len(persisted_data['images'])}"
        )

        print(
            "Chunks and images stored "
            "successfully in PostgreSQL!"
        )

        # =================================================
        # DONE
        # =================================================

        return context






# ================= without embeddings ===============

# from app.schemas.processing_context import (
#     ProcessingContext,
# )

# from app.schemas.semantic_block import SemanticBlockType
# from app.services.marker_parser_service import (
#     MarkerParserService,
# )

# from app.services.markdown_cleaner_service import (
#     MarkdownCleanerService,
# )

# from app.services.document_service import (
#     DocumentService,
# )

# from app.models.document import (
#     DocumentStatus,
# )

# from app.services.markdown_structure_parser import (
#     MarkdownStructureParser,
# )

# from app.services.semantic_block_service import (
#     SemanticBlockService,
# )

# from app.services.chunk_service import (
#     ChunkService,
# )

# from app.services.storage_service import (
#     StorageService,
# )

# from app.services.chunk_refinement_service import (
#     ChunkRefinementService,
# )

# from app.services.document_persistence_service import (
#     DocumentPersistenceService
# )

# from app.services.chunk_persistence_service import(
#     ChunkPersistenceService
# )


# from app.services.embedding_chunk_service import(
#     ChunkEmbeddingService
# )

# from sqlalchemy.orm import Session


# class DocumentProcessingPipeline:

#     def __init__(self):

#         # -------------------------------------------------
#         # Existing processing services
#         # -------------------------------------------------

#         self.storage_service = StorageService()

#         # IMPORTANT:
#         # Marker must run BEFORE MarkdownCleanerService.
#         self.marker_parser = MarkerParserService()

#         self.cleaner = MarkdownCleanerService()

#         self.parser = MarkdownStructureParser()

#         self.semantic_block_service = (
#             SemanticBlockService()
#         )

#         self.chunk_service = ChunkService()
        
#         self.chunk_refinement_service = (
#             ChunkRefinementService()
#         )
        
#         self.document_persistence_service = (
#             DocumentPersistenceService()
#         )
        
#         self.chunk_persistence_service = (
#             ChunkPersistenceService()
#         )
#         self.chunk_embedding_service = (
#             ChunkEmbeddingService()
#         )

#     def process(
#         self,
#         db: Session,
#         context: ProcessingContext,
#     ) -> ProcessingContext:

#         print()
#         print("=" * 60)
#         print("DOCUMENT PROCESSING PIPELINE")
#         print("=" * 60)

#         # =================================================
#         # STEP 0
#         # Update document status
#         # =================================================

#         DocumentService.update_status(
#             db,
#             context.document_id,
#             DocumentStatus.PARSING,
#         )

#         print("Status Updated -> PARSING")

#         # =================================================
#         # STEP 1
#         # Create workspace
#         # =================================================

#         context = self.storage_service.create_workspace(
#             context
#         )

#         print("Workspace Created")

#         # =================================================
#         # STEP 2
#         # Run Marker
#         #
#         # This MUST happen before the markdown cleaner.
#         #
#         # Marker generates:
#         #
#         # marker_outputs/
#         #     <stored_filename_without_extension>/
#         #         markdown.md
#         #         images...
#         #
#         # It also populates context.markdown_file.
#         # =================================================

#         # print("Running Marker...")

#         # context = self.marker_parser.parse(
#         #     context
#         # )

#         # print("Marker Processing Completed")

#         # print(
#         #     f"Markdown File: "
#         #     f"{context.markdown_file}"
#         # )
        
#         print("Running Marker...", flush=True)

#         print("BEFORE MARKER PARSE", flush=True)

#         context = self.marker_parser.parse(
#             context
#         )

#         print("AFTER MARKER PARSE", flush=True)

#         print("Marker Processing Completed", flush=True)

#         # =================================================
#         # STEP 3
#         # Clean Marker Markdown
#         # =================================================

#         context = self.cleaner.clean(
#             context
#         )

#         print("Markdown Cleaned")

#         # =================================================
#         # STEP 4
#         # Parse Markdown structure
#         # =================================================

#         parsed_document = self.parser.parse(
#             markdown_path=str(
#                 context.markdown_file
#             ),
#             document_id=context.document_id,
#             stored_filename=(
#                 context.stored_filename
#             ),
#         )

#         context.parsed_document = (
#             parsed_document
#         )

#         print("Markdown Structure Parsed")

#         # =================================================
#         # STEP 5
#         # Build semantic blocks
#         # =================================================

#         semantic_blocks = (
#             self.semantic_block_service.build(
#                 parsed_document
#             )
#         )

#         context.semantic_blocks = (
#             semantic_blocks
#         )

#         print(
#             f"Semantic Blocks Created: "
#             f"{len(context.semantic_blocks)}"
#         )

#         # =================================================
#         # STEP 6
#         # Update status -> CHUNKING
#         # =================================================

#         DocumentService.update_status(
#             db,
#             context.document_id,
#             DocumentStatus.CHUNKING,
#         )

#         print("Status Updated -> CHUNKING")

#         # # =================================================
#         # # STEP 7
#         # # Build chunks
#         # # =================================================

#         chunks = (
#             self.chunk_service.build_chunks(
#                 document_id=context.document_id,
#                 semantic_blocks=semantic_blocks,
#             )
#         )
        
#         # dont need refinement for now
#         # chunks = self.chunk_refinement_service.refine(
#         #     chunks
#         # )

#         context.chunks = chunks
        
#         # =================================================
#         # Save chunks to chunks.md
#         # =================================================

#         chunks_md_path = (
#             context.workspace / "chunks.md"
#         )

#         with open(
#             chunks_md_path,
#             "w",
#             encoding="utf-8",
#         ) as f:

#             for chunk in context.chunks:

#                 f.write(
#                     f"# Chunk {chunk.chunk_index}\n\n"
#                 )

#                 f.write(
#                     f"**Document ID:** "
#                     f"{chunk.document_id}\n\n"
#                 )

#                 f.write(
#                     f"**Page:** "
#                     f"{chunk.page_number}\n\n"
#                 )

#                 # ---------------------------------------------
#                 # Heading Path
#                 # ---------------------------------------------

#                 f.write("## Heading Path\n\n")

#                 if chunk.heading_path:
#                     for heading in chunk.heading_path:
#                         f.write(
#                             f"- {heading}\n"
#                         )
#                 else:
#                     f.write(
#                         "_No heading path_\n"
#                     )

#                 f.write("\n")

#                 # ---------------------------------------------
#                 # Block Types
#                 # ---------------------------------------------

#                 f.write("## Block Types\n\n")

#                 for block_type in chunk.block_types:
#                     f.write(
#                         f"- {block_type}\n"
#                     )

#                 f.write("\n")

#                 # ---------------------------------------------
#                 # Image Paths
#                 # ---------------------------------------------

#                 f.write("## Image Paths\n\n")

#                 if chunk.image_paths:
#                     for image_path in chunk.image_paths:
#                         f.write(
#                             f"- {image_path}\n"
#                         )
#                 else:
#                     f.write(
#                         "_No images_\n"
#                     )

#                 f.write("\n")

#                 # ---------------------------------------------
#                 # Text
#                 # ---------------------------------------------

#                 f.write("## Text\n\n")

#                 f.write(
#                     chunk.text.strip()
#                 )

#                 f.write(
#                     "\n\n---\n\n"
#                 )
        
#         print(
#             f"Chunks written to: "
#             f"{chunks_md_path}"
#         )

        
#         # calling the document persistence to store chunks and images into the db tables
#         stored_documents = self.document_persistence_service.persist(
#             db,chunks
#         )


#         print(f"Chunks and images stored succesfully in the db tables!!")
        
#         return context

