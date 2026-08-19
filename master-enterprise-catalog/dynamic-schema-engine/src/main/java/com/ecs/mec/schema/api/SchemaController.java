package com.ecs.mec.schema.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.exception.DomainException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.JsonSchema;
import com.networknt.schema.JsonSchemaFactory;
import com.networknt.schema.SpecVersion;
import com.networknt.schema.ValidationMessage;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Set;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/catalog/schema")
public class SchemaController {

    private final ObjectMapper mapper = new ObjectMapper();
    private final JsonSchemaFactory factory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);

    public record ValidateRequest(JsonNode schema, JsonNode instance) {}

    @PostMapping("/validate")
    public ApiResponse<Boolean> validate(@RequestBody ValidateRequest request) {
        JsonSchema schema = factory.getSchema(request.schema());
        Set<ValidationMessage> errors = schema.validate(request.instance());
        if (!errors.isEmpty()) {
            throw DomainException.badRequest(errors.stream().map(ValidationMessage::getMessage).collect(Collectors.joining("; ")));
        }
        return ApiResponse.ok(true);
    }
}
