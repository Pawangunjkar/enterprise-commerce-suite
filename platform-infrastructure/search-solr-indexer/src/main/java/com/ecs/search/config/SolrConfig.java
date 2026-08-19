package com.ecs.search.config;

import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.impl.Http2SolrClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SolrConfig {

    @Bean
    public SolrClient solrClient(@Value("${ecs.solr.base-url}") String baseUrl) {
        return new Http2SolrClient.Builder(baseUrl).build();
    }
}
