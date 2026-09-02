import DocumentCard from "./DocumentCard";
import EmptyState from "./EmptyState";
import type { Document } from "../../types/document";

interface DocumentListProps {

    documents: Document[];

    loading: boolean;

    onDelete: (id: number) => void;

    onDownload: (
    id:number,
    filename:string
)=>void

}

export default function DocumentList({

    documents,

    loading,

    onDelete,

    onDownload

}: DocumentListProps) {

    if (loading) {

        return (

            <p className="text-slate-500">

                Loading documents...

            </p>

        );

    }

    if (documents.length === 0) {

        return <EmptyState />;

    }

    return (

        <div className="space-y-4">

            {documents.map(document => (

                <DocumentCard

                    key={document.id}

                    document={document}

                    onDelete={onDelete}

                    onDownload={onDownload}

                />

            ))}

        </div>

    );

}