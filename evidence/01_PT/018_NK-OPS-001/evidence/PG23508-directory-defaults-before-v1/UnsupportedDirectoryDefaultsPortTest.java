package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

/** PT-SCN-DDEFAULT-001..004; RD FIL001..009/UI241/SS333§7.3,7.6,12. No actual FD or I/O. */
@Timeout(10)
final class UnsupportedDirectoryDefaultsPortTest {
  private static final String FIXED_MESSAGE = "transfer storage operation failed";

  @Test
  void defaults001PrivateFileUnsupportedHasNoPublicFileFallback() {
    var calls = new RejectingCalls();
    for (int parent : List.of(0, 7, Integer.MIN_VALUE, Integer.MAX_VALUE)) {
      var failure =
          assertThrows(StorageIoException.class, () -> calls.createPrivateFile(parent, "part"));
      assertFailure(failure);
    }
    assertEquals(0, calls.abstractCalls);
  }

  @Test
  void defaults002PrivateDirectoryUnsupportedHasNoPublicDirectoryFallback() {
    var calls = new RejectingCalls();
    for (String name : List.of("child", "", ".", "..", "bad/name", "bad\u0000name")) {
      var failure =
          assertThrows(StorageIoException.class, () -> calls.createPrivateDirectory(7, name));
      assertFailure(failure);
    }
    assertEquals(0, calls.abstractCalls);
  }

  @Test
  void defaults003EmptyDirectoryUnsupportedNeverDelegatesToUnlinkOrRootClose() {
    var calls = new RejectingCalls();
    for (String name : List.of("child", "", ".", "..", "bad/name")) {
      var failure =
          assertThrows(StorageIoException.class, () -> calls.removeEmptyDirectory(7, name));
      assertFailure(failure);
    }
    assertEquals(0, calls.abstractCalls);
  }

  @Test
  void defaults004EveryDeclinedOperationHasFreshBoundedExceptionState() {
    var calls = new RejectingCalls();
    var first = assertThrows(StorageIoException.class, () -> calls.createPrivateFile(7, "part"));
    first.addSuppressed(new IllegalStateException("synthetic previous caller"));
    var second =
        assertThrows(StorageIoException.class, () -> calls.createPrivateDirectory(7, "child"));
    var third =
        assertThrows(StorageIoException.class, () -> calls.removeEmptyDirectory(7, "child"));
    assertNotSame(first, second);
    assertNotSame(first, third);
    assertNotSame(second, third);
    assertFailure(second);
    assertFailure(third);
    assertEquals(1, first.getSuppressed().length);
    assertEquals(0, calls.abstractCalls);
  }

  private static void assertFailure(StorageIoException failure) {
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertEquals(FIXED_MESSAGE, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
    assertEquals(StorageIoException.class, failure.getClass());
  }

  /** Only three inherited default methods may execute; nine abstract ports always reject. */
  private static final class RejectingCalls implements DirectoryCalls {
    private int abstractCalls;

    private AssertionError unexpected() {
      abstractCalls++;
      return new AssertionError("unexpected abstract directory operation");
    }

    @Override
    public int openRoot() {
      throw unexpected();
    }

    @Override
    public int openDirectory(int parent, String name) {
      throw unexpected();
    }

    @Override
    public int openEntry(int parent, String name) {
      throw unexpected();
    }

    @Override
    public int createFile(int parent, String name) {
      throw unexpected();
    }

    @Override
    public void createDirectory(int parent, String name) {
      throw unexpected();
    }

    @Override
    public void publish(int directory, String part, String ready) {
      throw unexpected();
    }

    @Override
    public void unlink(int directory, String name) {
      throw unexpected();
    }

    @Override
    public void sync(int directory) {
      throw unexpected();
    }

    @Override
    public void close(int directory) {
      throw unexpected();
    }
  }
}
