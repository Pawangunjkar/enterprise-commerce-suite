package com.ecs.oms.atp;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class AtpInventoryApplication {
    public static void main(String[] args) { SpringApplication.run(AtpInventoryApplication.class, args); }
}
