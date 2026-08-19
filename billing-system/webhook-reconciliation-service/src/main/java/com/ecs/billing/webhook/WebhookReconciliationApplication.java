package com.ecs.billing.webhook;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class WebhookReconciliationApplication {
    public static void main(String[] args) { SpringApplication.run(WebhookReconciliationApplication.class, args); }
}
