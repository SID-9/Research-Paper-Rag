import traceback

from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.core.config import settings

from app.models.document import DocumentStatus
from app.services.document_service import DocumentService

from app.schemas.processing_job import DocumentProcessingJob
from app.schemas.processing_context import ProcessingContext

from app.pipelines.document_processing_pipeline import (
    DocumentProcessingPipeline,
)


QUEUE_NAME = settings.QUEUE_NAME


def start_worker():

    print("=" * 60)
    print("Document Processing Worker Started")
    print("Waiting For Jobs...")
    print("=" * 60)

    pipeline = DocumentProcessingPipeline()

    while True:

        try:

            result = redis_client.blpop(
                QUEUE_NAME,
                timeout=0,
            )

            if result is None:
                continue

            _, job = result

            payload = DocumentProcessingJob.model_validate_json(
                job
            )

            print("=" * 60)
            print("Received Processing Job")
            print("=" * 60)

            print(f"Document ID   : {payload.documentId}")
            print(f"User ID       : {payload.userId}")
            print(f"Original File : {payload.originalFilename}")
            print(f"Stored File   : {payload.storedFilename}")
            print(f"File Path     : {payload.filePath}")

            context = ProcessingContext(
                document_id=payload.documentId,
                user_id=payload.userId,
                original_filename=payload.originalFilename,
                stored_filename=payload.storedFilename,
                file_path=payload.filePath,
            )

            # -------------------------------------------------
            # One DB session per job
            # -------------------------------------------------

            db = SessionLocal()

            try:

                # Pipeline performs all DB updates inside
                # this transaction.
                pipeline.process(
                    db=db,
                    context=context,
                )

                # Commit only when the entire pipeline succeeds.
                db.commit()

                print("=" * 60)
                print(
                    f"Document {context.document_id} "
                    "processed successfully"
                )
                print("=" * 60)

            except Exception as e:

                # Roll back the failed processing transaction.
                db.rollback()

                print("=" * 60)
                print(
                    f"Document processing failed: "
                    f"{context.document_id}"
                )
                print(f"Error: {e}")
                print("=" * 60)

                traceback.print_exc()

                # -------------------------------------------------
                # IMPORTANT:
                # FAILED must be saved using a new transaction.
                # The previous transaction was rolled back.
                # -------------------------------------------------

                try:

                    failed_db = SessionLocal()

                    try:

                        DocumentService.update_status(
                            failed_db,
                            context.document_id,
                            DocumentStatus.FAILED,
                        )

                        failed_db.commit()

                    except Exception:
                        failed_db.rollback()
                        raise

                    finally:
                        failed_db.close()

                except Exception:

                    print(
                        "CRITICAL: Failed to update document "
                        "status to FAILED"
                    )

                    traceback.print_exc()

            finally:

                db.close()

        except KeyboardInterrupt:

            print("\nStopping Worker...")
            break

        except Exception as e:

            # Errors outside the actual processing transaction.
            print("=" * 60)
            print(f"Worker Error: {e}")
            print("=" * 60)

            # traceback.print_exc()




#===============================
# import json
# import traceback

# from app.core.database import SessionLocal
# from app.core.redis_client import redis_client

# from app.models.document import DocumentStatus
# from app.services.document_service import DocumentService
# from app.schemas.processing_job import DocumentProcessingJob
# from app.schemas.processing_context import ProcessingContext

# from app.core.config import settings

# from app.pipelines.document_processing_pipeline import(
#     DocumentProcessingPipeline
# )

# QUEUE_NAME = settings.QUEUE_NAME

# def start_worker():
    
#     print("=" * 60)
#     print("Worker Started")
#     print("Waiting For Jobs...")
#     print("=" * 60)
    
#     pipeline = DocumentProcessingPipeline()
       
#     while True:
        
#         try:
#             result = redis_client.blpop(
#                 QUEUE_NAME,
#                 timeout=0
#             )
            
#             if result is None:
#                 continue
            
            
#             _,job = result
#             payload = (
#                 DocumentProcessingJob.model_validate_json(job)
#             )
            
#             print("=" * 60)
#             print("Received Processing Job")
#             print("=" * 60)

#             print(f"Document ID      : {payload.documentId}")
#             print(f"User ID          : {payload.userId}")
#             print(f"Original File    : {payload.originalFilename}")
#             print(f"Stored File      : {payload.storedFilename}")
#             print(f"File Path        : {payload.filePath}")
            
#             context = ProcessingContext(
#                 document_id=payload.documentId,
#                 user_id=payload.userId,
#                 original_filename=payload.originalFilename,
#                 stored_filename=payload.storedFilename,
#                 file_path=payload.filePath
#             )
            
            
#             db = SessionLocal()
            
#             try:
                
#                 pipeline.process(
#                     db,
#                     context
#                 )
                
#             finally:
#                 db.close()
            
            
            
#         except KeyboardInterrupt:
            
#             print("\nStopping Worker...")
#             break

#         except Exception as e:
#             # import traceback
#             # traceback.print_exc()
#             # raise

#             print(f"Worker Error : {e}")


