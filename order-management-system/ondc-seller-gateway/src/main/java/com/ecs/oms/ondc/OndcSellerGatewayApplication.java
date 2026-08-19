package com.ecs.oms.ondc;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class OndcSellerGatewayApplication {
    public static void main(String[] args) { SpringApplication.run(OndcSellerGatewayApplication.class, args); }
}
