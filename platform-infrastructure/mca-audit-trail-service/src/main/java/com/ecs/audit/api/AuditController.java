package com.ecs.audit.api;

import com.ecs.audit.domain.AuditRecord;
import com.ecs.audit.repo.AuditRecordRepository;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.api.PageResponse;
import com.ecs.common.core.tenant.TenantContext;
import jakarta.validation.constraints.NotBlank;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/audit")
public class AuditController {

    private final AuditRecordRepository repository;

    public AuditController(AuditRecordRepository repository) {
        this.repository = repository;
    }

    public record AppendRequest(
            @NotBlank String actor,
            @NotBlank String action,
            @NotBlank String resourceType,
            @NotBlank String resourceId,
            Map<String, Object> payload
    ) {}

    @PostMapping
    public ApiResponse<AuditRecord> append(@RequestBody AppendRequest request) {
        AuditRecord record = new AuditRecord();
        record.setTenantId(TenantContext.get());
        record.setActor(request.actor());
        record.setAction(request.action());
        record.setResourceType(request.resourceType());
        record.setResourceId(request.resourceId());
        record.setPayload(request.payload() == null ? Map.of() : request.payload());
        String raw = record.getTenantId() + "|" + record.getActor() + "|" + record.getAction()
                + "|" + record.getResourceType() + "|" + record.getResourceId() + "|" + record.getOccurredAt();
        record.setChecksum(sha256(raw));
        return ApiResponse.ok(repository.save(record));
    }

    @GetMapping
    public ApiResponse<PageResponse<AuditRecord>> list(
            @RequestParam String resourceType,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "50") int size
    ) {
        return ApiResponse.ok(PageResponse.from(
                repository.findByTenantIdAndResourceType(TenantContext.get(), resourceType, PageRequest.of(page, size))));
    }

    private static String sha256(String raw) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(raw.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(digest);
        } catch (Exception ex) {
            throw new IllegalStateException(ex);
        }
    }
}
