package com.ecs.search.index;

import com.ecs.common.events.Topics;
import com.ecs.common.events.catalog.ProductPublishedEvent;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.common.SolrInputDocument;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
public class CatalogIndexListener {

    private final SolrClient solrClient;
    private final ObjectMapper objectMapper;
    private final String collection;

    public CatalogIndexListener(SolrClient solrClient, ObjectMapper objectMapper,
                                @Value("${ecs.solr.collection}") String collection) {
        this.solrClient = solrClient;
        this.objectMapper = objectMapper;
        this.collection = collection;
    }

    @KafkaListener(topics = {Topics.CATALOG_PRODUCT_PUBLISHED, Topics.CATALOG_PRODUCT_ACTIVATED})
    public void onProduct(String json) throws Exception {
        var tree = objectMapper.readTree(json);
        var payload = tree.has("data") ? tree.get("data") : tree;
        ProductPublishedEvent event = objectMapper.treeToValue(payload, ProductPublishedEvent.class);
        SolrInputDocument doc = new SolrInputDocument();
        doc.addField("id", event.productId().toString());
        doc.addField("sku_s", event.sku());
        doc.addField("name_txt_en", event.name());
        doc.addField("name_txt_hi", event.name());
        doc.addField("brand_s", event.brand());
        doc.addField("category_path_s", event.categoryPath());
        doc.addField("hsn_s", event.hsnCode());
        doc.addField("status_s", event.status());
        doc.addField("list_price_f", event.listPriceInr());
        doc.addField("effective_from_dt", event.effectiveFrom() == null ? Instant.now().toString() : event.effectiveFrom().toString());
        doc.addField("effective_to_dt", event.effectiveTo() == null ? "2099-12-31T23:59:59Z" : event.effectiveTo().toString());
        if (event.attributes() != null) {
            event.attributes().forEach((k, v) -> {
                if (v instanceof Number n) {
                    if (n instanceof Double || n instanceof Float) {
                        doc.addField("attr_" + k + "_f", n);
                    } else {
                        doc.addField("attr_" + k + "_i", n);
                    }
                } else {
                    doc.addField("attr_" + k + "_s", String.valueOf(v));
                }
            });
        }
        solrClient.add(collection, doc);
        solrClient.commit(collection);
    }
}
