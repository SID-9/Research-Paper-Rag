import Input from "../ui/Input";

interface UploadZoneProps {

    selectedFiles: File[];

onFilesChange: (
    files: File[]
)=>void;

}

/**
 * Upload Zone
 *
 * Responsible ONLY for selecting
 * a file.
 *
 * No upload logic.
 */

export default function UploadZone({

    selectedFiles,

    onFilesChange

}: UploadZoneProps) {

    function handleChange(

    event: React.ChangeEvent<HTMLInputElement>

){

    const files =

        Array.from(

            event.target.files ?? []

        );

    onFilesChange(files);

}

    return (

        <div className="space-y-4">

            <Input
            label="Select a PDF file"

    type="file"

    accept=".pdf"

    multiple

    onChange={handleChange}

/>

            {selectedFiles.map(file=>(

    <div
        key={file.name}
        className="rounded-md border p-3"
    >

        <p>{file.name}</p>

        <p>

            {(file.size/1024).toFixed(2)} KB

        </p>

    </div>

))}

        </div>

    );

}