#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OMS = ROOT / "order-management-system"


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
    <name>{artifact}</name>
    <dependencies>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-validation</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-actuator</artifactId></dependency>
        <dependency><groupId>org.springframework.kafka</groupId><artifactId>spring-kafka</artifactId></dependency>
        <dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-redis</artifactId></dependency>
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


def yml(app, port, db):
    return f'''server:
  port: {port}
spring:
  application:
    name: {app}
  datasource:
    url: jdbc:postgresql://localhost:5432/{db}
    username: ecs
    password: ecs_secret
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
  flyway:
    enabled: true
  data:
    redis:
      host: localhost
      port: 6379
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: {app}
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
import org.springframework.scheduling.annotation.EnableScheduling;
@SpringBootApplication(scanBasePackages = "com.ecs")
@EnableScheduling
public class {cls} {{
    public static void main(String[] args) {{ SpringApplication.run({cls}.class, args); }}
}}
'''


def boot(mod, pkg, cls, port, extra_files, extra=""):
    w(OMS / f"{mod}/pom.xml", svc_pom("order-management-system", mod, extra))
    w(OMS / f"{mod}/src/main/resources/application.yml", yml(mod, port, "ecs_oms"))
    w(OMS / f"{mod}/src/main/java/{pkg.replace('.', '/')}/{cls}.java", app(pkg, cls))
    for rel, content in extra_files.items():
        w(OMS / f"{mod}/src/main/{rel}", content)


mods = [
    "cart-service", "checkout-service", "order-orchestrator", "dynamic-price-engine",
    "atp-inventory-service", "wms-fulfillment-service", "ondc-seller-gateway",
    "carrier-logistics-service", "bopis-pickup-service", "ndr-returns-rma-service",
    "catalog-consumer-service"
]
w(OMS / "pom.xml", parent_pom("order-management-system", "Order Management System", mods))

SPI = '''
        <dependency><groupId>com.ecs</groupId><artifactId>saga-orchestration</artifactId></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>logistics-spi</artifactId></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>ondc-beckn-spi</artifactId></dependency>
        <dependency><groupId>com.ecs</groupId><artifactId>payment-spi</artifactId></dependency>
'''

boot("cart-service", "com.ecs.oms.cart", "CartServiceApplication", 8201, {
    "java/com/ecs/oms/cart/api/CartController.java": '''
package com.ecs.oms.cart.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.Duration;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/carts")
public class CartController {
    private final StringRedisTemplate redis;

    public CartController(StringRedisTemplate redis) { this.redis = redis; }

    public record Line(String sku, int qty, BigDecimal unitPrice) {}

    @PostMapping("/{cartId}/items")
    public ApiResponse<Map<String, String>> add(@PathVariable String cartId, @RequestBody Line line) {
        String key = "cart:" + cartId;
        redis.opsForHash().put(key, line.sku(), line.qty() + ":" + line.unitPrice());
        redis.expire(key, Duration.ofHours(24));
        return ApiResponse.ok(Map.of("cartId", cartId, "sku", line.sku(), "qty", String.valueOf(line.qty())));
    }

    @GetMapping("/{cartId}")
    public ApiResponse<Map<Object, Object>> get(@PathVariable String cartId) {
        return ApiResponse.ok(redis.opsForHash().entries("cart:" + cartId));
    }
}
'''
})

boot("checkout-service", "com.ecs.oms.checkout", "CheckoutServiceApplication", 8202, {
    "java/com/ecs/oms/checkout/api/CheckoutController.java": '''
package com.ecs.oms.checkout.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/checkout")
public class CheckoutController {
    private static final Set<String> HIGH_RISK = Set.of("999999", "000000");

    public record Intent(String cartId, String pincode, String paymentMode, BigDecimal amount, String gstin) {}

    @PostMapping("/intent")
    public ApiResponse<Map<String, Object>> intent(@RequestBody Intent intent) {
        if ("COD".equalsIgnoreCase(intent.paymentMode()) && (intent.amount().compareTo(BigDecimal.valueOf(25000)) > 0
                || HIGH_RISK.contains(intent.pincode()))) {
            throw DomainException.unprocessable("COD_INELIGIBLE", "COD is not available for this cart or pincode");
        }
        return ApiResponse.ok(Map.of(
                "checkoutId", UUID.randomUUID().toString(),
                "cartId", intent.cartId(),
                "paymentMode", intent.paymentMode(),
                "gstin", intent.gstin() == null ? "" : intent.gstin()
        ));
    }
}
'''
})

boot("dynamic-price-engine", "com.ecs.oms.price", "DynamicPriceEngineApplication", 8204, {
    "java/com/ecs/oms/price/api/PriceController.java": '''
package com.ecs.oms.price.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.events.Topics;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/prices")
public class PriceController {
    private final StringRedisTemplate redis;
    public PriceController(StringRedisTemplate redis) { this.redis = redis; }

    public record CalcRequest(String sku, BigDecimal basePrice, BigDecimal offerDiscount, BigDecimal loyaltyDiscount) {}

    @PostMapping("/calculate")
    public ApiResponse<Map<String, Object>> calculate(@RequestBody CalcRequest request) {
        String cached = redis.opsForValue().get("price:" + request.sku());
        BigDecimal offer = request.offerDiscount() == null ? BigDecimal.ZERO : request.offerDiscount();
        BigDecimal loyalty = request.loyaltyDiscount() == null ? BigDecimal.ZERO : request.loyaltyDiscount();
        BigDecimal effective = request.basePrice().subtract(offer).subtract(loyalty).max(BigDecimal.ZERO)
                .setScale(2, RoundingMode.HALF_UP);
        redis.opsForValue().set("price:" + request.sku(), effective.toPlainString());
        return ApiResponse.ok(Map.of("sku", request.sku(), "effectivePrice", effective, "cached", cached != null));
    }

    @KafkaListener(topics = Topics.CATALOG_OFFER_ACTIVATED)
    public void onOffer(String payload) {
        redis.keys("price:*").forEach(redis::delete);
    }

    @Scheduled(cron = "0 5 0 * * *", zone = "Asia/Kolkata")
    public void eod() {
        redis.keys("price:*").forEach(redis::delete);
    }
}
'''
})

boot("order-orchestrator", "com.ecs.oms.saga", "OrderOrchestratorApplication", 8203, {
    "java/com/ecs/oms/saga/api/OrderSagaController.java": '''
package com.ecs.oms.saga.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.saga.CheckoutSagaState;
import com.ecs.saga.SagaOrchestrator;
import com.ecs.saga.SagaStep;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;

@RestController
@RequestMapping("/api/v1/orders")
public class OrderSagaController {

    public record PlaceOrderRequest(String cartId, String pincode, String paymentMode, BigDecimal amount) {}
    public static final class Ctx {
        public final PlaceOrderRequest request;
        public final AtomicReference<UUID> orderId = new AtomicReference<>(UUID.randomUUID());
        public Ctx(PlaceOrderRequest request) { this.request = request; }
    }

    @PostMapping
    public ApiResponse<CheckoutSagaState> place(@RequestBody PlaceOrderRequest request) {
        SagaOrchestrator<Ctx> orchestrator = new SagaOrchestrator<>(List.of(
                step("atp-lock", CheckoutSagaState.ATP_LOCKED),
                step("payment-or-cod", "COD".equalsIgnoreCase(request.paymentMode())
                        ? CheckoutSagaState.COD_VERIFIED : CheckoutSagaState.PAYMENT_AUTHORIZED),
                step("warehouse-route", CheckoutSagaState.WAREHOUSE_ROUTED),
                step("capture-on-dispatch", CheckoutSagaState.PAYMENT_CAPTURED)
        ));
        return ApiResponse.ok(orchestrator.run(new Ctx(request)));
    }

    private SagaStep<Ctx> step(String name, CheckoutSagaState state) {
        return new SagaStep<>() {
            public String name() { return name; }
            public CheckoutSagaState execute(Ctx context) { return state; }
            public void compensate(Ctx context) { }
        };
    }
}
'''
}, SPI)

boot("atp-inventory-service", "com.ecs.oms.atp", "AtpInventoryApplication", 8205, {
    "java/com/ecs/oms/atp/api/AtpController.java": '''
package com.ecs.oms.atp.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/api/v1/inventory")
public class AtpController {
    private final Map<String, Integer> stock = new ConcurrentHashMap<>(Map.of("SKU-PHONE-8-128-BLACK", 42));

    public record LockRequest(String sku, int qty, String warehouse) {}

    @PostMapping("/lock")
    public ApiResponse<Map<String, Integer>> lock(@RequestBody LockRequest request) {
        int available = stock.getOrDefault(request.sku(), 0);
        if (available < request.qty()) {
            throw DomainException.unprocessable("ATP_SHORTAGE", "Only " + available + " units available");
        }
        stock.put(request.sku(), available - request.qty());
        return ApiResponse.ok(Map.of("remaining", stock.get(request.sku())));
    }
}
'''
})

boot("wms-fulfillment-service", "com.ecs.oms.wms", "WmsFulfillmentApplication", 8206, {
    "java/com/ecs/oms/wms/api/WmsController.java": '''
package com.ecs.oms.wms.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/wms")
public class WmsController {
    public record PickLine(String sku, String bin, int qty) {}

    @PostMapping("/waves")
    public ApiResponse<Map<String, Object>> createWave(@RequestBody List<PickLine> lines) {
        return ApiResponse.ok(Map.of("waveId", UUID.randomUUID().toString(), "lines", lines, "status", "RELEASED"));
    }
}
'''
})

boot("ondc-seller-gateway", "com.ecs.oms.ondc", "OndcSellerGatewayApplication", 8207, {
    "java/com/ecs/oms/ondc/api/BecknController.java": '''
package com.ecs.oms.ondc.api;

import com.ecs.ondc.spi.BecknRequest;
import com.ecs.ondc.spi.BecknResponse;
import com.ecs.ondc.spi.BecknSellerGateway;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/ondc")
public class BecknController implements BecknSellerGateway {
    private final ObjectMapper mapper = new ObjectMapper();

    private BecknResponse ack(BecknRequest request, String action) {
        ObjectNode message = mapper.createObjectNode();
        message.put("ack", "ACK");
        message.put("action", action);
        return new BecknResponse(request.context(), message);
    }

    @PostMapping("/search") public BecknResponse search(@RequestBody BecknRequest request) { return ack(request, "search"); }
    @PostMapping("/select") public BecknResponse select(@RequestBody BecknRequest request) { return ack(request, "select"); }
    @PostMapping("/init") public BecknResponse init(@RequestBody BecknRequest request) { return ack(request, "init"); }
    @PostMapping("/confirm") public BecknResponse confirm(@RequestBody BecknRequest request) { return ack(request, "confirm"); }
    @PostMapping("/status") public BecknResponse status(@RequestBody BecknRequest request) { return ack(request, "status"); }
    @PostMapping("/track") public BecknResponse track(@RequestBody BecknRequest request) { return ack(request, "track"); }
    @PostMapping("/cancel") public BecknResponse cancel(@RequestBody BecknRequest request) { return ack(request, "cancel"); }
}
'''
}, '''<dependency><groupId>com.ecs</groupId><artifactId>ondc-beckn-spi</artifactId></dependency>''')

boot("carrier-logistics-service", "com.ecs.oms.carrier", "CarrierLogisticsApplication", 8208, {
    "java/com/ecs/oms/carrier/DelhiveryAdapter.java": '''
package com.ecs.oms.carrier;

import com.ecs.logistics.spi.*;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Base64;
import java.util.UUID;

@Component
public class DelhiveryAdapter implements CarrierAdapter {
    public String carrierId() { return "DELHIVERY"; }

    public ServiceabilityResponse checkServiceability(ServiceabilityRequest request) {
        int days = request.destinationPincode().startsWith("1") ? 2 : 4;
        return new ServiceabilityResponse(true, false, BigDecimal.valueOf(79), days, LocalDate.now().plusDays(days), "N1");
    }

    public WaybillResponse createWaybill(WaybillRequest request) {
        String awb = "DLV" + UUID.randomUUID().toString().substring(0, 10).toUpperCase();
        return new WaybillResponse("DELHIVERY", awb, Base64.getEncoder().encodeToString(("AWB " + awb).getBytes()),
                "https://www.delhivery.com/track/" + awb);
    }

    public NdrStatus fetchNdr(String awb) {
        return new NdrStatus(awb, "CNA", "Consignee not available", 1, java.time.Instant.now(), false);
    }

    public byte[] reprintLabel(String awb) { return ("LABEL-" + awb).getBytes(); }
}
''',
    "java/com/ecs/oms/carrier/api/CarrierController.java": '''
package com.ecs.oms.carrier.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.logistics.spi.CarrierAdapter;
import com.ecs.logistics.spi.ServiceabilityRequest;
import com.ecs.logistics.spi.WaybillRequest;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/logistics")
public class CarrierController {
    private final Map<String, CarrierAdapter> adapters;

    public CarrierController(List<CarrierAdapter> adapters) {
        this.adapters = adapters.stream().collect(Collectors.toMap(a -> a.carrierId().toLowerCase(), Function.identity()));
    }

    @PostMapping("/{carrier}/serviceability")
    public ApiResponse<?> serviceability(@PathVariable String carrier, @RequestBody ServiceabilityRequest request) {
        return ApiResponse.ok(adapters.get(carrier.toLowerCase()).checkServiceability(request));
    }

    @PostMapping("/{carrier}/waybills")
    public ApiResponse<?> waybill(@PathVariable String carrier, @RequestBody WaybillRequest request) {
        return ApiResponse.ok(adapters.get(carrier.toLowerCase()).createWaybill(request));
    }
}
'''
}, '''<dependency><groupId>com.ecs</groupId><artifactId>logistics-spi</artifactId></dependency>''')

boot("bopis-pickup-service", "com.ecs.oms.bopis", "BopisPickupApplication", 8209, {
    "java/com/ecs/oms/bopis/api/BopisController.java": '''
package com.ecs.oms.bopis.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/bopis")
public class BopisController {
    @PostMapping("/reservations")
    public ApiResponse<Map<String, String>> reserve(@RequestBody Map<String, String> body) {
        return ApiResponse.ok(Map.of("reservationId", UUID.randomUUID().toString(), "hub", body.getOrDefault("hub", "DEL-HUB-01"), "status", "READY_FOR_PICKUP"));
    }
}
'''
})

boot("ndr-returns-rma-service", "com.ecs.oms.ndr", "NdrReturnsApplication", 8210, {
    "java/com/ecs/oms/ndr/api/NdrController.java": '''
package com.ecs.oms.ndr.api;

import com.ecs.common.core.api.ApiResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ndr")
public class NdrController {
    @PostMapping("/{awb}/action")
    public ApiResponse<Map<String, String>> action(@PathVariable String awb, @RequestParam String action) {
        String status = "REATTEMPT".equalsIgnoreCase(action) ? "REATTEMPT_SCHEDULED" : "RTO_INITIATED";
        return ApiResponse.ok(Map.of("awb", awb, "status", status));
    }
}
'''
})

boot("catalog-consumer-service", "com.ecs.oms.catalogreplica", "CatalogConsumerApplication", 8211, {
    "java/com/ecs/oms/catalogreplica/listener/ReplicaListener.java": '''
package com.ecs.oms.catalogreplica.listener;

import com.ecs.common.events.Topics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class ReplicaListener {
    private static final Logger log = LoggerFactory.getLogger(ReplicaListener.class);
    private final StringRedisTemplate redis;
    public ReplicaListener(StringRedisTemplate redis) { this.redis = redis; }

    @KafkaListener(topics = Topics.CATALOG_PRODUCT_PUBLISHED)
    public void onProduct(String payload) {
        redis.opsForValue().set("catalog:last-event", payload);
        log.info("Updated local catalog replica");
    }
}
'''
})

print("OMS generated")
