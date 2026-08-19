package com.ecs.mec.sync;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class CatalogSyncPublisherApplication {
    public static void main(String[] args) {
        SpringApplication.run(CatalogSyncPublisherApplication.class, args);
    }
}
