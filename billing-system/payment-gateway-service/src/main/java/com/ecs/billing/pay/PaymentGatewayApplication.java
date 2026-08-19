package com.ecs.billing.pay;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class PaymentGatewayApplication {
    public static void main(String[] args) { SpringApplication.run(PaymentGatewayApplication.class, args); }
}
