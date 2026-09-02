import { useState } from "react";

import Button from "../ui/Button";
import Card from "../ui/Card";
import UploadZone from "./UploadZone";

// import useDocuments from "../../hooks/useDocuments";

/**
 * Upload Form
 *
 * Responsible for:
 *
 * - keeping selected file
 * - validating selection
 * - triggering upload
 */

type UploadFormProps = {
    upload: (files: File[]) => Promise<void>;
};

export default function UploadForm({
    upload,
}: UploadFormProps) {

    // const {

    //     upload

    // } = useDocuments();

const [

    selectedFiles,

    setSelectedFiles

]

=

useState<File[]>([]);



    const [

        uploading,

        setUploading

    ] = useState(false);

    const [

        error,

        setError

    ] = useState<string | null>(null);

    async function handleUpload() {

        if(selectedFiles.length===0){

    setError(

        "Please select at least one PDF."

    );

    return;

}

        try {

            setUploading(true);

            setError(null);

            await upload(selectedFiles);

            setSelectedFiles([]);

        }

        catch {

            setError("Upload failed.");

        }

        finally {

            setUploading(false);

        }

    }

    return (

        <Card>

            <h2 className="mb-6 text-xl font-semibold">

                Upload PDF

            </h2>

            <UploadZone

                selectedFiles={selectedFiles}

                onFilesChange={setSelectedFiles}

            />

            {error && (

                <p className="mt-4 text-sm text-red-600">

                    {error}

                </p>

            )}

            <div className="mt-6">

                <Button

                    onClick={handleUpload}

                    disabled={uploading}

                >

                    {uploading

                        ? "Uploading..."

                        : "Upload"}

                </Button>

            </div>

        </Card>

    );

}