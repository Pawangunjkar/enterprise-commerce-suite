package com.ecs.billing.pricebook;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class PriceBookApplication {
    public static void main(String[] args) { SpringApplication.run(PriceBookApplication.class, args); }
}
