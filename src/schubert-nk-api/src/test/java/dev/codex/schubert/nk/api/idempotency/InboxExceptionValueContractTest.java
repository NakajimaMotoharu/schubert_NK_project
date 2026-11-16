package dev.codex.schubert.nk.api.idempotency;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-IDEM-REASONVALUE001; DAT009/UI241242/SS324/352/354; synthetic SQL exception data only. */
final class InboxExceptionValueContractTest {
  @Test
  void reasonValue001ClosedCatalogSqlStateAndDefensiveEnumLookup() {
    String[] names = {
      "MESSAGE_ID_REUSE",
      "OPERATION_TOKEN_REUSE",
      "FINGERPRINT_KEY_UNAVAILABLE",
      "STATE_CORRUPT",
      "TRANSACTION_REQUIRED"
    };
    String[] sqlStates = {"23000", "23000", "55000", "XX000", "25000"};
    InboxException.Reason[] values = InboxException.Reason.values();
    assertArrayEquals(names, Arrays.stream(values).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < values.length; i++) {
      assertEquals(i, values[i].ordinal());
      assertSame(values[i], InboxException.Reason.valueOf(names[i]));
      InboxException value = new InboxException(values[i], "BOUNDED_PUBLIC");
      assertSame(values[i], value.reason());
      assertEquals(sqlStates[i], value.getSQLState());
      assertEquals("BOUNDED_PUBLIC", value.getMessage());
      assertEquals(0, value.getErrorCode());
      assertNull(value.getCause());
      assertNull(value.getNextException());
      assertEquals(0, value.getSuppressed().length);
    }
    InboxException.Reason[] copy = InboxException.Reason.values();
    assertNotSame(values, copy);
    copy[0] = null;
    assertSame(InboxException.Reason.MESSAGE_ID_REUSE, InboxException.Reason.values()[0]);
    for (String invalid : List.of("", "message_id_reuse", "MESSAGE_ID_REUSE ", "UNKNOWN")) {
      assertThrows(IllegalArgumentException.class, () -> InboxException.Reason.valueOf(invalid));
    }
    assertThrows(NullPointerException.class, () -> InboxException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new InboxException(null, "BOUNDED_PUBLIC"));
  }
}
