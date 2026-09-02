import { useCallback, useEffect, useState } from "react";

import type { Document } from "../types/document";
import documentApi from "../api/documentApi";

/**
 * Document Hook
 *
 * Encapsulates every piece of
 * document-related state.
 *
 * UI Components should never
 * directly call documentApi.
 */



/**
 * Document processing states for which the backend
 * may still be working on the document.
 *
 * As long as at least one document is in one of these
 * states, the frontend will periodically refresh the
 * document list.
 */
const PROCESSING_STATUSES = new Set([
     "UPLOADED",
     "QUEUED",
     "PARSING",
     "CHUNKING",
     "EMBEDDING",
]);

const POLLING_INTERVAL = 3000; // ms so 3 sec

export default function useDocuments(){

    const[documents, setDocuments] = useState<Document[]>([]);
    const [loading , setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // fetch all documents

    const fetchDocuments = useCallback(async (showLoading=true)=>{

        try{
            if(showLoading){

                setLoading(true);
            }
            setError(null);
            const data = await documentApi.getDocuments();
            setDocuments(data);
        }catch{
            setError("Failed to load documents");
        }finally{
            if(showLoading){

                setLoading(false);
            }
        }

    }, []);

    // uplaod a new document

    async function upload(files: File[]){
        await Promise.all(

    files.map(file=>

        documentApi.upload(file)

    )

);
        await fetchDocuments();
    }

    // delete a document
    async function deleteDocument(documentId: number){
        await documentApi.deleteDocument(documentId);
        await fetchDocuments();
    }

    //download a document
    async function downloadDocument(documentId: number, OriginalFilename: string){
        return await documentApi.downloadDocument(documentId, OriginalFilename);
        
    }

    // initial load
    useEffect(()=>{
        fetchDocuments();

    },[fetchDocuments]);

    const hasProcessingDocuments = documents.some(
        document => PROCESSING_STATUSES.has(document.status)
    );

    // poll spingboot while one o rmore docs are still processing
    useEffect(()=>{
        // if there are no docs bieng processed there is nothing to poll
        if(!hasProcessingDocuments){
            return;
        }

        // else start the backgournd polling every 3 secs and fetch the latest data
        const intervalId = window.setInterval(()=>{
            fetchDocuments(false);
        }, POLLING_INTERVAL);
         /**
         * Cleanup function.
         *
         * React executes this when:
         *
         * - the component unmounts
         * - polling is no longer necessary
         *
         * This prevents an abandoned interval from continuing
         * to make HTTP requests.
         */
        return () => {

            window.clearInterval(intervalId);

        };

    }, [hasProcessingDocuments, fetchDocuments]);

    return{
        documents,
        loading,
        error,
        upload,
        deleteDocument,
        downloadDocument,
        refreshDocuments: fetchDocuments
    };


}

/* 

we purposely dont use the ready , failed status because we want to keep polling until all documents are either ready or failed
and if we put  ready and failed too then it will never stop polling bcz our logic is that if any document is in any one of the 
processing states as defined by us and it matches the backend states then we will keep polling so once the backend status 
changes to ready or failed then the condition becomes false and we will stop polling and cleanup the interval.

note : what does unmounting of component mean ? it means that the component is no longer being rendered on the screen and it is 
removed from the DOM. so we need to cleanup the interval when the component is unmounted to prevent memory leaks and unnecessary
network requests. This could happend if we move away from our documents page to like settings page etc.

hasProcessingDocuments = true
        ↓
setInterval()
        ↓
poll every 3 seconds
        ↓
backend eventually says READY
        ↓
setDocuments()
        ↓
hasProcessingDocuments = false
        ↓
cleanup runs
        ↓
clearInterval()
        ↓
STOP POLLING

why loading isn't activated during polling
This is a subtle but very production-important UX decision.
Imagine we did this every 3 seconds:

setLoading(true);
GET /documents
setLoading(false);

Your dashboard might constantly do:
Documents
   ↓
Loading...
   ↓
Documents
   ↓
Loading...
   ↓
Documents
   ↓
Loading...
💀
The user would think the application is constantly refreshing.

*/

