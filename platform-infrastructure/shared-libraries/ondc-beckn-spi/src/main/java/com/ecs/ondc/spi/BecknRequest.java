package com.ecs.ondc.spi;

import com.fasterxml.jackson.databind.JsonNode;

public record BecknRequest(BecknContext context, JsonNode message) {}
