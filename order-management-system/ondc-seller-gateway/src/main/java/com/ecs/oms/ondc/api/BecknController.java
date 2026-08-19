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
