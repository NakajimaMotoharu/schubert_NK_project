package dev.codex.schubert.nk.web.messaging;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-REPLY-VALUE001002; SS321: opaque value mechanics only, no validation/commit/exit proof. */
final class ReplyValueContractTest {
  private static final UUID ID = new UUID(0, 1);
  private static final String CAUSE_TEXT = "public unissued cause marker";

  @Test
  void replyvalue001OpaqueBytesRemainOwnedAndUuidAndJavaArrayValueContractsAreExact() {
    byte[] opaque = {1, 2, 3, 4};
    var value = new ValidatedReply(ID, opaque);
    opaque[0] = 9;
    assertEquals(ID, value.correlationId());
    byte[] first = value.body();
    assertArrayEquals(new byte[] {1, 2, 3, 4}, first);
    first[1] = 9;
    assertArrayEquals(new byte[] {1, 2, 3, 4}, value.body());
    assertNotSame(first, value.body());
    assertEquals(value, value);
    assertEquals("owned", Map.of(value, "owned").get(value));
    int stableHash = value.hashCode();
    value.body()[2] = 9;
    assertEquals(stableHash, value.hashCode());
    assertNotEquals(value, new ValidatedReply(ID, new byte[] {1, 2, 3, 4}));
    assertNotEquals(value, new ValidatedReply(new UUID(0, 2), new byte[] {1, 2, 3, 4}));
    assertNotEquals(value, null);
    assertNotEquals(value, CAUSE_TEXT);
    assertEquals(
        "ValidatedReply[correlationId=00000000-0000-0000-0000-000000000001, body=<redacted>]",
        value.toString());
    assertThrows(NullPointerException.class, () -> new ValidatedReply(null, new byte[0]));
    assertThrows(NullPointerException.class, () -> new ValidatedReply(ID, null));
  }

  @Test
  void replyvalue002CommittedSignalRetainsExactCauseAndFixedPrimaryDiagnosticOnly() {
    for (Throwable cause :
        List.of(new IllegalStateException(CAUSE_TEXT), new AssertionError(CAUSE_TEXT))) {
      var value = new CommittedFatalReplyException(cause);
      assertSame(cause, value.getCause());
      assertEquals("invalid JMS reply was committed to the fatal DLQ", value.getMessage());
      assertEquals(0, value.getSuppressed().length);
      assertFalse(value.toString().contains(CAUSE_TEXT));
    }
  }
}
