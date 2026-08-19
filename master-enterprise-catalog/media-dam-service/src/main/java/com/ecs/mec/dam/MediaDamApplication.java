package com.ecs.mec.dam;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class MediaDamApplication {
    public static void main(String[] args) {
        SpringApplication.run(MediaDamApplication.class, args);
    }
}
