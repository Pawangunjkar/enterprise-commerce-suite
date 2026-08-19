package com.ecs.dlq;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class KafkaDlqManagerApplication {
    public static void main(String[] args) {
        SpringApplication.run(KafkaDlqManagerApplication.class, args);
    }
}
