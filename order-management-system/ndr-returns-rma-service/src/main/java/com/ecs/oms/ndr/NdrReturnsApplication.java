package com.ecs.oms.ndr;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class NdrReturnsApplication {
    public static void main(String[] args) { SpringApplication.run(NdrReturnsApplication.class, args); }
}
