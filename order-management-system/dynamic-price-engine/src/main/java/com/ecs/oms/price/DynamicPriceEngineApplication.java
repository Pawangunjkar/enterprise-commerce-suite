package com.ecs.oms.price;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class DynamicPriceEngineApplication {
    public static void main(String[] args) { SpringApplication.run(DynamicPriceEngineApplication.class, args); }
}
