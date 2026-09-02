package com.AI_knowledge.Assistant.document.queue.publisher;

import com.AI_knowledge.Assistant.document.dto.DocumentProcessingJob;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

@Service
public class QueuePublisherImpl implements QueuePublisher {

    private final String QUEUE_NAME="document_queue";

    private final RedisTemplate<String, String> redisTemplate;

    private final ObjectMapper objectMapper;

    public QueuePublisherImpl(RedisTemplate<String, String> redisTemplate, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
    }

    @Override
    public void publish(DocumentProcessingJob job) {
        try {
            String payload = objectMapper.writeValueAsString(job);

            redisTemplate.opsForList().leftPush(QUEUE_NAME, payload);

            System.out.println("Published Job: " + job.getDocumentId());

        } catch (JsonProcessingException e) {
            throw new IllegalStateException("Failed to serialize DocumentProcessingJob", e);
        }
    }
}
