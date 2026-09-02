package com.AI_knowledge.Assistant.document.service;

import com.AI_knowledge.Assistant.document.dto.DocumentResponseDto;
import org.springframework.core.io.Resource;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface DocumentService {
    DocumentResponseDto uploadDocument(
            MultipartFile file,
            Long userId
    );

    List<DocumentResponseDto> getMyDocuments(Long userId);

    Resource downloadDocument(
            Long documentId,
            Long userId
    );

    void deleteDocument(
            Long documentId,
            Long userId
    );

    String documentProcessingQueue(DocumentResponseDto response);
}
