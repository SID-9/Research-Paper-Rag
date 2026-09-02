package com.AI_knowledge.Assistant.document.mapper;

import com.AI_knowledge.Assistant.document.dto.DocumentResponseDto;
import com.AI_knowledge.Assistant.model.Document;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface DocumentMapper {

    DocumentResponseDto toDto(Document document);

}
