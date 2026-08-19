package com.ecs.audit;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class McaAuditTrailApplication {
    public static void main(String[] args) {
        SpringApplication.run(McaAuditTrailApplication.class, args);
    }
}
