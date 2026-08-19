package com.ecs.search.api;

import com.ecs.common.core.api.ApiResponse;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/search")
public class ProductSearchController {

    private final SolrClient solrClient;
    private final String collection;

    public ProductSearchController(SolrClient solrClient, @Value("${ecs.solr.collection}") String collection) {
        this.solrClient = solrClient;
        this.collection = collection;
    }

    @GetMapping("/products")
    public ApiResponse<Map<String, Object>> search(
            @RequestParam(defaultValue = "*:*") String q,
            @RequestParam(required = false) String brand,
            @RequestParam(required = false) Integer ram,
            @RequestParam(required = false) String color,
            @RequestParam(required = false) Double minPrice,
            @RequestParam(required = false) Double maxPrice,
            @RequestParam(defaultValue = "0") int start,
            @RequestParam(defaultValue = "24") int rows
    ) throws Exception {
        SolrQuery query = new SolrQuery(q);
        query.setStart(start);
        query.setRows(rows);
        query.addFilterQuery("status_s:ACTIVE");
        String now = Instant.now().toString();
        query.addFilterQuery("effective_from_dt:[* TO " + now + "]");
        query.addFilterQuery("effective_to_dt:[" + now + " TO *]");
        if (brand != null) query.addFilterQuery("brand_s:" + brand);
        if (ram != null) query.addFilterQuery("attr_ram_i:" + ram);
        if (color != null) query.addFilterQuery("attr_color_s:" + color);
        if (minPrice != null || maxPrice != null) {
            String lo = minPrice == null ? "*" : minPrice.toString();
            String hi = maxPrice == null ? "*" : maxPrice.toString();
            query.addFilterQuery("list_price_f:[" + lo + " TO " + hi + "]");
        }
        query.setFacet(true);
        query.addFacetField("brand_s", "attr_ram_i", "attr_color_s", "attr_storage_s");
        query.set("defType", "edismax");
        query.set("qf", "name_txt_en name_txt_hi sku_s brand_s");
        QueryResponse response = solrClient.query(collection, query);
        List<Map<String, Object>> docs = response.getResults().stream().map(this::toMap).toList();
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("numFound", response.getResults().getNumFound());
        body.put("docs", docs);
        body.put("facets", response.getFacetFields());
        return ApiResponse.ok(body);
    }

    @GetMapping("/autocomplete")
    public ApiResponse<List<String>> autocomplete(@RequestParam String q) throws Exception {
        SolrQuery query = new SolrQuery(q + "*");
        query.setRows(8);
        query.set("defType", "edismax");
        query.set("qf", "name_txt_en name_txt_hi");
        query.setFields("name_txt_en");
        QueryResponse response = solrClient.query(collection, query);
        return ApiResponse.ok(response.getResults().stream()
                .map(d -> String.valueOf(d.getFieldValue("name_txt_en")))
                .toList());
    }

    private Map<String, Object> toMap(SolrDocument document) {
        Map<String, Object> map = new LinkedHashMap<>();
        document.forEach(map::put);
        return map;
    }
}
