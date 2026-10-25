package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.OptionalInt;
import org.junit.jupiter.api.Test;

/** PT-F03-EXC007; SS333/BUG1482/YKT1237: values only, no HTTP/file access. */
final class ExceptionValueContractTest {
  @Test
  void exc007MediaStatusAndRetryRemainClosedAndNonNull() {
    for (var reason : MediaDeliveryException.Reason.values()) {
      var failure = new MediaDeliveryException(reason);
      assertSame(reason, failure.reason());
      assertEquals("media delivery failed", failure.getMessage());
      assertEquals(503, failure.httpStatus());
      assertEquals(
          reason == MediaDeliveryException.Reason.BUSY ? OptionalInt.of(1) : OptionalInt.empty(),
          failure.retryAfterSeconds());
      assertNull(failure.getCause());
    }
    assertThrows(NullPointerException.class, () -> new MediaDeliveryException(null));
  }
}
