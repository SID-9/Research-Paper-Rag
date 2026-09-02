package com.AI_knowledge.Assistant.repository;

import com.AI_knowledge.Assistant.model.Document;
import com.AI_knowledge.Assistant.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DocumentRepository extends JpaRepository<Document,Long> {
    List<Document> findByOwner(User owner);
}
