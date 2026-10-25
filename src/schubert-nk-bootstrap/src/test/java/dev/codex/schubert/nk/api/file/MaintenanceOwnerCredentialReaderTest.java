package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.Fixture;
import dev.codex.schubert.nk.api.file.InspectorCredentialLoaderTest.TestIo;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-MOWNER-READ001..003; SS343/SSC119, opaque public fixture bytes, no Unit admission. */
final class MaintenanceOwnerCredentialReaderTest {
  @TempDir Path temporary;
  private static final String NAME = "maintenance-owner";

  @Test
  void owner001LiteralBoundsAreCallerOwnedAndScratchIsCleared() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      for (int length : new int[] {1, 1024}) {
        byte[] expected = new byte[length];
        Arrays.fill(expected, (byte) 'A');
        Files.write(fixture.root.resolve(NAME), expected);
        var io = new TestIo();
        io.maxRead = 17;
        byte[] actual = fixture.loader(io).readMaintenanceOwner();
        try {
          assertArrayEquals(expected, actual);
        } finally {
          Arrays.fill(actual, (byte) 0);
        }
        assertArrayEquals(expected, Files.readAllBytes(fixture.root.resolve(NAME)));
        assertEquals(1, io.opens);
        assertEquals(1, io.closes);
        io.assertCleared(1025);
      }
    }
  }

  @Test
  void owner002MissingFixedNameEmptyAndOverflowDoNotReturnBytes() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      Files.writeString(fixture.root.resolve("maintenance-owner-alternate"), "PUBLIC");
      var missing = new TestIo();
      rejected(fixture, missing);
      assertEquals(0, missing.opens);
      for (int length : new int[] {0, 1025, 65537}) {
        Files.write(fixture.root.resolve(NAME), new byte[length]);
        var io = new TestIo();
        rejected(fixture, io);
        assertEquals(io.opens, io.closes);
        io.assertCleared(1025);
      }
    }
  }

  @Test
  void owner003EveryIoAndCloseFailureWithholdsTheResultAndClearsScratch() throws Exception {
    try (var fixture = new Fixture(temporary)) {
      Files.writeString(fixture.root.resolve(NAME), "PUBLIC-OPAQUE-READER-FIXTURE");
      for (String fault :
          List.of(
              "attributes-root",
              "attributes-file",
              "open",
              "unsupported",
              "read",
              "short",
              "zero",
              "lying-read",
              "negative-read",
              "huge-read",
              "size-error-after",
              "close",
              "root-final")) {
        var io = new TestIo();
        io.fault = fault;
        rejected(fixture, io);
        assertEquals(io.opens, io.closes, fault);
        io.assertCleared(1025);
      }
    }
  }

  private static void rejected(Fixture fixture, TestIo io) {
    var error =
        assertThrows(
            InspectorCredentialException.class, () -> fixture.loader(io).readMaintenanceOwner());
    assertEquals("inspector credential cannot be loaded", error.getMessage());
    assertNull(error.getCause());
    assertEquals(0, error.getSuppressed().length);
  }
}
