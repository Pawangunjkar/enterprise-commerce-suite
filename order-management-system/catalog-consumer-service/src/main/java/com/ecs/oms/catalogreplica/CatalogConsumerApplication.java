package com.ecs.oms.catalogreplica;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class CatalogConsumerApplication {
    public static void main(String[] args) { SpringApplication.run(CatalogConsumerApplication.class, args); }
}
