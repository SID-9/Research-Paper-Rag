// ==========================================================
// Document Types
// ==========================================================

/**
 * Represents one document displayed
 * inside the dashboard.
 *
 * Mirrors DocumentResponseDto
 * returned from:
 *
 * GET /documents
 */
export interface Document {
    id: number;
    originalFilename: string;
    fileSize: number;
    contentType: string;
    uploadedAt: string;
    status: DocumentStatus;
}

/**
 * Response returned after a successful upload.
 *
 * Mirrors UploadDocumentResponseDto
 * returned from:
 *
 * POST /documents/upload
 */
export type UploadDocumentResponse = Document;

// doc status update
/**
 * Represents every processing state a document can have
 * throughout its lifecycle.
 *
 * The values MUST match the enum values returned by
 * the Spring Boot backend.
 * This is a TypeScript union type.
We're telling TypeScript:

DocumentStatus can ONLY be one of these seven strings
 * 
 */
export type DocumentStatus =
    | "UPLOADED"
    | "QUEUED"
    | "PARSING"
    | "CHUNKING"
    | "EMBEDDING"
    | "READY"
    | "FAILED";