from app.schemas.retrieval import RetrievalResult


class ContextBuilderService:

    def build_context(
        self,
        results: list[RetrievalResult],
    ) -> str:

        if not results:
            return ""

        sections = []

        for result in results:

            heading = (
                " > ".join(result.heading_path)
                if result.heading_path
                else "No heading"
            )

            section = (
                f"[Source Chunk {result.chunk_id}]\n"
                f"Document ID: {result.document_id}\n"
                f"Page: {result.page_number}\n"
                f"Heading: {heading}\n\n"
                f"{result.text}"
            )

            sections.append(section)

        return "\n\n---\n\n".join(sections)