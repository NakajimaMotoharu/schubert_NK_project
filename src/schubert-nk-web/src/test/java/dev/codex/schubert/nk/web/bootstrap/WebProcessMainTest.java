package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-WEB-MAIN-001..004. Independent exit/diagnostic oracle; no actual NK success claim. */
final class WebProcessMainTest {
  @TempDir Path root;
  private final WebProcessMain main = new WebProcessMain();
  private static final Map<String, String> ENV =
      Map.of(
          "SCHUBERT_NK_CONFIG_DIR",
          "/etc/schubert-nk",
          "CREDENTIALS_DIRECTORY",
          "/run/credentials/service");
  private static final NonSecretConfigSource SOURCE =
      service -> {
        assertEquals(ServiceConfigFiles.Service.WEB, service);
        return new ServiceConfigFiles.Contents("", "");
      };

  @Test
  void opsWebMain001AdmissionBeforeAssemblyAndUnwiredNativeRefusal() {
    AtomicInteger starts = new AtomicInteger();
    assertEquals(
        0,
        main.run(
            new String[0],
            ENV,
            SOURCE,
            inputs -> {
              assertEquals(Path.of("/run/credentials/service"), inputs.credentials().directory());
              assertEquals("001", inputs.config().value("nk.protocol.version"));
              starts.incrementAndGet();
            }));
    assertEquals(1, starts.get());
    assertEquals(50, main.run(new String[0], ENV, SOURCE));
    NonSecretConfigSource forbidden =
        service -> {
          throw new AssertionError("file IO forbidden");
        };
    assertEquals(70, main.run(new String[] {"override"}, ENV, forbidden));
    assertEquals(
        70,
        main.run(
            new String[] {"override"},
            ENV,
            forbidden,
            inputs -> {
              throw new AssertionError("rejected argv must not execute startup");
            }));
    assertEquals(70, main.run(new String[0], Map.of(), forbidden));
    assertEquals(
        70,
        main.run(
            new String[0], Map.of("CREDENTIALS_DIRECTORY", "/run/credentials/service"), forbidden));
    assertEquals(1, starts.get());
  }

  @Test
  void opsWebMain002FailuresAndUnknownRemainNonSuccess() {
    NonSecretConfigSource broken =
        service -> {
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        };
    assertEquals(50, main.run(new String[0], ENV, broken));
    assertEquals(
        50,
        main.run(
            new String[0],
            ENV,
            SOURCE,
            inputs -> {
              throw new IOException("UNTRUSTED");
            }));
    RuntimeException invalid = new IllegalArgumentException("UNTRUSTED");
    assertSame(
        invalid,
        assertThrows(
            IllegalArgumentException.class,
            () ->
                main.run(
                    new String[0],
                    ENV,
                    SOURCE,
                    inputs -> {
                      throw invalid;
                    })));
    RuntimeException unknown = new IllegalStateException("UNTRUSTED");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                main.run(
                    new String[0],
                    ENV,
                    SOURCE,
                    inputs -> {
                      throw unknown;
                    })));
    Error fatal = new AssertionError("UNTRUSTED");
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                main.run(
                    new String[0],
                    ENV,
                    SOURCE,
                    inputs -> {
                      throw fatal;
                    })));
    assertThrows(NullPointerException.class, () -> main.run(null, ENV, SOURCE));
    assertThrows(NullPointerException.class, () -> main.run(new String[0], null, SOURCE));
    assertThrows(NullPointerException.class, () -> main.run(new String[0], ENV, null));
    assertThrows(NullPointerException.class, () -> main.run(new String[0], ENV, SOURCE, null));
  }

  @Test
  void opsWebMain003FatalDiagnosticIsFixed() throws IOException {
    synchronized (System.class) {
      PrintStream original = System.err;
      Thread thread = Thread.currentThread();
      Thread.UncaughtExceptionHandler originalHandler = thread.getUncaughtExceptionHandler();
      ByteArrayOutputStream bytes = new ByteArrayOutputStream();
      try (PrintStream output = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
        try {
          System.setErr(output);
          var exits = new ArrayList<Integer>();
          new WebProcessMain(ENV, SOURCE, exits::add).main(new String[0]);
          new WebProcessMain(Map.of(), SOURCE, exits::add).main(new String[0]);
          assertEquals(List.of(50, 70), exits);
          assertThrows(
              NullPointerException.class, () -> new WebProcessMain(null, SOURCE, exits::add));
          assertThrows(NullPointerException.class, () -> new WebProcessMain(ENV, null, exits::add));
          assertThrows(NullPointerException.class, () -> new WebProcessMain(ENV, SOURCE, null));
          WebProcessMain.fatal(Thread.currentThread(), new IllegalStateException("UNTRUSTED"));
        } finally {
          System.setErr(original);
          thread.setUncaughtExceptionHandler(originalHandler);
        }
      }
      assertEquals(
          "WEB process stopped\nWEB process stopped\nWEB process failed\n",
          bytes.toString(StandardCharsets.UTF_8));
    }
  }

  @Test
  void opsWebMain004ActualExternalMainRejectsMissingConfigAndArgv() throws Exception {
    for (List<String> arguments : List.of(List.<String>of(), List.of("override"))) {
      var command = new ArrayList<String>();
      command.add(Path.of(System.getProperty("java.home"), "bin/java").toString());
      // Preserve the existing coverage agent only; never pass credential/config JVM overrides.
      ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
          .filter(arg -> arg.startsWith("-javaagent:") && arg.contains("jacoco"))
          .forEach(command::add);
      command.add("--enable-native-access=ALL-UNNAMED");
      command.addAll(
          List.of("-cp", System.getProperty("java.class.path"), WebProcessMain.class.getName()));
      command.addAll(arguments);
      var builder = new ProcessBuilder(command);
      builder.environment().clear();
      Path stdout = Files.createTempFile(root, "stdout-", ".txt");
      Path stderr = Files.createTempFile(root, "stderr-", ".txt");
      builder.redirectOutput(stdout.toFile()).redirectError(stderr.toFile());
      Process process = builder.start();
      try {
        assertTrue(process.waitFor(15, TimeUnit.SECONDS));
        assertEquals(70, process.exitValue());
      } finally {
        if (process.isAlive()) {
          process.destroy();
          assertTrue(process.waitFor(5, TimeUnit.SECONDS));
        }
      }
      assertEquals("", Files.readString(stdout));
      assertEquals("WEB process stopped\n", Files.readString(stderr));
    }
  }
}
