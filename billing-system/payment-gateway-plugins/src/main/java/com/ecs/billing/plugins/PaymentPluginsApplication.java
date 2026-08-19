package com.ecs.billing.plugins;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class PaymentPluginsApplication {
    public static void main(String[] args) { SpringApplication.run(PaymentPluginsApplication.class, args); }
}
