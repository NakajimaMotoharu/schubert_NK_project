package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.sql.SQLException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** NK-PRO-003/FIL001..009/UI237/SS333/BUG2718: public memory objects, no resource capability. */
@Timeout(10)
final class StorageFailureGraphTest {
  @Test
  void fixedReasonsAndNullContract() {
    for (StorageIoException.Reason reason : StorageIoException.Reason.values()) {
      var failure = new StorageIoException(reason);
      assertSame(reason, failure.reason());
      assertEquals("transfer storage operation failed", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertDoesNotThrow(() -> StorageIoException.preserveFatal(failure));
    }
    assertThrows(NullPointerException.class, () -> new StorageIoException(null));
    assertThrows(NullPointerException.class, () -> StorageIoException.preserveFatal(null));
  }

  @Test
  void directCauseAndSuppressedIdentityAndOrder() {
    var first = new AssertionError("public first");
    var second = new AssertionError("public second");
    assertSame(first, assertThrows(Error.class, () -> StorageIoException.preserveFatal(first)));
    var root = new IOException("public wrapper", first);
    root.addSuppressed(second);
    assertSame(first, assertThrows(Error.class, () -> StorageIoException.preserveFatal(root)));
    var suppressed = new IOException("public wrapper");
    suppressed.addSuppressed(second);
    assertSame(
        second, assertThrows(Error.class, () -> StorageIoException.preserveFatal(suppressed)));
    assertSame(first, root.getCause());
    assertSame(second, root.getSuppressed()[0]);
    assertEquals(1, root.getSuppressed().length);
  }

  @Test
  void sqlNextAndMixedEdgesRetainIdentity() {
    var fatal = new LinkageError("public fatal");
    var next = new SQLException("public next", fatal);
    var sql = new SQLException("public head");
    sql.setNextException(next);
    var outer = new IOException("public outer", sql);
    outer.addSuppressed(next);
    assertSame(fatal, assertThrows(Error.class, () -> StorageIoException.preserveFatal(outer)));
    assertSame(next, sql.getNextException());
    assertSame(fatal, next.getCause());
    assertEquals(0, sql.getSuppressed().length);
    var earlier = new AssertionError("public suppressed first");
    sql.addSuppressed(earlier);
    assertSame(earlier, assertThrows(Error.class, () -> StorageIoException.preserveFatal(sql)));
  }

  @Test
  void nonFatalCyclesAndDuplicateEdgesFinishWithoutMutation() {
    var first = new IOException("public first");
    var second = new SQLException("public second");
    var third = new SQLException("public third");
    first.initCause(second);
    second.initCause(first);
    second.setNextException(third);
    third.initCause(first);
    first.addSuppressed(third);
    third.addSuppressed(second);
    assertDoesNotThrow(() -> StorageIoException.preserveFatal(first));
    assertSame(second, first.getCause());
    assertSame(first, second.getCause());
    assertSame(third, second.getNextException());
    assertSame(first, third.getCause());
    assertSame(third, first.getSuppressed()[0]);
    assertSame(second, third.getSuppressed()[0]);
    assertEquals(1, first.getSuppressed().length);
    assertEquals(1, third.getSuppressed().length);
    assertDoesNotThrow(() -> StorageIoException.preserveFatal(new IOException("public plain")));
  }
}
