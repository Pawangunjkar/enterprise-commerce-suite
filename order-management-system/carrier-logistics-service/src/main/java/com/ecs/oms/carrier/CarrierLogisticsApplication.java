package com.ecs.oms.carrier;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class CarrierLogisticsApplication {
    public static void main(String[] args) { SpringApplication.run(CarrierLogisticsApplication.class, args); }
}
