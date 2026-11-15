package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-STORAGE-PUBLIC001002; SS333/354 SSC440: synthetic Throwable graphs, no JDBC driver or IO. */
@Timeout(10)
final class StoragePublicContractTest {
  private static final String PUBLIC = "PUBLIC_SYNTHETIC";

  @Test
  void public001ClosedReasonAndFixedStorageFailureExposeNoProviderDiagnostics() {
    String[] names = {"COLLISION", "MISSING", "UNAVAILABLE"};
    StorageIoException.Reason[] values = StorageIoException.Reason.values();
    assertArrayEquals(names, Arrays.stream(values).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < names.length; i++) {
      assertEquals(i, values[i].ordinal());
      assertSame(values[i], StorageIoException.Reason.valueOf(names[i]));
      StorageIoException failure = new StorageIoException(values[i]);
      assertSame(values[i], failure.reason());
      assertEquals("transfer storage operation failed", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    StorageIoException.Reason[] copy = StorageIoException.Reason.values();
    assertNotSame(values, copy);
    copy[0] = null;
    assertSame(StorageIoException.Reason.COLLISION, StorageIoException.Reason.values()[0]);
    for (String unknown : List.of("", "collision", "COLLISION ", "UNKNOWN")) {
      assertThrows(
          IllegalArgumentException.class, () -> StorageIoException.Reason.valueOf(unknown));
    }
    assertThrows(NullPointerException.class, () -> StorageIoException.Reason.valueOf(null));
    assertThrows(NullPointerException.class, () -> new StorageIoException(null));
  }

  @Test
  void public002FatalIdentityBreadthFirstOrderAndFiniteSharedCyclesRemainIndependentOfEquality() {
    Error fatal = new AssertionError(PUBLIC);
    RuntimeException cause = new IllegalStateException(PUBLIC, fatal);
    RuntimeException suppressed = new IllegalStateException(PUBLIC);
    suppressed.addSuppressed(fatal);
    SqlLink nextRoot = new SqlLink();
    SqlLink next = new SqlLink();
    next.initCause(fatal);
    nextRoot.next = next;
    for (Throwable root : List.of(fatal, cause, suppressed, nextRoot)) {
      Throwable oldCause = root.getCause();
      Throwable[] oldSuppressed = root.getSuppressed();
      assertSame(fatal, assertThrows(Error.class, () -> StorageIoException.preserveFatal(root)));
      assertSame(oldCause, root.getCause());
      assertArrayEquals(oldSuppressed, root.getSuppressed());
    }
    Error first = new AssertionError(PUBLIC);
    Error second = new LinkageError(PUBLIC);
    RuntimeException directPriority = new IllegalStateException(PUBLIC, first);
    directPriority.addSuppressed(second);
    assertSame(
        first, assertThrows(Error.class, () -> StorageIoException.preserveFatal(directPriority)));
    RuntimeException breadthPriority =
        new IllegalStateException(PUBLIC, new IllegalStateException(PUBLIC, first));
    breadthPriority.addSuppressed(second);
    assertSame(
        second, assertThrows(Error.class, () -> StorageIoException.preserveFatal(breadthPriority)));
    EqualThrowable equalSafe = new EqualThrowable();
    EqualThrowable equalFatal = new EqualThrowable();
    equalFatal.initCause(fatal);
    assertEquals(equalSafe, equalFatal);
    assertNotSame(equalSafe, equalFatal);
    RuntimeException rootWithEqualNodes = new IllegalStateException(PUBLIC);
    rootWithEqualNodes.addSuppressed(equalSafe);
    rootWithEqualNodes.addSuppressed(equalFatal);
    assertSame(
        fatal,
        assertThrows(Error.class, () -> StorageIoException.preserveFatal(rootWithEqualNodes)));
    RuntimeException cycle = new IllegalStateException(PUBLIC);
    IOException shared = new IOException(PUBLIC);
    cycle.initCause(shared);
    shared.initCause(cycle);
    cycle.addSuppressed(shared);
    SqlLink sqlCycle = new SqlLink();
    SqlLink sqlOther = new SqlLink();
    sqlCycle.next = sqlOther;
    sqlOther.next = sqlCycle;
    sqlOther.initCause(shared);
    assertDoesNotThrow(() -> StorageIoException.preserveFatal(cycle));
    assertDoesNotThrow(() -> StorageIoException.preserveFatal(sqlCycle));
    assertSame(sqlOther, sqlCycle.next);
    assertSame(sqlCycle, sqlOther.next);
    assertSame(shared, sqlOther.getCause());
    assertThrows(NullPointerException.class, () -> StorageIoException.preserveFatal(null));
  }

  private static final class SqlLink extends SQLException {
    private static final long serialVersionUID = 1L;
    private @Nullable SQLException next;

    SqlLink() {
      super(PUBLIC);
    }

    @Override
    public @Nullable SQLException getNextException() {
      return next;
    }
  }

  private static final class EqualThrowable extends RuntimeException {
    private static final long serialVersionUID = 1L;

    EqualThrowable() {
      super(PUBLIC);
    }

    @Override
    public boolean equals(@Nullable Object other) {
      return other instanceof EqualThrowable;
    }

    @Override
    public int hashCode() {
      return 0;
    }
  }
}
