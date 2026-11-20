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

  @Test
  void mediaFailureNamesResolveOnlyToTheDefinedReasons() {
    // PT-MED-FAILURE-NAME-001 / SS333: named reasons keep the public failure metadata.
    var invalid =
        new MediaDeliveryException(MediaDeliveryException.Reason.valueOf("INVALID_DESCRIPTOR"));
    var busy = new MediaDeliveryException(MediaDeliveryException.Reason.valueOf("BUSY"));
    var unavailable =
        new MediaDeliveryException(MediaDeliveryException.Reason.valueOf("UNAVAILABLE"));
    assertSame(MediaDeliveryException.Reason.INVALID_DESCRIPTOR, invalid.reason());
    assertSame(MediaDeliveryException.Reason.BUSY, busy.reason());
    assertSame(MediaDeliveryException.Reason.UNAVAILABLE, unavailable.reason());
    assertEquals(503, invalid.httpStatus());
    assertEquals(503, busy.httpStatus());
    assertEquals(503, unavailable.httpStatus());
    assertEquals(OptionalInt.empty(), invalid.retryAfterSeconds());
    assertEquals(OptionalInt.of(1), busy.retryAfterSeconds());
    assertEquals(OptionalInt.empty(), unavailable.retryAfterSeconds());
    assertThrows(
        IllegalArgumentException.class, () -> MediaDeliveryException.Reason.valueOf("busy"));
    assertThrows(
        IllegalArgumentException.class, () -> MediaDeliveryException.Reason.valueOf("OTHER"));
    assertThrows(NullPointerException.class, () -> MediaDeliveryException.Reason.valueOf(null));
  }
}
