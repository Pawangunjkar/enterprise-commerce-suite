package com.ecs.mec.variant;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class VariantMatrixApplication {
    public static void main(String[] args) {
        SpringApplication.run(VariantMatrixApplication.class, args);
    }
}
