package com.ecs.oms.cart;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class CartServiceApplication {
    public static void main(String[] args) { SpringApplication.run(CartServiceApplication.class, args); }
}
