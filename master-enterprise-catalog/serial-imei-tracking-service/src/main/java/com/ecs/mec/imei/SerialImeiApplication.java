package com.ecs.mec.imei;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class SerialImeiApplication {
    public static void main(String[] args) {
        SpringApplication.run(SerialImeiApplication.class, args);
    }
}
