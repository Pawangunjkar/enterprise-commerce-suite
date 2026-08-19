package com.ecs.mec.product.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.api.PageResponse;
import com.ecs.common.core.exception.DomainException;
import com.ecs.mec.product.domain.Product;
import com.ecs.mec.product.repo.ProductRepository;
import com.ecs.mec.product.service.ProductCommandService;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/products")
public class ProductController {

    private final ProductCommandService commandService;
    private final ProductRepository repository;

    public ProductController(ProductCommandService commandService, ProductRepository repository) {
        this.commandService = commandService;
        this.repository = repository;
    }

    @PostMapping
    public ApiResponse<Product> create(@RequestBody ProductCommandService.UpsertRequest request) {
        return ApiResponse.ok(commandService.upsert(request));
    }

    @PutMapping("/{id}/activate")
    public ApiResponse<Product> activate(@PathVariable UUID id) {
        return ApiResponse.ok(commandService.activate(id));
    }

    @GetMapping("/{id}")
    public ApiResponse<Product> get(@PathVariable UUID id) {
        return ApiResponse.ok(repository.findById(id).orElseThrow(() -> DomainException.notFound("Product", id)));
    }

    @GetMapping
    public ApiResponse<PageResponse<Product>> list(@RequestParam(defaultValue = "0") int page,
                                                   @RequestParam(defaultValue = "20") int size) {
        return ApiResponse.ok(PageResponse.from(repository.findAll(PageRequest.of(page, size))));
    }
}
