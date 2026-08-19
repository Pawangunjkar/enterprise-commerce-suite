package com.ecs.billing.invoice;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class InvoiceServiceApplication {
    public static void main(String[] args) { SpringApplication.run(InvoiceServiceApplication.class, args); }
}
