package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-F03-EXC001; SS324/352/BUG1482/YKT1237: finite SQL exception values, no connection. */
final class ExceptionValueContractTest {
  @Test
  void exc001InboxAndResponseReasonsPreserveValuesSqlStateAndCause() {
    var states =
        Map.of(
            "MESSAGE_ID_REUSE",
            "23000",
            "OPERATION_TOKEN_REUSE",
            "23000",
            "FINGERPRINT_KEY_UNAVAILABLE",
            "55000",
            "STATE_CORRUPT",
            "XX000",
            "TRANSACTION_REQUIRED",
            "25000");
    for (var reason : InboxException.Reason.values()) {
      var failure = new InboxException(reason, "bounded inbox failure");
      assertSame(reason, failure.reason());
      assertEquals(states.get(reason.name()), failure.getSQLState());
      assertEquals("bounded inbox failure", failure.getMessage());
    }
    assertThrows(NullPointerException.class, () -> new InboxException(null, "bounded"));
    for (var reason : ResponseSnapshotException.Reason.values()) {
      var plain = new ResponseSnapshotException(reason, "bounded snapshot failure");
      assertSame(reason, plain.reason());
      assertEquals("bounded snapshot failure", plain.getMessage());
      assertNull(plain.getCause());
      var cause = new IllegalStateException("synthetic cause");
      var caused = new ResponseSnapshotException(reason, "bounded snapshot failure", cause);
      assertSame(reason, caused.reason());
      assertSame(cause, caused.getCause());
    }
    assertThrows(NullPointerException.class, () -> new ResponseSnapshotException(null, "bounded"));
    assertThrows(
        NullPointerException.class, () -> new ResponseSnapshotException(null, "bounded", null));
  }
}
