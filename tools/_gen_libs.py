#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SL = ROOT / "platform-infrastructure" / "shared-libraries"
PI = ROOT / "platform-infrastructure"


def w(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def lib_pom(artifact, name, extra=""):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>com.ecs</groupId>
        <artifactId>shared-libraries</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{artifact}</artifactId>
    <name>{name}</name>
    <dependencies>{extra}</dependencies>
</project>
'''


JACKSON = '''
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
        <dependency>
            <groupId>com.ecs</groupId>
            <artifactId>common-core</artifactId>
        </dependency>
'''

# ---------- common-security ----------
w(SL / "common-security/pom.xml", lib_pom("common-security", "Common Security", '''
        <dependency>
            <groupId>com.ecs</groupId>
            <artifactId>common-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
        </dependency>
'''))

w(SL / "common-security/src/main/java/com/ecs/common/security/GatewayPrincipal.java", '''
package com.ecs.common.security;

import java.util.List;
import java.util.UUID;

public record GatewayPrincipal(
        UUID userId,
        String tenantId,
        List<String> roles,
        List<String> scopes,
        String mobile,
        String email
) {
    public boolean hasRole(String role) {
        return roles != null && roles.stream().anyMatch(r -> r.equalsIgnoreCase(role) || r.equalsIgnoreCase("ROLE_" + role));
    }

    public boolean hasScope(String scope) {
        return scopes != null && scopes.contains(scope);
    }
}
''')

w(SL / "common-security/src/main/java/com/ecs/common/security/GatewayHeaders.java", '''
package com.ecs.common.security;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public final class GatewayHeaders {
    public static final String USER_ID = "X-User-Id";
    public static final String TENANT_ID = "X-Tenant-Id";
    public static final String USER_ROLES = "X-User-Roles";
    public static final String SCOPES = "X-Scopes";
    public static final String MOBILE = "X-User-Mobile";
    public static final String EMAIL = "X-User-Email";

    private GatewayHeaders() {}

    public static GatewayPrincipal current() {
        HttpServletRequest request = request();
        UUID userId = Optional.ofNullable(request.getHeader(USER_ID))
                .filter(s -> !s.isBlank())
                .map(UUID::fromString)
                .orElse(null);
        return new GatewayPrincipal(
                userId,
                Optional.ofNullable(request.getHeader(TENANT_ID)).orElse("default"),
                split(request.getHeader(USER_ROLES)),
                split(request.getHeader(SCOPES)),
                request.getHeader(MOBILE),
                request.getHeader(EMAIL)
        );
    }

    private static List<String> split(String value) {
        if (value == null || value.isBlank()) {
            return List.of();
        }
        return Arrays.stream(value.split(",")).map(String::trim).filter(s -> !s.isEmpty()).toList();
    }

    private static HttpServletRequest request() {
        var attrs = RequestContextHolder.getRequestAttributes();
        if (attrs instanceof ServletRequestAttributes servlet) {
            return servlet.getRequest();
        }
        throw new IllegalStateException("No HTTP request bound to the current thread");
    }
}
''')

w(SL / "common-security/src/main/java/com/ecs/common/security/RequireRole.java", '''
package com.ecs.common.security;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireRole {
    String[] value();
}
''')

w(SL / "common-security/src/main/java/com/ecs/common/security/RoleGuardAspect.java", '''
package com.ecs.common.security;

import com.ecs.common.core.exception.DomainException;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class RoleGuardAspect {

    @Before("@annotation(requireRole)")
    public void check(JoinPoint joinPoint, RequireRole requireRole) {
        GatewayPrincipal principal = GatewayHeaders.current();
        for (String role : requireRole.value()) {
            if (principal.hasRole(role) || principal.hasRole("SUPER_ADMIN")) {
                return;
            }
        }
        throw new DomainException(HttpStatus.FORBIDDEN, "FORBIDDEN", "Insufficient role for " + joinPoint.getSignature());
    }
}
''')

w(SL / "common-security/src/main/java/com/ecs/common/security/ResourceServerSecurityConfig.java", '''
package com.ecs.common.security;

import org.springframework.boot.autoconfigure.condition.ConditionalOnWebApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@ConditionalOnWebApplication
public class ResourceServerSecurityConfig {

    @Bean
    public SecurityFilterChain resourceServerFilterChain(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.disable())
                .sessionManagement(sm -> sm.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/actuator/**", "/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
                        .requestMatchers("/api/v1/public/**").permitAll()
                        .anyRequest().authenticated())
                .oauth2ResourceServer(oauth -> oauth.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
''')

# ---------- common-events ----------
w(SL / "common-events/pom.xml", lib_pom("common-events", "Common Events", JACKSON))

w(SL / "common-events/src/main/java/com/ecs/common/events/CloudEventEnvelope.java", '''
package com.ecs.common.events;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.time.Instant;
import java.util.UUID;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record CloudEventEnvelope<T>(
        String specversion,
        String type,
        String source,
        String id,
        Instant time,
        String datacontenttype,
        String subject,
        String tenantId,
        T data
) {
    public static <T> CloudEventEnvelope<T> of(String type, String source, String tenantId, String subject, T data) {
        return new CloudEventEnvelope<>(
                "1.0",
                type,
                source,
                UUID.randomUUID().toString(),
                Instant.now(),
                "application/json",
                subject,
                tenantId,
                data
        );
    }
}
''')

w(SL / "common-events/src/main/java/com/ecs/common/events/Topics.java", '''
package com.ecs.common.events;

public final class Topics {
    public static final String CATALOG_PRODUCT_PUBLISHED = "catalog.product-published";
    public static final String CATALOG_OFFER_SYNCED = "catalog.offer-synced";
    public static final String CATALOG_OFFER_ACTIVATED = "catalog.offer-activated";
    public static final String CATALOG_PRODUCT_ACTIVATED = "catalog.product-activated";
    public static final String PRICING_EOD_UPDATE = "pricing.eod-update";
    public static final String ORDER_PLACED = "order.placed";
    public static final String ORDER_STATUS_CHANGED = "order.status-changed";
    public static final String PAYMENT_AUTHORIZED = "billing.payment-authorized";
    public static final String PAYMENT_CAPTURED = "billing.payment-captured";
    public static final String PAYMENT_FAILED = "billing.payment-failed";
    public static final String INVOICE_ISSUED = "billing.invoice-issued";
    public static final String SHIPMENT_CREATED = "logistics.shipment-created";
    public static final String NDR_RAISED = "logistics.ndr-raised";
    public static final String CART_ABANDONED = "crm.cart-abandoned";
    public static final String CUSTOMER_KYC_UPDATED = "crm.kyc-updated";
    public static final String DLQ = "platform.dlq";
    public static final String AUDIT = "platform.mca-audit";

    private Topics() {}
}
''')

w(SL / "common-events/src/main/java/com/ecs/common/events/catalog/ProductPublishedEvent.java", '''
package com.ecs.common.events.catalog;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;

public record ProductPublishedEvent(
        UUID productId,
        String sku,
        String name,
        String hsnCode,
        String status,
        Instant effectiveFrom,
        Instant effectiveTo,
        Map<String, Object> attributes,
        BigDecimal listPriceInr,
        String brand,
        String categoryPath
) {}
''')

w(SL / "common-events/src/main/java/com/ecs/common/events/catalog/OfferActivatedEvent.java", '''
package com.ecs.common.events.catalog;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public record OfferActivatedEvent(
        UUID offerId,
        String offerCode,
        String offerType,
        BigDecimal discountValue,
        String discountKind,
        Instant validFrom,
        Instant validTo,
        UUID productId,
        String sku
) {}
''')

w(SL / "common-events/src/main/java/com/ecs/common/events/order/OrderPlacedEvent.java", '''
package com.ecs.common.events.order;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

public record OrderPlacedEvent(
        UUID orderId,
        String orderNumber,
        UUID customerId,
        String pincode,
        String originStateCode,
        String destinationStateCode,
        BigDecimal grandTotalInr,
        String paymentMode,
        List<Line> lines
) {
    public record Line(UUID skuId, String sku, int qty, BigDecimal unitPrice, String hsnCode) {}
}
''')

w(SL / "common-events/src/main/java/com/ecs/common/events/billing/PaymentEvent.java", '''
package com.ecs.common.events.billing;

import java.math.BigDecimal;
import java.util.UUID;

public record PaymentEvent(
        UUID paymentId,
        UUID orderId,
        String provider,
        String method,
        String status,
        BigDecimal amountInr,
        String upiVpa,
        String providerTxnId
) {}
''')

w(SL / "common-events/src/main/java/com/ecs/common/events/logistics/ShipmentEvent.java", '''
package com.ecs.common.events.logistics;

import java.util.UUID;

public record ShipmentEvent(
        UUID shipmentId,
        UUID orderId,
        String carrier,
        String awb,
        String status,
        String originPincode,
        String destinationPincode
) {}
''')

# ---------- payment-spi ----------
w(SL / "payment-spi/pom.xml", lib_pom("payment-spi", "Payment SPI", JACKSON + '''
        <dependency>
            <groupId>com.google.zxing</groupId>
            <artifactId>core</artifactId>
            <version>3.5.3</version>
        </dependency>
        <dependency>
            <groupId>com.google.zxing</groupId>
            <artifactId>javase</artifactId>
            <version>3.5.3</version>
        </dependency>
'''))

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/PaymentMethod.java", '''
package com.ecs.payment.spi;

public enum PaymentMethod {
    UPI_QR, UPI_INTENT, UPI_AUTOPAY, CARD, NETBANKING, WALLET, COD, EMI
}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/PaymentStatus.java", '''
package com.ecs.payment.spi;

public enum PaymentStatus {
    CREATED, AUTHORIZED, CAPTURED, FAILED, CANCELLED, REFUNDED, PENDING
}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/AuthorizeRequest.java", '''
package com.ecs.payment.spi;

import java.math.BigDecimal;
import java.util.Map;
import java.util.UUID;

public record AuthorizeRequest(
        UUID orderId,
        String orderNumber,
        BigDecimal amountInr,
        PaymentMethod method,
        String customerMobile,
        String returnUrl,
        Map<String, String> metadata
) {}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/AuthorizeResponse.java", '''
package com.ecs.payment.spi;

import java.util.UUID;

public record AuthorizeResponse(
        UUID paymentId,
        PaymentStatus status,
        String provider,
        String providerTxnId,
        String redirectUrl,
        UpiIntentResponse upiIntent,
        DynamicBharatQr bharatQr
) {}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/UpiIntentResponse.java", '''
package com.ecs.payment.spi;

public record UpiIntentResponse(
        String gpay,
        String phonepe,
        String paytm,
        String cred,
        String generic
) {}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/DynamicBharatQr.java", '''
package com.ecs.payment.spi;

public record DynamicBharatQr(
        String upiUri,
        String pngBase64,
        String txnId,
        String vpa
) {}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/CaptureRequest.java", '''
package com.ecs.payment.spi;

import java.math.BigDecimal;
import java.util.UUID;

public record CaptureRequest(UUID paymentId, UUID orderId, BigDecimal amountInr, String providerTxnId) {}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/WebhookEvent.java", '''
package com.ecs.payment.spi;

import java.time.Instant;
import java.util.Map;

public record WebhookEvent(
        String provider,
        String signature,
        String rawBody,
        PaymentStatus status,
        String providerTxnId,
        Instant receivedAt,
        Map<String, Object> payload
) {}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/ByokCredential.java", '''
package com.ecs.payment.spi;

public record ByokCredential(
        String provider,
        String keyId,
        String encryptedSecret,
        String merchantId,
        String vpa,
        String mcc
) {}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/PaymentGatewayAdapter.java", '''
package com.ecs.payment.spi;

public interface PaymentGatewayAdapter {
    String providerId();

    AuthorizeResponse authorize(AuthorizeRequest request, ByokCredential credential);

    PaymentStatus capture(CaptureRequest request, ByokCredential credential);

    PaymentStatus refund(String providerTxnId, java.math.BigDecimal amountInr, ByokCredential credential);

    boolean verifyWebhook(WebhookEvent event, ByokCredential credential);
}
''')

w(SL / "payment-spi/src/main/java/com/ecs/payment/spi/BharatQrFactory.java", '''
package com.ecs.payment.spi;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;

import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.UUID;

public final class BharatQrFactory {

    private BharatQrFactory() {}

    public static DynamicBharatQr create(String vpa, String merchantName, String mcc, String orderId, BigDecimal amount) {
        String txnId = UUID.randomUUID().toString().replace("-", "").substring(0, 20);
        String uri = "upi://pay?pa=" + enc(vpa)
                + "&pn=" + enc(merchantName)
                + "&mc=" + enc(mcc)
                + "&tid=" + enc(txnId)
                + "&tr=" + enc(orderId)
                + "&am=" + amount.toPlainString()
                + "&cu=INR";
        return new DynamicBharatQr(uri, toPngBase64(uri), txnId, vpa);
    }

    public static UpiIntentResponse intents(String upiUri) {
        String encoded = enc(upiUri);
        return new UpiIntentResponse(
                "tez://upi/pay?data=" + encoded,
                "phonepe://pay?pa=" + encoded,
                "paytmmp://pay?pa=" + encoded,
                "credpay://upi?uri=" + encoded,
                upiUri
        );
    }

    private static String enc(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    private static String toPngBase64(String content) {
        try {
            BitMatrix matrix = new QRCodeWriter().encode(content, BarcodeFormat.QR_CODE, 320, 320);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            MatrixToImageWriter.writeToStream(matrix, "PNG", out);
            return Base64.getEncoder().encodeToString(out.toByteArray());
        } catch (Exception ex) {
            throw new IllegalStateException("Unable to render BharatQR", ex);
        }
    }
}
''')

# ---------- logistics-spi ----------
w(SL / "logistics-spi/pom.xml", lib_pom("logistics-spi", "Logistics SPI", JACKSON))

w(SL / "logistics-spi/src/main/java/com/ecs/logistics/spi/ServiceabilityRequest.java", '''
package com.ecs.logistics.spi;

import java.math.BigDecimal;

public record ServiceabilityRequest(
        String originPincode,
        String destinationPincode,
        BigDecimal weightKg,
        BigDecimal declaredValueInr,
        boolean cod
) {}
''')

w(SL / "logistics-spi/src/main/java/com/ecs/logistics/spi/ServiceabilityResponse.java", '''
package com.ecs.logistics.spi;

import java.math.BigDecimal;
import java.time.LocalDate;

public record ServiceabilityResponse(
        boolean serviceable,
        boolean oda,
        BigDecimal shippingChargeInr,
        int transitDays,
        LocalDate estimatedDeliveryDate,
        String zone
) {}
''')

w(SL / "logistics-spi/src/main/java/com/ecs/logistics/spi/WaybillRequest.java", '''
package com.ecs.logistics.spi;

import java.math.BigDecimal;
import java.util.UUID;

public record WaybillRequest(
        UUID orderId,
        String consigneeName,
        String consigneeMobile,
        String destinationPincode,
        String destinationAddress,
        BigDecimal weightKg,
        BigDecimal collectableInr,
        boolean cod
) {}
''')

w(SL / "logistics-spi/src/main/java/com/ecs/logistics/spi/WaybillResponse.java", '''
package com.ecs.logistics.spi;

public record WaybillResponse(
        String carrier,
        String awb,
        String labelPdfBase64,
        String trackingUrl
) {}
''')

w(SL / "logistics-spi/src/main/java/com/ecs/logistics/spi/NdrStatus.java", '''
package com.ecs.logistics.spi;

import java.time.Instant;

public record NdrStatus(
        String awb,
        String reasonCode,
        String reasonText,
        int attemptCount,
        Instant lastAttemptAt,
        boolean rtoInitiated
) {}
''')

w(SL / "logistics-spi/src/main/java/com/ecs/logistics/spi/CarrierAdapter.java", '''
package com.ecs.logistics.spi;

public interface CarrierAdapter {
    String carrierId();

    ServiceabilityResponse checkServiceability(ServiceabilityRequest request);

    WaybillResponse createWaybill(WaybillRequest request);

    NdrStatus fetchNdr(String awb);

    byte[] reprintLabel(String awb);
}
''')

# ---------- ondc-beckn-spi ----------
w(SL / "ondc-beckn-spi/pom.xml", lib_pom("ondc-beckn-spi", "ONDC Beckn SPI", JACKSON))

w(SL / "ondc-beckn-spi/src/main/java/com/ecs/ondc/spi/BecknContext.java", '''
package com.ecs.ondc.spi;

public record BecknContext(
        String domain,
        String country,
        String city,
        String action,
        String coreVersion,
        String bapId,
        String bapUri,
        String bppId,
        String bppUri,
        String transactionId,
        String messageId,
        String timestamp
) {}
''')

w(SL / "ondc-beckn-spi/src/main/java/com/ecs/ondc/spi/BecknRequest.java", '''
package com.ecs.ondc.spi;

import com.fasterxml.jackson.databind.JsonNode;

public record BecknRequest(BecknContext context, JsonNode message) {}
''')

w(SL / "ondc-beckn-spi/src/main/java/com/ecs/ondc/spi/BecknResponse.java", '''
package com.ecs.ondc.spi;

import com.fasterxml.jackson.databind.JsonNode;

public record BecknResponse(BecknContext context, JsonNode message) {}
''')

w(SL / "ondc-beckn-spi/src/main/java/com/ecs/ondc/spi/CatalogItemMessage.java", '''
package com.ecs.ondc.spi;

import java.math.BigDecimal;

public record CatalogItemMessage(
        String id,
        String descriptor,
        String categoryId,
        BigDecimal priceInr,
        int availableQty,
        String fulfillmentId
) {}
''')

w(SL / "ondc-beckn-spi/src/main/java/com/ecs/ondc/spi/OrderMessage.java", '''
package com.ecs.ondc.spi;

import java.math.BigDecimal;
import java.util.List;

public record OrderMessage(
        String id,
        String status,
        BigDecimal totalInr,
        List<CatalogItemMessage> items
) {}
''')

w(SL / "ondc-beckn-spi/src/main/java/com/ecs/ondc/spi/BecknSellerGateway.java", '''
package com.ecs.ondc.spi;

public interface BecknSellerGateway {
    BecknResponse search(BecknRequest request);
    BecknResponse select(BecknRequest request);
    BecknResponse init(BecknRequest request);
    BecknResponse confirm(BecknRequest request);
    BecknResponse status(BecknRequest request);
    BecknResponse track(BecknRequest request);
    BecknResponse cancel(BecknRequest request);
}
''')

# ---------- saga-orchestration ----------
w(SL / "saga-orchestration/pom.xml", lib_pom("saga-orchestration", "Saga Orchestration", JACKSON + '''
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter</artifactId>
        </dependency>
'''))

w(SL / "saga-orchestration/src/main/java/com/ecs/saga/CheckoutSagaState.java", '''
package com.ecs.saga;

public enum CheckoutSagaState {
    CART_VALIDATED,
    ATP_LOCKED,
    PAYMENT_AUTHORIZED,
    COD_VERIFIED,
    WAREHOUSE_ROUTED,
    DISPATCHED,
    PAYMENT_CAPTURED,
    COMPLETED,
    COMPENSATING,
    FAILED
}
''')

w(SL / "saga-orchestration/src/main/java/com/ecs/saga/SagaStep.java", '''
package com.ecs.saga;

public interface SagaStep<C> {
    String name();
    CheckoutSagaState execute(C context);
    void compensate(C context);
}
''')

w(SL / "saga-orchestration/src/main/java/com/ecs/saga/SagaOrchestrator.java", '''
package com.ecs.saga;

import com.ecs.common.core.exception.DomainException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

public class SagaOrchestrator<C> {
    private static final Logger log = LoggerFactory.getLogger(SagaOrchestrator.class);
    private final List<SagaStep<C>> steps;

    public SagaOrchestrator(List<SagaStep<C>> steps) {
        this.steps = List.copyOf(steps);
    }

    public CheckoutSagaState run(C context) {
        List<SagaStep<C>> executed = new ArrayList<>();
        try {
            CheckoutSagaState last = CheckoutSagaState.CART_VALIDATED;
            for (SagaStep<C> step : steps) {
                log.info("Executing saga step {}", step.name());
                last = step.execute(context);
                executed.add(step);
            }
            return last == CheckoutSagaState.PAYMENT_CAPTURED ? CheckoutSagaState.COMPLETED : last;
        } catch (Exception ex) {
            log.error("Saga failed, compensating {} steps", executed.size(), ex);
            for (int i = executed.size() - 1; i >= 0; i--) {
                try {
                    executed.get(i).compensate(context);
                } catch (Exception compensateEx) {
                    log.error("Compensation failed for {}", executed.get(i).name(), compensateEx);
                }
            }
            throw DomainException.unprocessable("SAGA_FAILED", ex.getMessage());
        }
    }
}
''')

print("shared libraries complete")
