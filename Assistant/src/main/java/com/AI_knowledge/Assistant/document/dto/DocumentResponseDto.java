package com.AI_knowledge.Assistant.document.dto;

import com.AI_knowledge.Assistant.enums.DocumentStatus;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
public class DocumentResponseDto {

    private Long id;
    private String originalFilename;
    private Long fileSize;
    private String contentType;
    private LocalDateTime uploadedAt;
    private DocumentStatus status;

}
