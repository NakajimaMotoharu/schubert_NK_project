package dev.codex.schubert.nk.api.application.question;

import java.time.Clock;
import java.util.Objects;

/**
 * No external call, persistence, logging or retained question; PG190/STB001..005; SS312 section8.1.
 */
public final class StubAnswerProvider implements AnswerProvider {
  private final Clock clock;

  public StubAnswerProvider(Clock clock) {
    this.clock = Objects.requireNonNull(clock, "clock");
  }

  @Override
  public AnswerResult answer(String question) {
    Objects.requireNonNull(question, "question");
    return new AnswerResult("", clock.instant());
  }
}
