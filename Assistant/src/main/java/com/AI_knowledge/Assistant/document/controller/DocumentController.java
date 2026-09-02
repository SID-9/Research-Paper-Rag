package com.AI_knowledge.Assistant.document.controller;

import com.AI_knowledge.Assistant.auth.security.UserDetailsImpl;
import com.AI_knowledge.Assistant.document.dto.DocumentProcessingJob;
import com.AI_knowledge.Assistant.document.dto.DocumentResponseDto;
import com.AI_knowledge.Assistant.document.queue.publisher.QueuePublisher;
import com.AI_knowledge.Assistant.document.service.DocumentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/documents")
public class DocumentController {

    @Autowired
    private DocumentService documentService;

    @Autowired
    private QueuePublisher queuePublisher;


    // upload a document

    @PostMapping(
            value="/upload",
            consumes = MediaType.MULTIPART_FORM_DATA_VALUE
    )
    public ResponseEntity<DocumentResponseDto> uploadDocument(
            @RequestParam("file")MultipartFile file,
            @AuthenticationPrincipal UserDetailsImpl user
            ){

        DocumentResponseDto response = documentService.uploadDocument(file, user.getId());
        // adding the document to the redis queue as a job to be picked up by fastapi service
        String jobQueue = documentService.documentProcessingQueue(response);
        return ResponseEntity.ok(response);

    }

    // get all documents uploaded by the current user
    @GetMapping
    public ResponseEntity<List<DocumentResponseDto>> getMyDocuments(
            @AuthenticationPrincipal UserDetailsImpl user
    ){

        List<DocumentResponseDto> response = documentService.getMyDocuments(user.getId());
        return ResponseEntity.ok(response);
    }

    // download a document
    @GetMapping("/{documentId}")
    public ResponseEntity<Resource> downloadDocument(
            @PathVariable Long documentId,
            @AuthenticationPrincipal UserDetailsImpl user
    ){

        Resource resource = documentService.downloadDocument(documentId, user.getId());
        return ResponseEntity.ok()
                .header(
                        HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\""+
                                resource.getFilename()+
                                 "\""
                ).body(resource);

    }

    // delete a document
    @DeleteMapping("/{documentId}")
    public ResponseEntity<String> deleteDocument(
            @PathVariable Long documentId,
            @AuthenticationPrincipal UserDetailsImpl user
    ){

        documentService.deleteDocument(documentId, user.getId());

        return ResponseEntity.ok("Document deleted successfully.");

    }


    // testing redis
    @PostMapping("/test-queue")
    public String testQueue() {

        DocumentProcessingJob job =
                DocumentProcessingJob.builder()
                        .documentId(999L)
                        .userId(1L)
                        .filePath("test.pdf")
                        .build();

        queuePublisher.publish(job);

        return "Job Published";
    }


}
