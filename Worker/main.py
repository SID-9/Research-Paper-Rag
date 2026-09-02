from app.core.redis_client import redis_client
from app.core.database import engine
from app.workers.document_worker import start_worker
from app.models import *
from fastapi import FastAPI
from app.api.retrieval import router as retrieval_router
from app.api.qa import (
    router as qa_router,
)

app = FastAPI()

app.include_router(
    retrieval_router
)
app.include_router(
    qa_router
)

def main():

    print("=" * 60)
    print("Starting AI Worker")
    print("=" * 60)

    try:
        
        with engine.connect():
            print("Connected to PostgreSQL")

        if redis_client.ping():
            print("Connected to Redis\n")
            print()
            start_worker()

    except Exception as e:
        print(f"Startup Failed : {e}")


if __name__ == "__main__":
    main()