package com.ecs.ondc.spi;

import com.fasterxml.jackson.databind.JsonNode;

public record BecknResponse(BecknContext context, JsonNode message) {}
