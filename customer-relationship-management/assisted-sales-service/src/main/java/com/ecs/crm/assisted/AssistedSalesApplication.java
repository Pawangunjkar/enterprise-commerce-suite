package com.ecs.crm.assisted;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class AssistedSalesApplication {
    public static void main(String[] args) { SpringApplication.run(AssistedSalesApplication.class, args); }
}
