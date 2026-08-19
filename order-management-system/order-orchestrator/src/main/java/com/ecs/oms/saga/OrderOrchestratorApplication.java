package com.ecs.oms.saga;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class OrderOrchestratorApplication {
    public static void main(String[] args) { SpringApplication.run(OrderOrchestratorApplication.class, args); }
}
