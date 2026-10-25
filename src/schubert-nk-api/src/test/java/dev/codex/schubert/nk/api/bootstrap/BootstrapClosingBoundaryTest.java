package dev.codex.schubert.nk.api.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** SSC234/SS343354/PT-ADM-CLOSE743001..003: same main body, independent literal status/order. */
class BootstrapClosingBoundaryTest {
  @Test
  void close743001SameMainTerminalReturnDiagnosticClosingThenOriginalExit() throws Exception {
    for (int status : new int[] {0, 20, 50, 70}) {
      for (boolean enabled : new boolean[] {true, false}) {
        var bytes = new ByteArrayOutputStream();
        var events = new ArrayList<String>();
        try (var diagnostics = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
          new BootstrapAdminMain(
                  Map.of("public", "fixture"),
                  (args, env) -> {
                    assertArrayEquals(new String[0], args);
                    assertEquals(Map.of("public", "fixture"), env);
                    events.add("business-return");
                    return status;
                  },
                  () -> {
                    events.add("terminal-return");
                    return enabled;
                  },
                  () -> {
                    assertEquals(
                        "Initial ADMIN bootstrap finished\n"
                            + (enabled ? "Bootstrap fixed PT native capture complete\n" : ""),
                        bytes.toString(StandardCharsets.UTF_8));
                    events.add("closing-return");
                    return enabled;
                  },
                  diagnostics,
                  actual -> {
                    assertEquals(status, actual);
                    events.add("exit-" + actual);
                  })
              .main(new String[0]);
        }
        assertEquals(
            List.of("business-return", "terminal-return", "closing-return", "exit-" + status),
            events);
        assertEquals(
            "Initial ADMIN bootstrap finished\n"
                + (enabled
                    ? "Bootstrap fixed PT native capture complete\nBootstrap fixed PT native closing complete\n"
                    : ""),
            bytes.toString(StandardCharsets.UTF_8));
      }
    }
  }

  @Test
  void close743002ClosingFailuresNeverEmitCompletionAndAreFixed50() throws Exception {
    for (boolean error : new boolean[] {false, true}) {
      var bytes = new ByteArrayOutputStream();
      try (var diagnostics = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
        new BootstrapAdminMain(
                Map.of(),
                (a, e) -> 20,
                () -> true,
                () -> {
                  if (error) throw new AssertionError("PRIVATE");
                  throw new IOException("PRIVATE");
                },
                diagnostics,
                status -> assertEquals(50, status))
            .main(new String[0]);
      }
      assertEquals(
          "Initial ADMIN bootstrap finished\nBootstrap fixed PT native capture complete\nInitial ADMIN bootstrap failed\n",
          bytes.toString(StandardCharsets.UTF_8));
    }
  }

  @Test
  void close743003MissingPortsRefuseBeforeAnyOperationOrTermination() {
    BootstrapAdminMain.Operation op =
        (a, e) -> {
          fail("no business");
          return 0;
        };
    BootstrapAdminMain.Capture capture =
        () -> {
          fail("no measurement");
          return true;
        };
    java.util.function.IntConsumer exit = status -> fail("no termination");
    assertThrows(
        IllegalArgumentException.class,
        () -> new BootstrapAdminMain(null, op, capture, capture, System.err, exit));
    assertThrows(
        IllegalArgumentException.class,
        () -> new BootstrapAdminMain(Map.of(), null, capture, capture, System.err, exit));
    assertThrows(
        IllegalArgumentException.class,
        () -> new BootstrapAdminMain(Map.of(), op, null, capture, System.err, exit));
    assertThrows(
        IllegalArgumentException.class,
        () -> new BootstrapAdminMain(Map.of(), op, capture, null, System.err, exit));
    assertThrows(
        IllegalArgumentException.class,
        () -> new BootstrapAdminMain(Map.of(), op, capture, capture, null, exit));
    assertThrows(
        IllegalArgumentException.class,
        () -> new BootstrapAdminMain(Map.of(), op, capture, capture, System.err, null));
  }
}
