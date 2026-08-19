package com.ecs.dlq.api;

import com.ecs.common.core.api.ApiResponse;
import com.ecs.common.core.api.PageResponse;
import com.ecs.common.core.exception.DomainException;
import com.ecs.dlq.domain.DeadLetter;
import com.ecs.dlq.repo.DeadLetterRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/v1/dlq")
public class DlqController {

    private final DeadLetterRepository repository;
    private final KafkaTemplate<String, String> kafkaTemplate;

    public DlqController(DeadLetterRepository repository, KafkaTemplate<String, String> kafkaTemplate) {
        this.repository = repository;
        this.kafkaTemplate = kafkaTemplate;
    }

    @GetMapping
    public ApiResponse<PageResponse<DeadLetter>> list(
            @RequestParam(defaultValue = "OPEN") String status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size
    ) {
        return ApiResponse.ok(PageResponse.from(repository.findByStatus(status, PageRequest.of(page, size))));
    }

    @PostMapping("/{id}/replay")
    public ApiResponse<DeadLetter> replay(@PathVariable UUID id) {
        DeadLetter letter = repository.findById(id).orElseThrow(() -> DomainException.notFound("DeadLetter", id));
        kafkaTemplate.send(letter.getOriginalTopic(), letter.getPayload());
        letter.setReplayAttempts(letter.getReplayAttempts() + 1);
        letter.setStatus("REPLAYED");
        return ApiResponse.ok(repository.save(letter), "Message replayed to " + letter.getOriginalTopic());
    }

    @PostMapping("/replay")
    public ApiResponse<DeadLetter> replayAlias(@RequestParam UUID id) {
        return replay(id);
    }
}
