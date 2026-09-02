package com.AI_knowledge.Assistant.document.queue.publisher;

import com.AI_knowledge.Assistant.document.dto.DocumentProcessingJob;
import com.fasterxml.jackson.core.JsonProcessingException;

public interface QueuePublisher {
    void publish(DocumentProcessingJob job) ;
}
