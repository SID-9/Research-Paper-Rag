from app.services.markdown_structure_parser import (
    MarkdownStructureParser,
)


def main():

    markdown_path = (
        r"D:\Full Stack Projects\AI_ASSISTANT_KNOWLEDGE_STORAGE\marker_outputs\28c14d6f-7ec8-496e-a4db-79d52e457b10\markdown.md"
    )

    parser = MarkdownStructureParser()

    parsed_document = parser.parse(
        markdown_path=markdown_path,
        document_id=44,
        stored_filename="attention is all you need.pdf",
    )

    print()
    print("=" * 80)
    print("PARSED DOCUMENT")
    print("=" * 80)

    print(
        f"Document ID : {parsed_document.document_id}"
    )

    print(
        f"Total Blocks: {parsed_document.total_blocks}"
    )

    print()

    for block in parsed_document.blocks:

        print("-" * 80)

        print(
            f"Block Index : {block.block_index}"
        )

        print(
            f"Type        : {block.block_type.value}"
        )

        print(
            f"Page        : {block.page_number}"
        )

        if block.heading_text:

            print(
                f"Heading     : {block.heading_text}"
            )

            print(
                f"Level       : {block.heading_level}"
            )

        if block.image_path:

            print(
                f"Image       : {block.image_path}"
            )

        if block.text:

            print(
                f"Text        : {block.text[:500]}"
            )

    print("=" * 80)


if __name__ == "__main__":
    main()