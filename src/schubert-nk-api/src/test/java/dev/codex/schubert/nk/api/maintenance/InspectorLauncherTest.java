package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.file.InspectorCredentialException;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-DB-INBOX-225..232; fixed receipt/status oracles and real main/native negative boundaries. */
final class InspectorLauncherTest {
  private static final String FIXTURE_UNTRUSTED_6FC6869D = "UNTRUSTED";
  @TempDir Path root;

  private Map<String, String> environment() {
    return InspectorLaunchConfigurationTest.environment(root);
  }

  @Test
  void successWarningAndFailureStatus() {
    var launcher = new InspectorLauncher();
    for (var status : InspectionExecution.Status.values()) {
      int expected =
          switch (status) {
            case SUCCESS -> 0;
            case WARNING -> 10;
            case TIME_LIMIT, INTERRUPTED, STORAGE_FAILURE -> 50;
          };
      assertEquals(
          expected,
          launcher.run(
              new String[0],
              environment(),
              settings -> {
                assertEquals(root, settings.credentialRoot());
                assertEquals(Set.of("fp1", "old-v.2"), settings.fingerprintVersions());
                return run -> {
                  assertEquals(InspectorLaunchConfigurationTest.ID, run.id().toString());
                  assertEquals(InspectorLaunchConfigurationTest.CUTOFF, run.cutoff().toString());
                  return result(status, run);
                };
              }));
    }
  }

  @Test
  void expectedFailuresAndRedaction() {
    var launcher = new InspectorLauncher();
    assertEquals(
        70,
        launcher.run(
            new String[] {FIXTURE_UNTRUSTED_6FC6869D},
            environment(),
            s -> {
              throw new AssertionError("no IO");
            }));
    assertEquals(
        70,
        launcher.run(
            new String[0],
            environment(),
            s ->
                r -> {
                  throw new InspectorCredentialException();
                }));
    assertEquals(
        70,
        launcher.run(
            new String[0],
            environment(),
            s ->
                r -> {
                  throw new NoSuchAlgorithmException("UNTRUSTED_SECRET");
                }));
    assertEquals(
        50,
        launcher.run(
            new String[0],
            environment(),
            s ->
                r -> {
                  throw new IOException("UNTRUSTED_SECRET");
                }));
    assertThrows(
        IllegalStateException.class,
        () ->
            launcher.run(
                new String[0],
                environment(),
                s ->
                    r -> {
                      throw new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D);
                    }));
  }

  @Test
  void nativeFactoryFailure() throws Exception {
    var launcher = new InspectorLauncher();
    // SSC119/BUG359: no genuine Unit/OS actor, so IO admission50 precedes any credential70.
    assertEquals(50, launcher.run(new String[0], environment()));
    var missing = environment();
    missing.put("CREDENTIALS_DIRECTORY", root.resolve("missing").toString());
    assertEquals(50, launcher.run(new String[0], missing));
    try (var contents = Files.list(root)) {
      assertEquals(0, contents.count());
    }
  }

  @Test
  void receiptAndOutputFailure() throws Exception {
    var launcher = new InspectorLauncher();
    for (var status : InspectionExecution.Status.values()) {
      int expected =
          switch (status) {
            case SUCCESS -> 0;
            case WARNING -> 10;
            case TIME_LIMIT, INTERRUPTED, STORAGE_FAILURE -> 50;
          };
      var bytes = new ByteArrayOutputStream();
      try (var output = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
        launcher.write(new String[0], environment(), output, s -> r -> result(status, r));
      }
      assertArrayEquals(
          ("NKINSPECTOR1 " + expected + "\n").getBytes(StandardCharsets.US_ASCII),
          bytes.toByteArray());
    }
    try (var output =
        new PrintStream(
            new OutputStream() {
              @Override
              public void write(int value) throws IOException {
                throw new IOException(FIXTURE_UNTRUSTED_6FC6869D);
              }
            })) {
      var failure =
          assertThrows(
              IOException.class,
              () ->
                  launcher.write(
                      new String[0],
                      environment(),
                      output,
                      s -> r -> result(InspectionExecution.Status.SUCCESS, r)));
      assertEquals("inspector receipt unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
  }

  @Test
  void nullContracts() throws Exception {
    var launcher = new InspectorLauncher();
    InspectorLauncher.Factory good = s -> r -> result(InspectionExecution.Status.SUCCESS, r);
    assertThrows(NullPointerException.class, () -> launcher.run(null, environment(), good));
    assertThrows(NullPointerException.class, () -> launcher.run(new String[0], null, good));
    assertThrows(
        NullPointerException.class, () -> launcher.run(new String[0], environment(), null));
    assertThrows(
        NullPointerException.class, () -> launcher.run(new String[0], environment(), s -> null));
    assertThrows(
        NullPointerException.class,
        () -> launcher.run(new String[0], environment(), s -> r -> null));
    assertThrows(
        NullPointerException.class, () -> launcher.write(new String[0], environment(), null, good));
  }

  @Test
  void mainAndFatalHandler() throws Exception {
    var thread = Thread.currentThread();
    var originalHandler = thread.getUncaughtExceptionHandler();
    var originalOut = System.out;
    var originalErr = System.err;
    var bytes = new ByteArrayOutputStream();
    var errors = new ByteArrayOutputStream();
    try (var output = new PrintStream(bytes, false, StandardCharsets.UTF_8);
        var error = new PrintStream(errors, false, StandardCharsets.UTF_8)) {
      try {
        System.setOut(output);
        System.setErr(error);
        InspectorLauncher.main(new String[] {FIXTURE_UNTRUSTED_6FC6869D});
        assertEquals("NKINSPECTOR1 70\n", bytes.toString(StandardCharsets.UTF_8));
        assertEquals("", errors.toString(StandardCharsets.UTF_8));
        thread
            .getUncaughtExceptionHandler()
            .uncaughtException(thread, new IllegalStateException("UNTRUSTED_SECRET"));
        assertEquals("inspector failed\n", errors.toString(StandardCharsets.UTF_8));
      } finally {
        System.setOut(originalOut);
        System.setErr(originalErr);
        thread.setUncaughtExceptionHandler(originalHandler);
      }
    }
  }

  @Test
  void concurrentInvocations() throws Exception {
    var launcher = new InspectorLauncher();
    try (var pool = Executors.newFixedThreadPool(8)) {
      var work = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 64; i++) {
        UUID id = new UUID(0, 100 + i);
        work.add(
            () -> {
              var env = environment();
              env.put("NK_INSPECTOR_RUN_ID", id.toString());
              var bytes = new ByteArrayOutputStream();
              try (var output = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
                launcher.write(
                    new String[0],
                    env,
                    output,
                    s ->
                        r -> {
                          assertEquals(id, r.id());
                          return result(InspectionExecution.Status.SUCCESS, r);
                        });
              }
              assertEquals("NKINSPECTOR1 0\n", bytes.toString(StandardCharsets.UTF_8));
              return true;
            });
      }
      for (var done : pool.invokeAll(work)) assertTrue(done.get(5, TimeUnit.SECONDS));
    }
  }

  @Test
  void actualJvmEntry() throws Exception {
    for (List<String> args : List.of(List.<String>of(), List.of(FIXTURE_UNTRUSTED_6FC6869D))) {
      var command =
          new ArrayList<>(
              List.of(
                  Path.of(System.getProperty("java.home"), "bin/java").toString(),
                  "-cp",
                  System.getProperty("java.class.path"),
                  InspectorLauncher.class.getName()));
      command.addAll(args);
      var builder = new ProcessBuilder(command);
      builder.environment().clear();
      Path output = Files.createTempFile(root, "stdout-", ".txt");
      Path error = Files.createTempFile(root, "stderr-", ".txt");
      builder.redirectOutput(output.toFile()).redirectError(error.toFile());
      var process = builder.start();
      try {
        assertTrue(process.waitFor(15, TimeUnit.SECONDS));
        assertEquals(0, process.exitValue());
      } finally {
        if (process.isAlive()) process.destroy();
      }
      assertEquals("NKINSPECTOR1 70\n", Files.readString(output));
      assertEquals("", Files.readString(error));
    }
  }

  private static InspectionExecution result(InspectionExecution.Status status, InspectionRun run) {
    return switch (status) {
      case SUCCESS ->
          new InspectionExecution(
              status, Optional.of(new InspectionProgress(run, Optional.empty(), 0, 0, 0, true)));
      case WARNING ->
          new InspectionExecution(
              status,
              Optional.of(
                  new InspectionProgress(run, Optional.of(new UUID(0, 100)), 1, 0, 1, true)));
      default -> new InspectionExecution(status, Optional.empty());
    };
  }
}
