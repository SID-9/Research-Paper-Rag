package com.AI_knowledge.Assistant.model;

import com.AI_knowledge.Assistant.enums.DocumentStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Table(name="documents")
@Builder
public class Document {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * Original filename uploaded by user
     * Example:
     * Resume.pdf
     */
    @Column(nullable = false)
    private String originalFilename;

    /**
     * Random UUID filename stored on disk
     * Example:
     * 0e8ac4ef-4c33-4d0d-acde.pdf
     */
    @Column(nullable = false,unique = true)
    private String storedFilename;

    // complete file path
    @Column(nullable = false)
    private String filePath;

    /**
     * application/pdf
     * image/png
     */
    private String contentType;

    // byte
    private Long fileSize;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name="user_id",nullable = false)
    private User owner;

    @CreationTimestamp
    private LocalDateTime uploadedAt;

    // this builder default is bcz lombok ignores such enum default values when storing things in db and since we have a
    // not null constraint here then it would cause an error cuz lombok setting it as null.
    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private DocumentStatus status=DocumentStatus.UPLOADED;

    // this is also just a precaution for the same above problem if that doesnt work this will
    @PrePersist
    public void prePersist() {
        if (status == null) {
            status = DocumentStatus.UPLOADED;
        }
    }


}
