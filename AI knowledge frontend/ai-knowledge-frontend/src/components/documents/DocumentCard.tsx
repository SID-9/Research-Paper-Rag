import Button from "../ui/Button";
import Card from "../ui/Card";

import type { Document } from "../../types/document";

interface DocumentCardProps {

    document: Document;

    onDelete: (id: number) => void;

    onDownload: (
    id: number,
    filename: string
) => void;

}

export default function DocumentCard({

    document,

    onDelete,

    onDownload

}: DocumentCardProps) {

    // document status update

    // a doc is considered ready when the entire doc processing pipeline has completed
    const isReady = document.status === "READY";

    // doc is still in an intermediate steps 
    const isProcessing = 
        document.status === "UPLOADED"||
        document.status === "QUEUED" ||
        document.status === "PARSING" || 
        document.status === "CHUNKING" || 
        document.status === "EMBEDDING";        

    // a failed doc has reached terminal state 
    const isFailed = document.status === "FAILED";

    // =========================================================
    // STATUS DISPLAY
    // =========================================================

    /**
     * Convert backend status into human-readable UI text.
     *
     * The backend should continue returning machine-friendly
     * values such as "CHUNKING".
     *
     * The frontend decides how that state should be presented
     * to the user.
     */

    function getStatusLabel(): string{
        switch(document.status){
            case "UPLOADED":
                return "Uploaded";
             case "QUEUED":
                return "Queued for processing";

            case "PARSING":
                return "Parsing document";

            case "CHUNKING":
                return "Creating document chunks";

            case "EMBEDDING":
                return "Generating embeddings";

            case "READY":
                return "Ready";

            case "FAILED":
                return "Processing failed";

            default:
                return "Unknown status";
        }
    }

    // determining the visual style of the status indicator
    function getStatusClassName(): string{
        if(isReady){
            return "text-green-600";
        }
        if(isFailed){
            return "text-red-600";
        }
        if(isProcessing){
            return "text-amber-600";
        }
        return "text-slate-500";
    }


    return (

        <Card>

            <div className="flex items-center justify-between gap-6">

                <div className="min-w-0">

                    <h3 className="font-semibold truncate">

                        {document.originalFilename}

                    </h3>

                    <p className="text-sm text-slate-500 mt-1">

                        PDF • {(document.fileSize / 1024).toFixed(2)} KB

                    </p>

                    <div
                    className={`flex items-center gap-2 text-sm mt-2 ${getStatusClassName()}`}>
                        {/* processing indicator */}
                        {isProcessing && (
                            <span
                            className="inline-block h-2 w-2 rounded-full bg-amber-500 animate-pulse"
                            aria-hidden="true"
                            />
                        )}

                        {/* failed indicator */}
                        {isReady && (
                            <span
                                className="inline-block h-2 w-2 rounded-full bg-green-500"
                                aria-hidden="true"
                            />

                        )}

                        {/* failed indicator */}
                        {isFailed && (
                            <span
                                className="inline-block h-2 w-2 rounded-full bg-red-500"
                                aria-hidden="true"
                            />
                        )}

                        <span>
                            {getStatusLabel()}
                        </span>

                    </div>

                </div>

                <div className="flex gap-2 shrink-0">

                    <Button

                        onClick={() =>

                            onDownload(
    document.id,
    document.originalFilename
)

                        }

                    >

                        Download

                    </Button>

                    {/* CHAT BUTTON  */}
                    {isReady && (
                        <Button>
                            Chat
                        </Button>
                    )}

                    <Button

                        variant="danger"

                        onClick={() => {
                            onDelete(document.id);
                        }}

                    >

                        Delete

                    </Button>

                </div>

            </div>

        </Card>

    );

}