package com.AI_knowledge.Assistant.document.dto;

import lombok.*;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class DocumentProcessingJob {
    private Long documentId;
    private Long userId;
    private String filePath;
    private String originalFilename;
    private String storedFilename;


}
