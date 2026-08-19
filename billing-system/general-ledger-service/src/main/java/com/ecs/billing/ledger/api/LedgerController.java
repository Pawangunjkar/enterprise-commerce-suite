package com.ecs.billing.ledger.api;
import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/ledger")
public class LedgerController {
    public record Entry(String account, String dc, BigDecimal amount) {}
    @PostMapping("/journals")
    public ApiResponse<Map<String, Object>> post(@RequestBody List<Entry> entries) {
        BigDecimal debit = entries.stream().filter(e -> "D".equalsIgnoreCase(e.dc())).map(Entry::amount).reduce(BigDecimal.ZERO, BigDecimal::add);
        BigDecimal credit = entries.stream().filter(e -> "C".equalsIgnoreCase(e.dc())).map(Entry::amount).reduce(BigDecimal.ZERO, BigDecimal::add);
        if (debit.compareTo(credit) != 0) {
            throw DomainException.unprocessable("UNBALANCED_JOURNAL", "Debit " + debit + " != Credit " + credit);
        }
        return ApiResponse.ok(Map.of("balanced", true, "debit", debit, "credit", credit));
    }
}
