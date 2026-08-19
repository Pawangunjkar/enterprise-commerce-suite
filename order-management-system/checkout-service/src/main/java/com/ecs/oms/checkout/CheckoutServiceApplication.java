package com.ecs.oms.checkout;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class CheckoutServiceApplication {
    public static void main(String[] args) { SpringApplication.run(CheckoutServiceApplication.class, args); }
}
