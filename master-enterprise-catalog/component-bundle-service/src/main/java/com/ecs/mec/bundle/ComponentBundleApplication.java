package com.ecs.mec.bundle;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class ComponentBundleApplication {
    public static void main(String[] args) {
        SpringApplication.run(ComponentBundleApplication.class, args);
    }
}
