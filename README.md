# Research Paper Intelligence Platform

A production-oriented RAG platform for uploading, processing, and querying research papers using a scalable Spring Boot–FastAPI architecture.

## Overview

Research Paper Intelligence Platform is a full-stack application designed to help users organize and interact with research papers through AI-powered document understanding and retrieval.

Users can create an account, upload multiple research papers, and query selected documents through a context-aware Q&A system.

The application separates backend responsibilities from AI processing, allowing document ingestion and AI processing to operate independently and asynchronously.

## Architecture

```text
                    ┌──────────────────┐
                    │   React Frontend │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Spring Boot API │
                    │                  │
                    │ Authentication   │
                    │ Document APIs    │
                    │ User Management  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      Redis       │
                    │    Job Queue     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ FastAPI AI       │
                    │ Processing       │
                    │                  │
                    │ Document Parsing │
                    │ Chunking         │
                    │ Embeddings       │
                    │ Metadata         │
                    │ Retrieval        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │                  │
                    │ Documents       │
                    │ Chunks           │
                    │ Embeddings       │
                    │ Metadata         │
                    │ User Data       │
                    └──────────────────┘
```

## Key Features

* User registration and authentication
* Secure document management
* Multiple research paper uploads
* Asynchronous document processing
* Redis-based job orchestration
* Automated document processing and indexing
* Text chunking and embedding generation
* Metadata and document information storage
* Document-specific RAG-based Q&A
* Modular Spring Boot backend
* Independent FastAPI AI processing service
* PostgreSQL-based persistent storage

## Backend

The Spring Boot service is responsible for the application's core business logic and API layer.

It handles:

* User authentication and authorization
* Document upload and management
* Request validation
* Job creation and orchestration
* Database interactions
* Q&A API requests
* DTO-based API contracts
* Entity-to-DTO mapping
* Centralized exception handling
* Relational data modeling

The backend follows a modular layered architecture to keep controllers, services, repositories, DTOs, mappers, and domain models separated.

## AI Processing Pipeline

The AI processing service is implemented independently using FastAPI.

Once a document processing job is created, the AI service consumes the job and performs the required document processing workflow.

The pipeline includes:

1. Document ingestion
2. Document parsing
3. Text extraction
4. Chunk generation
5. Embedding generation
6. Metadata extraction
7. Persistence of processed information
8. Retrieval during Q&A

This separation allows the AI processing workload to evolve independently from the core application backend.

## Asynchronous Processing

Document processing can be computationally expensive, especially when users upload multiple research papers.

Instead of keeping the upload request active while processing documents, the Spring Boot backend creates a processing job in Redis.

```text
User Upload
     │
     ▼
Spring Boot
     │
     ▼
Create Job
     │
     ▼
Redis Queue
     │
     ▼
FastAPI Worker
     │
     ├── Parse
     ├── Chunk
     ├── Embed
     └── Store
          │
          ▼
      PostgreSQL
```

This allows document uploads and processing to be decoupled and prevents long-running AI workloads from blocking the main API request.

## Q&A Flow

Users can select a processed research paper and submit questions against it.

```text
User Question
      │
      ▼
Spring Boot API
      │
      ▼
Retrieval Pipeline
      │
      ├── Query Processing
      ├── Relevant Chunk Retrieval
      └── Context Construction
                │
                ▼
          LLM Response
                │
                ▼
              User
```

The system uses the selected document as the retrieval scope, allowing users to ask questions based on the content of their uploaded research papers.

## Technology Stack

### Backend

* Java
* Spring Boot
* Spring Security
* REST APIs
* JPA/Hibernate
* MapStruct

### AI / RAG

* Python
* FastAPI
* RAG
* Embeddings
* Vector Retrieval
* Document Processing

### Data & Infrastructure

* PostgreSQL
* Redis
* Docker

### Frontend

* React

## Project Structure

The project is organized as separate backend and AI-processing services.

```text
research-paper-rag/
│
├── backend/
│   └── spring-boot-application/
│
├── ai-service/
│   └── fastapi-application/
│
├── frontend/
│   └── react-application/
│
└── README.md
```

Each service is independently structured to keep responsibilities isolated and make the system easier to maintain and extend.

## Future Improvements

Planned features include:

* AI-generated research reports
* Interactive report editing
* Research insights and visualizations
* Cross-paper analysis
* Comparative analysis across multiple papers
* Enhanced conversational Q&A
* Additional retrieval and evaluation strategies

## Project Status

**Backend:** Complete first version
**AI Processing Pipeline:** Functional
**RAG Q&A:** Functional
**Frontend:** Under development

This project is actively being developed, with additional AI-powered research and reporting capabilities planned for future versions.

## Author

**Siddharth Upadhyay**

Built as a personal project to explore production-oriented backend architecture, asynchronous AI processing, and end-to-end RAG application development.
