package com.ecs.billing.invoice.api;

import com.ecs.billing.invoice.domain.GstInvoice;
import com.ecs.billing.invoice.repo.GstInvoiceRepository;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.charset.StandardCharsets;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/invoices")
public class InvoiceController {

    private static final Set<Integer> SLABS = Set.of(0, 5, 12, 18, 28);
    private final GstInvoiceRepository invoices;

    public InvoiceController(GstInvoiceRepository invoices) {
        this.invoices = invoices;
    }

    public record IssueRequest(
            String orderId,
            String orderNumber,
            BigDecimal taxable,
            Integer slab,
            String originState,
            String destState,
            String hsn
    ) {}

    public record IssueResponse(UUID invoiceId, String invoiceNumber, String taxType, BigDecimal totalInr) {}

    @PostMapping
    public ApiResponse<IssueResponse> issue(@RequestBody IssueRequest request) {
        int slab = request.slab() == null || !SLABS.contains(request.slab()) ? 18 : request.slab();
        BigDecimal taxable = request.taxable() == null ? BigDecimal.ZERO : request.taxable();
        String origin = request.originState() == null ? "HR" : request.originState();
        String dest = request.destState() == null ? "DL" : request.destState();
        BigDecimal rate = BigDecimal.valueOf(slab).divide(BigDecimal.valueOf(100), 6, RoundingMode.HALF_UP);
        boolean intra = origin.equalsIgnoreCase(dest);
        GstInvoice invoice = new GstInvoice();
        invoice.setInvoiceNumber("INV-DL-" + System.currentTimeMillis());
        invoice.setOrderId(UUID.fromString(request.orderId()));
        invoice.setOrderNumber(request.orderNumber() == null ? request.orderId() : request.orderNumber());
        invoice.setTaxableInr(taxable);
        invoice.setSlab(slab);
        invoice.setOriginState(origin);
        invoice.setDestState(dest);
        invoice.setHsnCode(request.hsn());
        if (intra) {
            BigDecimal half = taxable.multiply(rate).divide(BigDecimal.valueOf(2), 2, RoundingMode.HALF_UP);
            invoice.setCgstInr(half);
            invoice.setSgstInr(half);
            invoice.setIgstInr(BigDecimal.ZERO.setScale(2));
            invoice.setTotalInr(taxable.add(half).add(half));
            invoice.setTaxType("CGST_SGST");
        } else {
            BigDecimal igst = taxable.multiply(rate).setScale(2, RoundingMode.HALF_UP);
            invoice.setCgstInr(BigDecimal.ZERO.setScale(2));
            invoice.setSgstInr(BigDecimal.ZERO.setScale(2));
            invoice.setIgstInr(igst);
            invoice.setTotalInr(taxable.add(igst));
            invoice.setTaxType("IGST");
        }
        GstInvoice saved = invoices.save(invoice);
        return ApiResponse.ok(new IssueResponse(saved.getId(), saved.getInvoiceNumber(), saved.getTaxType(), saved.getTotalInr()));
    }

    @GetMapping("/{id}")
    public ApiResponse<GstInvoice> get(@PathVariable UUID id) {
        return ApiResponse.ok(invoices.findById(id).orElseThrow(() -> DomainException.notFound("invoice", id)));
    }

    @GetMapping("/{id}/pdf")
    public ResponseEntity<byte[]> pdf(@PathVariable String id) {
        byte[] body = ("GST TAX INVOICE " + id).getBytes(StandardCharsets.UTF_8);
        return ResponseEntity.ok().header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=invoice-" + id + ".pdf")
                .contentType(MediaType.APPLICATION_PDF).body(body);
    }
}
