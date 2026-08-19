package com.ecs.mec.schema;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class DynamicSchemaApplication {
    public static void main(String[] args) {
        SpringApplication.run(DynamicSchemaApplication.class, args);
    }
}
