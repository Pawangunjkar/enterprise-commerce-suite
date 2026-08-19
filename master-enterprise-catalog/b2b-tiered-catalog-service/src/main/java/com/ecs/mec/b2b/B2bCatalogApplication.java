package com.ecs.mec.b2b;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class B2bCatalogApplication {
    public static void main(String[] args) {
        SpringApplication.run(B2bCatalogApplication.class, args);
    }
}
