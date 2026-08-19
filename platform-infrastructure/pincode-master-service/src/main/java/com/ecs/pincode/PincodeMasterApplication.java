package com.ecs.pincode;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class PincodeMasterApplication {
    public static void main(String[] args) {
        SpringApplication.run(PincodeMasterApplication.class, args);
    }
}
