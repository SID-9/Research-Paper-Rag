import UploadForm from "../components/documents/UploadForm";
import DocumentList from "../components/documents/DocumentList";

import useDocuments from "../hooks/useDocuments";
import Header from "../components/layout/Header";
import Card from "../components/ui/Card";

export default function DashboardPage() {

    const {

        documents,

        loading,

        upload,

        deleteDocument,

        downloadDocument

    } = useDocuments();

    return (

        <div className="min-h-screen bg-slate-100">

            <Header/>

            <main className="mx-auto max-w-6xl p-8">

                <Card>

                    <h2 className="text-2xl font-bold text-slate-900">

                        Welcome back!

                    </h2>

                    <p className="mt-3 text-slate-600">

                        You are successfully authenticated.

                    </p>

                    <div className="space-y-8">

                        <UploadForm

                            upload={upload}

                        />

                        <div>

                            <h2 className="text-2xl font-bold mb-4">

                                My Documents 🚀

                            </h2>

                            <DocumentList

                                documents={documents}

                                loading={loading}

                                onDelete={deleteDocument}

                                onDownload={downloadDocument}

                            />

                        </div>

                    </div>
                </Card>

            </main>

        </div>


    );

}




//=======================================================

// import Header from "../components/layout/Header";
// import Card from "../components/ui/Card";

// /**
//  * Dashboard Page
//  *
//  * First protected page.
//  *
//  * Later this page will contain:
//  *
//  * - Upload
//  * - Documents
//  * - Chat
//  * - Search
//  */
// export default function DashboardPage() {

//     return (

//         <div className="min-h-screen bg-slate-100">

//             <Header />

//             <main className="mx-auto max-w-6xl p-8">

//                 <Card>

//                     <h2 className="text-2xl font-bold text-slate-900">

//                         Welcome back!

//                     </h2>

//                     <p className="mt-3 text-slate-600">

//                         You are successfully authenticated.

//                     </p>

//                     <div className="mt-8 rounded-lg border border-dashed border-slate-300 p-8">

//                         <p className="text-center text-slate-500">

//                             🚀

//                             <br /><br />

//                             Document Upload Module

//                             <br />

//                             Coming Next...

//                         </p>

//                     </div>

//                 </Card>

//             </main>

//         </div>

//     );

// }