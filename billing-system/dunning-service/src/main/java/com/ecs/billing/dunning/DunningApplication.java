package com.ecs.billing.dunning;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class DunningApplication {
    public static void main(String[] args) { SpringApplication.run(DunningApplication.class, args); }
}
