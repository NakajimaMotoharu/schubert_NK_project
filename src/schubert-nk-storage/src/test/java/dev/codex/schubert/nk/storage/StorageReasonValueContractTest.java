package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;

/** PT-STORAGE-REASON001; SS333/354 SSC439: fixed public catalog, never storage or DB operations. */
final class StorageReasonValueContractTest {
  @Test
  void reason001ClosedCatalogFactoryAndRedactedFailureKeepTheirIndependentLiteralContract() {
    String[] names = {"COLLISION", "MISSING", "UNAVAILABLE"};
    StorageIoException.Reason[] reasons = StorageIoException.Reason.values();
    assertArrayEquals(names, Arrays.stream(reasons).map(Enum::name).toArray(String[]::new));
    for (int index = 0; index < names.length; index++) {
      StorageIoException.Reason reason = reasons[index];
      assertEquals(index, reason.ordinal());
      assertEquals(names[index], reason.name());
      assertSame(reason, StorageIoException.Reason.valueOf(names[index]));
      StorageIoException failure = new StorageIoException(reason);
      assertSame(reason, failure.reason());
      assertEquals("transfer storage operation failed", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    StorageIoException.Reason[] copy = StorageIoException.Reason.values();
    assertNotSame(reasons, copy);
    copy[0] = null;
    assertSame(StorageIoException.Reason.COLLISION, StorageIoException.Reason.values()[0]);
    for (String unknown : List.of("", "collision", "COLLISION ", "UNKNOWN")) {
      assertThrows(
          IllegalArgumentException.class, () -> StorageIoException.Reason.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> StorageIoException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new StorageIoException(null));
  }
}
