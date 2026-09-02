package com.AI_knowledge.Assistant.document.storage;

import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Service
public class StorageServiceImpl implements StorageService{

    private final Path rootLocation;

    @Autowired
    public StorageServiceImpl(FileStorageProperties properties){
        this.rootLocation=
                Paths.get(properties.getUploadDir())
                        .toAbsolutePath()
                        .normalize();
    }

    @PostConstruct
    public void init(){
        try{
            Files.createDirectories(rootLocation);
        }catch(IOException e){
            throw new RuntimeException(
                    "Could not initialize upload directory",e
            );

        }
    }

    @Override
    public String store(MultipartFile file) {

        if(file.isEmpty()){
            throw new RuntimeException("cannot upload empty file");
        }

        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());
        if (originalFilename.contains("..")) {
            throw new RuntimeException("Invalid file name.");
        }
        String extension = "";

        int dotIndex = originalFilename.lastIndexOf('.');

        if(dotIndex >= 0){
            extension = originalFilename.substring(dotIndex);
        }

        String storedFilename = UUID.randomUUID() + extension;

        try{
            Path destination = rootLocation.resolve(storedFilename);
            Files.copy(
                    file.getInputStream(),
                    destination,
                    StandardCopyOption.REPLACE_EXISTING
            );
            return storedFilename;
        }catch (IOException e){
            throw  new RuntimeException("Failed to store file",e);
        }

    }

    @Override
    public Resource loadAsResource(String storedFilename) {

        try{
            Path file =  rootLocation.resolve(storedFilename).normalize();

            Resource resource = new UrlResource(file.toUri());

            if(resource.exists()){
                return resource;
            }

            throw new RuntimeException("File not found");
        }catch (MalformedURLException e){
            throw  new RuntimeException("Cannot read file",e);
        }
    }

    @Override
    public void delete(String storedFilename) {

        try{
            Path file = rootLocation.resolve(storedFilename);
            Files.deleteIfExists(file);
        }catch (IOException e){
            throw  new RuntimeException("Unable to delete file",e);
        }

    }
}
