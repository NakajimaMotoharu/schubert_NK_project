package dev.codex.schubert.nk.api.application.question;

import java.time.Instant;
import java.util.Objects;

/** Provider result, not persisted completion; PG190/STB002/004; SS312 section8.1. */
public record AnswerResult(String body, Instant answeredAt) {
  public AnswerResult {
    Objects.requireNonNull(body, "answer body");
    Objects.requireNonNull(answeredAt, "answer time");
  }

  @Override
  public String toString() {
    return "AnswerResult[REDACTED]";
  }
}
