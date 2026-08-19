package com.ecs.search;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.ecs")
public class SearchSolrIndexerApplication {
    public static void main(String[] args) {
        SpringApplication.run(SearchSolrIndexerApplication.class, args);
    }
}
