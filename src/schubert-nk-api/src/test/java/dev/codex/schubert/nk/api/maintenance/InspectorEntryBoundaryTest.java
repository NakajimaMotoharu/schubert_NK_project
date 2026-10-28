package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-DB-INBOX-669001..004 / SS343354 / PG-D401: no synthetic native admission. */
final class InspectorEntryBoundaryTest {
  private static final String FIXTURE_UNEXPECTED_B0C94341 = "unexpected";

  /** SSC234/PT-DB-CLOSE743001: same completed receipt/callback returns before CLOSING. */
  @Test
  void close743001ClosingRunsAfterCompleteReturnsWithLiteralReceiptAndDiagnostic()
      throws Exception {
    for (boolean enabled : new boolean[] {false, true}) {
      var out = new ByteArrayOutputStream();
      var err = new ByteArrayOutputStream();
      try (var output = new PrintStream(out);
          var diagnostics = new PrintStream(err)) {
        InspectorLauncher.completeAndClose(
            new String[] {FIXTURE_UNEXPECTED_B0C94341},
            Map.of(),
            output,
            settings -> {
              throw new AssertionError("no business IO");
            },
            () -> enabled,
            () -> {
              assertEquals("NKINSPECTOR1 70\n", out.toString(StandardCharsets.UTF_8));
              assertEquals(
                  enabled ? "Inspector fixed PT native capture complete\n" : "",
                  err.toString(StandardCharsets.UTF_8));
              return enabled;
            },
            diagnostics);
      }
      assertEquals(
          enabled
              ? "Inspector fixed PT native capture complete\nInspector fixed PT native closing complete\n"
              : "",
          err.toString(StandardCharsets.UTF_8));
    }
  }

  /** SSC234/PT-DB-CLOSE743002: no marker/fallback on closing failure; null before business. */
  @Test
  void close743002ClosingFailureAndMissingNeverManufactureSuccess() throws Exception {
    var out = new ByteArrayOutputStream();
    var err = new ByteArrayOutputStream();
    try (var output = new PrintStream(out);
        var diagnostics = new PrintStream(err)) {
      InspectorLauncher.Factory factory =
          s -> {
            throw new AssertionError("no IO");
          };
      InspectorLauncher.Capture terminal = () -> true;
      assertThrows(
          IllegalArgumentException.class,
          () ->
              InspectorLauncher.completeAndClose(
                  new String[0], Map.of(), output, factory, terminal, null, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              InspectorLauncher.completeAndClose(
                  new String[0], Map.of(), output, factory, terminal, terminal, null));
      assertEquals(0, out.size());
      var failure = new IOException("PRIVATE");
      assertSame(
          failure,
          assertThrows(
              IOException.class,
              () ->
                  InspectorLauncher.completeAndClose(
                      new String[] {FIXTURE_UNEXPECTED_B0C94341},
                      Map.of(),
                      output,
                      factory,
                      terminal,
                      () -> {
                        throw failure;
                      },
                      diagnostics)));
      assertEquals("NKINSPECTOR1 70\n", out.toString(StandardCharsets.UTF_8));
      assertEquals(
          "Inspector fixed PT native capture complete\n", err.toString(StandardCharsets.UTF_8));
    }
  }

  @Test
  void fixedReceiptBeforeOptionalCaptureWithNoConfigurationIo() throws Exception {
    for (boolean present : new boolean[] {false, true}) {
      var out = new ByteArrayOutputStream();
      var err = new ByteArrayOutputStream();
      try (var output = new PrintStream(out, false, StandardCharsets.UTF_8);
          var diagnostics = new PrintStream(err, false, StandardCharsets.UTF_8)) {
        InspectorLauncher.complete(
            new String[] {FIXTURE_UNEXPECTED_B0C94341},
            Map.of(),
            output,
            s -> {
              throw new AssertionError("configuration rejected before IO");
            },
            () -> {
              assertEquals("NKINSPECTOR1 70\n", out.toString(StandardCharsets.UTF_8));
              return present;
            },
            diagnostics);
      }
      assertEquals("NKINSPECTOR1 70\n", out.toString(StandardCharsets.UTF_8));
      assertEquals(
          present ? "Inspector fixed PT native capture complete\n" : "",
          err.toString(StandardCharsets.UTF_8));
    }
  }

  @Test
  void captureFailurePropagatesWithoutCompleteDiagnostic() throws Exception {
    var out = new ByteArrayOutputStream();
    var err = new ByteArrayOutputStream();
    try (var output = new PrintStream(out, false, StandardCharsets.UTF_8);
        var diagnostics = new PrintStream(err, false, StandardCharsets.UTF_8)) {
      var expected = new IOException("fixed failure");
      assertSame(
          expected,
          assertThrows(
              IOException.class,
              () ->
                  InspectorLauncher.complete(
                      new String[] {FIXTURE_UNEXPECTED_B0C94341},
                      Map.of(),
                      output,
                      s -> {
                        throw new AssertionError("no IO");
                      },
                      () -> {
                        throw expected;
                      },
                      diagnostics)));
    }
    assertEquals("NKINSPECTOR1 70\n", out.toString(StandardCharsets.UTF_8));
    assertEquals(0, err.size());
  }

  @Test
  void outputFailureMustPreventCapture() throws Exception {
    var err = new ByteArrayOutputStream();
    try (var output =
            new PrintStream(
                new OutputStream() {
                  @Override
                  public void write(int value) throws IOException {
                    throw new IOException("untrusted details");
                  }
                });
        var diagnostics = new PrintStream(err, false, StandardCharsets.UTF_8)) {
      var failure =
          assertThrows(
              IOException.class,
              () ->
                  InspectorLauncher.complete(
                      new String[] {FIXTURE_UNEXPECTED_B0C94341},
                      Map.of(),
                      output,
                      s -> {
                        throw new AssertionError("no IO");
                      },
                      () -> {
                        fail("no capture after bad receipt");
                        return true;
                      },
                      diagnostics));
      assertEquals("inspector receipt unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    assertEquals(0, err.size());
  }

  @Test
  void missingEntryPortsRejectBeforeReceiptOrCapture() throws Exception {
    var out = new ByteArrayOutputStream();
    var err = new ByteArrayOutputStream();
    InspectorLauncher.Factory factory =
        s -> {
          throw new AssertionError("no factory");
        };
    InspectorLauncher.Capture capture =
        () -> {
          fail("no capture");
          return true;
        };
    try (var output = new PrintStream(out, false, StandardCharsets.UTF_8);
        var diagnostics = new PrintStream(err, false, StandardCharsets.UTF_8)) {
      assertThrows(
          IllegalArgumentException.class,
          () -> InspectorLauncher.complete(null, Map.of(), output, factory, capture, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              InspectorLauncher.complete(
                  new String[0], null, output, factory, capture, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              InspectorLauncher.complete(
                  new String[0], Map.of(), null, factory, capture, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              InspectorLauncher.complete(
                  new String[0], Map.of(), output, null, capture, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              InspectorLauncher.complete(
                  new String[0], Map.of(), output, factory, null, diagnostics));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              InspectorLauncher.complete(new String[0], Map.of(), output, factory, capture, null));
    }
    assertEquals(0, out.size());
    assertEquals(0, err.size());
  }
}
