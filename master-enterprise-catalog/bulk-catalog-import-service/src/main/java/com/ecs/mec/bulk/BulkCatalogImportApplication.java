package com.ecs.mec.bulk;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class BulkCatalogImportApplication {
    public static void main(String[] args) {
        SpringApplication.run(BulkCatalogImportApplication.class, args);
    }
}
