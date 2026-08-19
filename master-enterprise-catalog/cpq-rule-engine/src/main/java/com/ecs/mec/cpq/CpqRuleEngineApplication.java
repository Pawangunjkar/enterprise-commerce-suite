package com.ecs.mec.cpq;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class CpqRuleEngineApplication {
    public static void main(String[] args) {
        SpringApplication.run(CpqRuleEngineApplication.class, args);
    }
}
