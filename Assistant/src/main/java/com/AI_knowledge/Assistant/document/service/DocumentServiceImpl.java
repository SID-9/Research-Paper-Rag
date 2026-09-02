package com.AI_knowledge.Assistant.document.service;

import com.AI_knowledge.Assistant.document.dto.DocumentProcessingJob;
import com.AI_knowledge.Assistant.document.dto.DocumentResponseDto;
import com.AI_knowledge.Assistant.document.mapper.DocumentMapper;
import com.AI_knowledge.Assistant.document.queue.publisher.QueuePublisher;
import com.AI_knowledge.Assistant.document.storage.FileStorageProperties;
import com.AI_knowledge.Assistant.document.storage.StorageService;
import com.AI_knowledge.Assistant.enums.DocumentStatus;
import com.AI_knowledge.Assistant.model.Document;
import com.AI_knowledge.Assistant.model.User;
import com.AI_knowledge.Assistant.repository.DocumentRepository;
import com.AI_knowledge.Assistant.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Paths;
import java.util.List;

@Service
public class DocumentServiceImpl implements DocumentService{

    @Autowired
    private DocumentRepository documentRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private StorageService storageService;

    @Autowired
    private DocumentMapper documentMapper;

    @Autowired
    private FileStorageProperties properties;

    @Autowired
    private QueuePublisher queuePublisher;

    @Override
    public DocumentResponseDto uploadDocument(MultipartFile file, Long userId) {

        User owner = userRepository.findById(userId)
                .orElseThrow(()-> new RuntimeException("User does not exist"));

        String storedFilename = storageService.store(file);

        Document document = Document.builder()
                .originalFilename(file.getOriginalFilename())
                .storedFilename(storedFilename)
                .contentType(file.getContentType())
                .fileSize(file.getSize())
                .filePath(
                        Paths.get(
                                properties.getUploadDir(),
                                storedFilename
                        ).toString()
                )
                .owner(owner)
                .status(DocumentStatus.UPLOADED)
                .build();

        documentRepository.save(document);

        return documentMapper.toDto(document);
    }


    @Override
    public String documentProcessingQueue(DocumentResponseDto response) {

        Document document = documentRepository.findById(response.getId())
                .orElseThrow(()-> new RuntimeException("File not found"));

        // adding the job to redis queue to be picked up by fastapi service
        DocumentProcessingJob job = DocumentProcessingJob.builder()
                .documentId(document.getId())
                .userId(document.getOwner().getId())
                .filePath(document.getFilePath())
                .originalFilename(document.getOriginalFilename())
                .storedFilename(document.getStoredFilename())
                .build();

        // change the status of the document from uploaded to queued right before you add it to the redis queue and save it agian
        document.setStatus(DocumentStatus.QUEUED);
        documentRepository.save(document);

        queuePublisher.publish(job);

        return "Job Published";
    }


    @Override
    public List<DocumentResponseDto> getMyDocuments(Long userId) {

        User owner = userRepository.findById(userId)
                .orElseThrow(()-> new RuntimeException("User not found"));

        return documentRepository.findByOwner(owner)
                .stream()
                .map(documentMapper::toDto)
                .toList();
    }

    @Override
    public Resource downloadDocument(Long documentId, Long userId) {

        Document document = documentRepository .findById(documentId)
                .orElseThrow(()-> new RuntimeException("Document not found"));

        if(!document.getOwner().getId().equals(userId)){
            throw new RuntimeException("Access Denied");
        }

        return storageService.loadAsResource(document.getStoredFilename());
    }

    @Override
    public void deleteDocument(Long documentId, Long userId) {

        Document document = documentRepository.findById(documentId)
                .orElseThrow(()-> new RuntimeException("Document not found"));

        if(!document.getOwner().getId().equals(userId)){
            throw new RuntimeException("Access Denied");
        }

        storageService.delete(document.getStoredFilename());
        documentRepository.delete(document);

        /*notice the order:
        Delete file
            ↓
        Delete DB row*/

    }


}
