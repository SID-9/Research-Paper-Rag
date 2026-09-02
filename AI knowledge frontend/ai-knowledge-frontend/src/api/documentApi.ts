import api from "./axios";

import type {
    Document,
    UploadDocumentResponse
}from "../types/document";

/**
 * Document API
 *
 * Contains every HTTP request
 * related to documents.
 *
 * Components NEVER call Axios directly.
 */


const documentAPi = {

    // upload pdf , post /documents/upload

    async upload(file: File): Promise<UploadDocumentResponse>{

        const formData = new FormData();
        formData.append("file",file);

        const response = await api.post<UploadDocumentResponse>(
            "/documents/upload",
            formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            }
    );
        return response.data;

},

// list docs , GET /documents

async getDocuments(): Promise<Document[]>{

    const response = await api.get<Document[]>("/documents");
    return response.data;
},

// delete documents /documents/{id}

async deleteDocument(documentId: number):Promise<void>{
    await api.delete(`/documents/${documentId}`);
},

// download document GET /documents/{id}

/**
 * Download Document
 */

async downloadDocument(
    documentId: number,
    filename: string
): Promise<void> {

    const response = await api.get(

        `/documents/${documentId}`,

        {
            responseType: "blob"
        }

    );

    // Create temporary URL

    const url = window.URL.createObjectURL(response.data);

    // Create temporary anchor element

    const link = document.createElement("a");

    link.href = url;

    link.download = filename;

    document.body.appendChild(link);

    link.click();

    link.remove();

    window.URL.revokeObjectURL(url);

}

};

export default documentAPi;



