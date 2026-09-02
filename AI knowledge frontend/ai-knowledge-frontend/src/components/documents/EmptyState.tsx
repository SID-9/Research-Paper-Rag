import Card from "../ui/Card";

export default function EmptyState() {

    return (

        <Card>

            <div className="text-center py-8">

                <h2 className="text-lg font-semibold">

                    No Documents

                </h2>

                <p className="text-slate-500 mt-2">

                    Upload your first PDF to get started.

                </p>

            </div>

        </Card>

    );

}