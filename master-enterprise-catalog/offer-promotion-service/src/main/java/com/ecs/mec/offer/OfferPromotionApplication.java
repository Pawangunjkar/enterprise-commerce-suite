package com.ecs.mec.offer;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class OfferPromotionApplication {
    public static void main(String[] args) {
        SpringApplication.run(OfferPromotionApplication.class, args);
    }
}
