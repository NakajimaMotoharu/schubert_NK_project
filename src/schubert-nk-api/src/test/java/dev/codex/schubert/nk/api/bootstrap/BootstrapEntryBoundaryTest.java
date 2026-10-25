package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-ADM-BOOT669001..005 / SS343354 / PG-D401: internal composition, no Unit proof. */
final class BootstrapEntryBoundaryTest {
  @Test
  void fixedNormalStatusAndAbsentOrPresentCaptureOrder() throws Exception {
    for (int status : new int[] {0, 20, 50, 70}) {
      for (boolean captured : new boolean[] {false, true}) {
        var bytes = new ByteArrayOutputStream();
        var events = new ArrayList<String>();
        try (var diagnostics = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
          assertEquals(
              status,
              BootstrapAdminMain.launch(
                  new String[] {"argument"},
                  Map.of("key", "value"),
                  (arguments, environment) -> {
                    assertArrayEquals(new String[] {"argument"}, arguments);
                    assertEquals(Map.of("key", "value"), environment);
                    events.add("run");
                    return status;
                  },
                  () -> {
                    assertEquals(
                        "Initial ADMIN bootstrap finished\n",
                        bytes.toString(StandardCharsets.UTF_8));
                    events.add("capture");
                    return captured;
                  },
                  diagnostics));
        }
        assertEquals(List.of("run", "capture"), events);
        assertEquals(
            "Initial ADMIN bootstrap finished\n"
                + (captured ? "Bootstrap fixed PT native capture complete\n" : ""),
            bytes.toString(StandardCharsets.UTF_8));
      }
    }
  }

  @Test
  void operationFailureStillCapturesOnlyAfterFixedDiagnostic() throws Exception {
    for (boolean error : new boolean[] {false, true}) {
      var bytes = new ByteArrayOutputStream();
      try (var diagnostics = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
        assertEquals(
            50,
            BootstrapAdminMain.launch(
                new String[0],
                Map.of(),
                (a, e) -> {
                  if (error) throw new AssertionError("untrusted details");
                  throw new IOException("untrusted details");
                },
                () -> {
                  assertEquals(
                      "Initial ADMIN bootstrap failed\nInitial ADMIN bootstrap finished\n",
                      bytes.toString(StandardCharsets.UTF_8));
                  return true;
                },
                diagnostics));
      }
      assertEquals(
          "Initial ADMIN bootstrap failed\nInitial ADMIN bootstrap finished\nBootstrap fixed PT native capture complete\n",
          bytes.toString(StandardCharsets.UTF_8));
      assertFalse(bytes.toString(StandardCharsets.UTF_8).contains("untrusted"));
    }
  }

  @Test
  void captureFailureIsNonSuccessWithNoFakeComplete() throws Exception {
    for (boolean error : new boolean[] {false, true}) {
      var bytes = new ByteArrayOutputStream();
      try (var diagnostics = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
        assertEquals(
            50,
            BootstrapAdminMain.launch(
                new String[0],
                Map.of(),
                (a, e) -> 20,
                () -> {
                  if (error) throw new AssertionError("untrusted details");
                  throw new IOException("untrusted details");
                },
                diagnostics));
      }
      assertEquals(
          "Initial ADMIN bootstrap finished\nInitial ADMIN bootstrap failed\n",
          bytes.toString(StandardCharsets.UTF_8));
    }
  }

  @Test
  void everyDeclaredCheckedFamilyRemainsFixedNonSuccess() throws Exception {
    for (int kind : new int[] {0, 1, 2}) {
      var bytes = new ByteArrayOutputStream();
      try (var diagnostics = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
        assertEquals(
            50,
            BootstrapAdminMain.launch(
                new String[0],
                Map.of(),
                (arguments, environment) -> {
                  if (kind == 0) throw new IOException("untrusted details");
                  if (kind == 1) throw new SQLException("untrusted details");
                  throw new NoSuchAlgorithmException("untrusted details");
                },
                () -> false,
                diagnostics));
      }
      assertEquals(
          "Initial ADMIN bootstrap failed\nInitial ADMIN bootstrap finished\n",
          bytes.toString(StandardCharsets.UTF_8));
    }
  }

  @Test
  void missingDependenciesRejectBeforeOperationOrCapture() throws Exception {
    var bytes = new ByteArrayOutputStream();
    BootstrapAdminMain.Operation operation =
        (a, e) -> {
          fail("operation must not run");
          return 0;
        };
    BootstrapAdminMain.Capture capture =
        () -> {
          fail("capture must not run");
          return false;
        };
    try (var diagnostics = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
      assertThrows(
          IllegalArgumentException.class,
          () -> BootstrapAdminMain.launch(null, Map.of(), operation, capture, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () -> BootstrapAdminMain.launch(new String[0], null, operation, capture, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () -> BootstrapAdminMain.launch(new String[0], Map.of(), null, capture, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () -> BootstrapAdminMain.launch(new String[0], Map.of(), operation, null, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () -> BootstrapAdminMain.launch(new String[0], Map.of(), operation, capture, null));
    }
    assertEquals(0, bytes.size());
  }
}
