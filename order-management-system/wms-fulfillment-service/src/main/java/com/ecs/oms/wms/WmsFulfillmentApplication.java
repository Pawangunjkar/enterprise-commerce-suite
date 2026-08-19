package com.ecs.oms.wms;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class WmsFulfillmentApplication {
    public static void main(String[] args) { SpringApplication.run(WmsFulfillmentApplication.class, args); }
}
