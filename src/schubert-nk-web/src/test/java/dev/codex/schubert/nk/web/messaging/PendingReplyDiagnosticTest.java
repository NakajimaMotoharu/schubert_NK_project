package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-JMS-008-DIAG001. Approved SS351 diagnostic is independent of public correlation access. */
final class PendingReplyDiagnosticTest {
  private static final String EXPECTED = "PendingReply[correlationId/deadline/body=<redacted>]";

  @Test
  void differentCorrelationsDeadlinesAndTerminalStatesShareTheFixedDiagnostic() {
    UUID firstId = new UUID(0, 17);
    UUID secondId = new UUID(0, 29);
    Instant firstDeadline = Instant.ofEpochSecond(9345);
    Instant secondDeadline = Instant.ofEpochSecond(17890);
    var first = new PendingReply(firstId, firstDeadline);
    var second = new PendingReply(secondId, secondDeadline);
    assertEquals(firstId, first.correlationId());
    assertEquals(secondId, second.correlationId());
    assertEquals(firstDeadline, first.deadline());
    assertEquals(secondDeadline, second.deadline());
    assertEquals(EXPECTED, first.toString());
    assertEquals(EXPECTED, second.toString());

    first.complete(new byte[] {12, 18});
    second.fail(new IllegalStateException("unit failure"));
    var completed = first.completion().toCompletableFuture();
    assertTrue(completed.isDone());
    assertArrayEquals(new byte[] {12, 18}, completed.join());
    assertTrue(second.completion().toCompletableFuture().isCompletedExceptionally());
    assertEquals(EXPECTED, first.toString());
    assertEquals(EXPECTED, second.toString());
  }
}
