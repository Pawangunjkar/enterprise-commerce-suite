package com.ecs.billing.gst;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class GstTaxEngineApplication {
    public static void main(String[] args) { SpringApplication.run(GstTaxEngineApplication.class, args); }
}
