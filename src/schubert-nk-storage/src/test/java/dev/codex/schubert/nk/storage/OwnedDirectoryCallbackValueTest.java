package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.lang.reflect.Proxy;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.NoSuchFileException;
import java.security.NoSuchAlgorithmException;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS333 §7.3 and SSC-461. Synthetic callbacks never use their path or a real descriptor. */
final class OwnedDirectoryCallbackValueTest {
  private static final String PRIVATE_DIAGNOSTIC = "SYNTHETIC_CALLBACK_DETAIL";
  private static final int DESCRIPTOR = 245;

  /** PT-STORAGE-CB001. */
  @Test
  void callback001SuccessKeepsTheResultAndDirectoryOwnership() throws StorageIoException {
    var calls = new Calls();
    var expected = new Object();
    try (var directory = OwnedTransferDirectory.openRoot(calls.port())) {
      assertSame(expected, directory.atDirectory(ignored -> expected));
      assertEquals(1, calls.opened);
      assertEquals(0, calls.closed);
    }
    assertEquals(1, calls.closed);
  }

  /** PT-STORAGE-CB002. */
  @Test
  void callback002ExpectedFileFailureCategoriesDropProviderDiagnostics() throws StorageIoException {
    var cases =
        List.of(
            new FileFailure(new FileAlreadyExistsException(PRIVATE_DIAGNOSTIC), "COLLISION"),
            new FileFailure(new NoSuchFileException(PRIVATE_DIAGNOSTIC), "MISSING"),
            new FileFailure(new IOException(PRIVATE_DIAGNOSTIC), "UNAVAILABLE"),
            new FileFailure(new NoSuchAlgorithmException(PRIVATE_DIAGNOSTIC), "UNAVAILABLE"));
    var calls = new Calls();
    try (var directory = OwnedTransferDirectory.openRoot(calls.port())) {
      for (var sample : cases) {
        var failure =
            assertThrows(
                StorageIoException.class, () -> directory.atDirectory(ignored -> sample.raise()));
        assertEquals(sample.reason(), failure.reason().name());
        assertEquals("transfer storage operation failed", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertEquals(0, calls.closed);
      }
    }
    assertEquals(1, calls.closed);
  }

  /** PT-STORAGE-CB003. */
  @Test
  void callback003EachConversionPropagatesTheOriginalFatalBeforeRedaction()
      throws StorageIoException {
    var calls = new Calls();
    try (var directory = OwnedTransferDirectory.openRoot(calls.port())) {
      var failures =
          List.of(
              new FileAlreadyExistsException(PRIVATE_DIAGNOSTIC),
              new NoSuchFileException(PRIVATE_DIAGNOSTIC),
              new IOException(PRIVATE_DIAGNOSTIC),
              new NoSuchAlgorithmException(PRIVATE_DIAGNOSTIC));
      for (var failure : failures) {
        var fatal = new AssertionError("SYNTHETIC_FATAL");
        failure.addSuppressed(fatal);
        var sample = new FileFailure(failure, "");
        assertSame(
            fatal,
            assertThrows(AssertionError.class, () -> directory.atDirectory(ignored -> sample.raise())));
        assertEquals(0, calls.closed);
      }
      assertEquals("still-owned", directory.atDirectory(ignored -> "still-owned"));
    }
    assertEquals(1, calls.closed);
  }

  private record FileFailure(Exception exception, String reason) {
    Object raise() throws IOException, NoSuchAlgorithmException {
      if (exception instanceof IOException failure) throw failure;
      throw (NoSuchAlgorithmException) exception;
    }
  }

  private static final class Calls {
    int opened;
    int closed;

    DirectoryCalls port() {
      return (DirectoryCalls)
          Proxy.newProxyInstance(
              DirectoryCalls.class.getClassLoader(),
              new Class<?>[] {DirectoryCalls.class},
              (proxy, method, arguments) ->
                  switch (method.getName()) {
                    case "openRoot" -> {
                      opened++;
                      yield DESCRIPTOR;
                    }
                    case "close" -> {
                      assertEquals(DESCRIPTOR, arguments[0]);
                      closed++;
                      yield null;
                    }
                    default -> throw new AssertionError("unexpected directory port");
                  });
    }
  }
}
