package com.ecs.billing.invoice.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;
@RestController
@RequestMapping("/api/v1/invoices")
public class InvoiceController {
    @PostMapping
    public ApiResponse<Map<String, String>> issue(@RequestBody Map<String, Object> order) {
        return ApiResponse.ok(Map.of("invoiceId", UUID.randomUUID().toString(), "invoiceNumber", "INV-DL-" + System.currentTimeMillis()));
    }
    @GetMapping("/{id}/pdf")
    public ResponseEntity<byte[]> pdf(@PathVariable String id) {
        byte[] body = ("GST TAX INVOICE " + id).getBytes(StandardCharsets.UTF_8);
        return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=invoice-" + id + ".pdf")
                .contentType(MediaType.APPLICATION_PDF).body(body);
    }
}
