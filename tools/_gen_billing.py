#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIL = ROOT / "billing-system"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def parent_pom(artifact, name, modules):
    mods = "\n".join(f"        <module>{m}</module>" for m in modules)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>enterprise-commerce-suite</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{artifact}</artifactId>
    <packaging>pom</packaging>
    <name>{name}</name>
    <modules>
{mods}
    </modules>
</project>
'''


def svc_pom(parent, artifact, extra=""):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>{parent}</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{artifact}</artifactId>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
        <dependency><groupId>org.springframework.kafka</groupId><artifactId>spring-kafka</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-websocket</artifactId></dependency>
        <dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>
        <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-core</artifactId></dependency>
        <dependency><groupId>org.flywaydb</groupId><artifactId>flyway-database-postgresql</artifactId></dependency>
        <dependency><groupId>org.springdoc</groupId><artifactId>springdoc-openapi-starter-webmvc-ui</artifactId><version>2.6.0</version></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>common-core</artifactId></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>common-security</artifactId></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>common-events</artifactId></dependency>
        {extra}
    </dependencies>
    <build><plugins><plugin><groupId>org.springframework.boot</groupId><artifactId>spring-boot-maven-plugin</artifactId></plugin></plugins></build>
</project>
'''


def yml(app, port):
    return f'''server:
  port: {port}
spring:
  application:
    name: {app}
  datasource:
    url: jdbc:postgresql://localhost:5432/ecs_billing
    username: ecs
    password: ecs_secret
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
  flyway:
    enabled: true
  kafka:
    bootstrap-servers: localhost:9092
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: http://localhost:8081/realms/ecs
'''


def app(pkg, cls):
    return f'''package {pkg};
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
@SpringBootApplication(scanBasePackages = "com.ecs")
public class {cls} {{
    public static void main(String[] args) {{ SpringApplication.run({cls}.class, args); }}
}}
'''


def boot(mod, pkg, cls, port, files, extra=""):
    w(BIL / f"{mod}/pom.xml", svc_pom("billing-system", mod, extra))
    w(BIL / f"{mod}/src/main/resources/application.yml", yml(mod, port))
    w(BIL / f"{mod}/src/main/java/{pkg.replace('.', '/')}/{cls}.java", app(pkg, cls))
    for rel, content in files.items():
        w(BIL / f"{mod}/src/main/java/{rel}", content)


mods = [
    "gst-tax-engine", "tcs-tds-compliance-engine", "price-book-service", "subscription-emi-service",
    "payment-gateway-service", "payment-gateway-plugins", "cod-remittance-reconcile-service",
    "webhook-reconciliation-service", "invoice-service", "general-ledger-service", "dunning-service"
]
w(BIL / "pom.xml", parent_pom("billing-system", "Billing System", mods))

PAY = '''<dependency><groupId>com.ecs</groupId><artifactId>payment-spi</artifactId></dependency>'''

boot("gst-tax-engine", "com.ecs.billing.gst", "GstTaxEngineApplication", 8301, {
    "com/ecs/billing/gst/GstCalculator.java": '''
package com.ecs.billing.gst;

import com.ecs.common.core.exception.DomainException;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Set;

public final class GstCalculator {
    private static final Set<Integer> SLABS = Set.of(0, 5, 12, 18, 28);

    public record GstBreakdown(BigDecimal taxable, BigDecimal cgst, BigDecimal sgst, BigDecimal igst, BigDecimal total,
                               String taxType, int slab) {}

    public static GstBreakdown compute(BigDecimal taxable, int slab, String originState, String destState) {
        if (!SLABS.contains(slab)) {
            throw DomainException.badRequest("Invalid GST slab: " + slab);
        }
        BigDecimal rate = BigDecimal.valueOf(slab).divide(BigDecimal.valueOf(100), 6, RoundingMode.HALF_UP);
        boolean intra = originState.equalsIgnoreCase(destState);
        if (intra) {
            BigDecimal half = taxable.multiply(rate).divide(BigDecimal.valueOf(2), 2, RoundingMode.HALF_UP);
            BigDecimal total = taxable.add(half).add(half);
            return new GstBreakdown(taxable, half, half, BigDecimal.ZERO.setScale(2), total, "CGST_SGST", slab);
        }
        BigDecimal igst = taxable.multiply(rate).setScale(2, RoundingMode.HALF_UP);
        return new GstBreakdown(taxable, BigDecimal.ZERO.setScale(2), BigDecimal.ZERO.setScale(2), igst,
                taxable.add(igst), "IGST", slab);
    }
}
''',
    "com/ecs/billing/gst/api/GstController.java": '''
package com.ecs.billing.gst.api;

import com.ecs.billing.gst.GstCalculator;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/gst")
public class GstController {
    public record ComputeRequest(BigDecimal taxable, int slab, String originState, String destState, String hsn) {}

    @PostMapping("/compute")
    public ApiResponse<GstCalculator.GstBreakdown> compute(@RequestBody ComputeRequest request) {
        return ApiResponse.ok(GstCalculator.compute(request.taxable(), request.slab(), request.originState(), request.destState()));
    }

    @PostMapping("/eway-bill")
    public ApiResponse<Map<String, Object>> eway(@RequestBody ComputeRequest request) {
        boolean required = request.taxable().compareTo(BigDecimal.valueOf(50000)) > 0;
        return ApiResponse.ok(Map.of(
                "required", required,
                "hsn", request.hsn(),
                "taxableValue", request.taxable(),
                "originState", request.originState(),
                "destState", request.destState()
        ));
    }
}
'''
})

boot("tcs-tds-compliance-engine", "com.ecs.billing.tcs", "TcsTdsApplication", 8302, {
    "com/ecs/billing/tcs/api/TcsController.java": '''
package com.ecs.billing.tcs.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/tcs")
public class TcsController {
    @PostMapping("/194o")
    public ApiResponse<Map<String, Object>> section194O(@RequestBody Map<String, BigDecimal> body) {
        BigDecimal gmv = body.getOrDefault("gmv", BigDecimal.ZERO);
        BigDecimal tcs = gmv.multiply(new BigDecimal("0.01")).setScale(2, RoundingMode.HALF_UP);
        return ApiResponse.ok(Map.of("section", "194O", "gmv", gmv, "tcs", tcs));
    }
}
'''
})

boot("payment-gateway-service", "com.ecs.billing.pay", "PaymentGatewayApplication", 8305, {
    "com/ecs/billing/pay/api/PaymentController.java": '''
package com.ecs.billing.pay.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.payment.spi.BharatQrFactory;
import com.ecs.payment.spi.DynamicBharatQr;
import com.ecs.payment.spi.UpiIntentResponse;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/v1/payments")
public class PaymentController {
    private final Map<String, String> status = new ConcurrentHashMap<>();

    public record QrRequest(String orderId, BigDecimal amount, String vpa, String merchantName, String mcc) {}

    @PostMapping("/upi/bharat-qr")
    public ApiResponse<Map<String, Object>> qr(@RequestBody QrRequest request) {
        DynamicBharatQr qr = BharatQrFactory.create(request.vpa(), request.merchantName(), request.mcc(),
                request.orderId(), request.amount());
        UpiIntentResponse intents = BharatQrFactory.intents(qr.upiUri());
        status.put(qr.txnId(), "PENDING");
        return ApiResponse.ok(Map.of("paymentId", UUID.randomUUID().toString(), "qr", qr, "intents", intents));
    }

    @GetMapping("/{txnId}/status")
    public ApiResponse<Map<String, String>> poll(@PathVariable String txnId) {
        return ApiResponse.ok(Map.of("txnId", txnId, "status", status.getOrDefault(txnId, "UNKNOWN")));
    }

    @PostMapping("/{txnId}/simulate-success")
    public ApiResponse<Map<String, String>> simulate(@PathVariable String txnId) {
        status.put(txnId, "CAPTURED");
        return ApiResponse.ok(Map.of("txnId", txnId, "status", "CAPTURED"));
    }
}
'''
}, PAY)

boot("payment-gateway-plugins", "com.ecs.billing.plugins", "PaymentPluginsApplication", 8306, {
    "com/ecs/billing/plugins/RazorpayAdapter.java": '''
package com.ecs.billing.plugins;

import com.ecs.payment.spi.*;
import org.springframework.stereotype.Component;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;
import java.util.HexFormat;
import java.util.UUID;

@Component
public class RazorpayAdapter implements PaymentGatewayAdapter {
    public String providerId() { return "RAZORPAY"; }

    public AuthorizeResponse authorize(AuthorizeRequest request, ByokCredential credential) {
        DynamicBharatQr qr = BharatQrFactory.create(credential.vpa(), "ECS Merchant", credential.mcc(),
                request.orderNumber(), request.amountInr());
        return new AuthorizeResponse(UUID.randomUUID(), PaymentStatus.PENDING, providerId(),
                "rzp_" + UUID.randomUUID().toString().substring(0, 8), null,
                BharatQrFactory.intents(qr.upiUri()), qr);
    }

    public PaymentStatus capture(CaptureRequest request, ByokCredential credential) { return PaymentStatus.CAPTURED; }
    public PaymentStatus refund(String providerTxnId, java.math.BigDecimal amountInr, ByokCredential credential) { return PaymentStatus.REFUNDED; }

    public boolean verifyWebhook(WebhookEvent event, ByokCredential credential) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(credential.encryptedSecret().getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            String expected = HexFormat.of().formatHex(mac.doFinal(event.rawBody().getBytes(StandardCharsets.UTF_8)));
            return expected.equalsIgnoreCase(event.signature());
        } catch (Exception ex) {
            return false;
        }
    }
}
'''
}, PAY)

boot("price-book-service", "com.ecs.billing.pricebook", "PriceBookApplication", 8303, {
    "com/ecs/billing/pricebook/api/PriceBookController.java": '''
package com.ecs.billing.pricebook.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/price-books")
public class PriceBookController {
    @GetMapping("/{sku}")
    public ApiResponse<Map<String, Object>> get(@PathVariable String sku) {
        return ApiResponse.ok(Map.of("sku", sku, "mrp", new BigDecimal("79999.00"), "channel", "D2C"));
    }
}
'''
})

boot("subscription-emi-service", "com.ecs.billing.emi", "SubscriptionEmiApplication", 8304, {
    "com/ecs/billing/emi/api/EmiController.java": '''
package com.ecs.billing.emi.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/emi")
public class EmiController {
    @GetMapping("/quote")
    public ApiResponse<Map<String, Object>> quote(@RequestParam BigDecimal principal, @RequestParam int months) {
        BigDecimal installment = principal.divide(BigDecimal.valueOf(months), 2, RoundingMode.HALF_UP);
        return ApiResponse.ok(Map.of("principal", principal, "months", months, "installment", installment, "noCost", true));
    }
}
'''
})

boot("cod-remittance-reconcile-service", "com.ecs.billing.cod", "CodRemittanceApplication", 8307, {
    "com/ecs/billing/cod/api/CodReconcileController.java": '''
package com.ecs.billing.cod.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.math.BigDecimal;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/cod")
public class CodReconcileController {
    public record Match(String awb, BigDecimal carrierAmount, BigDecimal bankAmount) {}
    @PostMapping("/match")
    public ApiResponse<Map<String, Object>> match(@RequestBody Match request) {
        boolean ok = request.carrierAmount().compareTo(request.bankAmount()) == 0;
        return ApiResponse.ok(Map.of("awb", request.awb(), "matched", ok, "delta", request.carrierAmount().subtract(request.bankAmount())));
    }
}
'''
})

boot("webhook-reconciliation-service", "com.ecs.billing.webhook", "WebhookReconciliationApplication", 8308, {
    "com/ecs/billing/webhook/api/WebhookController.java": '''
package com.ecs.billing.webhook.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/payments/webhooks")
public class WebhookController {
    @PostMapping("/{provider}")
    public ApiResponse<Map<String, String>> ingest(@PathVariable String provider, @RequestHeader(value = "X-Signature", required = false) String signature) {
        return ApiResponse.ok(Map.of("provider", provider, "accepted", "true", "signaturePresent", String.valueOf(signature != null)));
    }
}
'''
})

boot("invoice-service", "com.ecs.billing.invoice", "InvoiceServiceApplication", 8309, {
    "com/ecs/billing/invoice/api/InvoiceController.java": '''
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
'''
})

boot("general-ledger-service", "com.ecs.billing.ledger", "GeneralLedgerApplication", 8310, {
    "com/ecs/billing/ledger/api/LedgerController.java": '''
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
'''
})

boot("dunning-service", "com.ecs.billing.dunning", "DunningApplication", 8311, {
    "com/ecs/billing/dunning/api/DunningController.java": '''
package com.ecs.billing.dunning.api;
import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;
@RestController
@RequestMapping("/api/v1/dunning")
public class DunningController {
    @GetMapping("/schedule")
    public ApiResponse<List<Map<String, Object>>> schedule() {
        return ApiResponse.ok(List.of(
                Map.of("attempt", 1, "delayHours", 0),
                Map.of("attempt", 2, "delayHours", 24),
                Map.of("attempt", 3, "delayHours", 72)
        ));
    }
}
'''
})

print("billing generated")
