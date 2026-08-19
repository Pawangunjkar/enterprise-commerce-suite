package com.ecs.billing.emi;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class SubscriptionEmiApplication {
    public static void main(String[] args) { SpringApplication.run(SubscriptionEmiApplication.class, args); }
}
