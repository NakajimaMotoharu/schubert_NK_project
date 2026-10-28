package dev.codex.schubert.nk.api.bootstrap;

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

/** PT-OPS-API-MAIN-001..005. Independent exit/diagnostic oracle; no actual NK success claim. */
final class ApiProcessMainTest {
  private static final String FIXTURE_UNTRUSTED_6FC6869D = "UNTRUSTED";
  @TempDir Path root;
  private final ApiProcessMain main = new ApiProcessMain();
  private static final Map<String, String> ENV =
      Map.of(
          "SCHUBERT_NK_CONFIG_DIR",
          "/etc/schubert-nk",
          "CREDENTIALS_DIRECTORY",
          "/run/credentials/service");
  private static final NonSecretConfigSource SOURCE =
      service -> {
        assertEquals(ServiceConfigFiles.Service.API, service);
        return new ServiceConfigFiles.Contents("", "");
      };

  @Test
  void opsApiMain001AdmissionBeforeAssemblyAndUnwiredNativeRefusal() {
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
    // PT-OPS-API-OWN004: four-argument public component admission rejects argv before IO.
    assertEquals(
        70,
        main.run(
            new String[] {"override"},
            ENV,
            forbidden,
            inputs -> {
              throw new AssertionError("assembly after rejected argv");
            }));
    assertEquals(70, main.run(new String[0], Map.of(), forbidden));
    assertEquals(
        70,
        main.run(
            new String[0], Map.of("CREDENTIALS_DIRECTORY", "/run/credentials/service"), forbidden));
    assertEquals(1, starts.get());
  }

  @Test
  void opsApiMain002FailuresAndUnknownRemainNonSuccess() {
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
              throw new IOException(FIXTURE_UNTRUSTED_6FC6869D);
            }));
    RuntimeException invalid = new IllegalArgumentException(FIXTURE_UNTRUSTED_6FC6869D);
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
    RuntimeException unknown = new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D);
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
    Error fatal = new AssertionError(FIXTURE_UNTRUSTED_6FC6869D);
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
  void opsApiMain005ConfigurationLoadFailuresNeverEnterAssembly() {
    var calls = new AtomicInteger();
    NonSecretConfigSource invalid =
        service -> {
          assertEquals(ServiceConfigFiles.Service.API, service);
          return new ServiceConfigFiles.Contents("", "\"nk.protocol.version\": \"INVALID\"\n");
        };
    NonSecretConfigSource unavailable =
        service -> {
          assertEquals(ServiceConfigFiles.Service.API, service);
          throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
        };
    assertEquals(70, main.run(new String[0], ENV, invalid, inputs -> calls.incrementAndGet()));
    assertEquals(
        0, calls.get(), "invalid non-secret configuration cannot acquire runtime resources");
    assertEquals(50, main.run(new String[0], ENV, unavailable, inputs -> calls.incrementAndGet()));
    assertEquals(
        0, calls.get(), "configuration IO failure cannot enter assembly or report success");
  }

  @Test
  void opsApiMain003FatalDiagnosticIsFixed() throws IOException {
    synchronized (System.class) {
      PrintStream original = System.err;
      Thread thread = Thread.currentThread();
      Thread.UncaughtExceptionHandler originalHandler = thread.getUncaughtExceptionHandler();
      ByteArrayOutputStream bytes = new ByteArrayOutputStream();
      try (PrintStream output = new PrintStream(bytes, false, StandardCharsets.UTF_8)) {
        try {
          System.setErr(output);
          var exits = new ArrayList<Integer>();
          new ApiProcessMain(ENV, SOURCE, exits::add).main(new String[0]);
          new ApiProcessMain(Map.of(), SOURCE, exits::add).main(new String[0]);
          assertEquals(List.of(50, 70), exits);
          assertThrows(
              NullPointerException.class, () -> new ApiProcessMain(null, SOURCE, exits::add));
          assertThrows(NullPointerException.class, () -> new ApiProcessMain(ENV, null, exits::add));
          assertThrows(NullPointerException.class, () -> new ApiProcessMain(ENV, SOURCE, null));
          ApiProcessMain.fatal(
              Thread.currentThread(), new IllegalStateException(FIXTURE_UNTRUSTED_6FC6869D));
        } finally {
          System.setErr(original);
          thread.setUncaughtExceptionHandler(originalHandler);
        }
      }
      assertEquals(
          "API startup entered ADMISSION\n"
              + "API process stopped\n"
              + "API process stopped\n"
              + "API process failed\n",
          bytes.toString(StandardCharsets.UTF_8));
    }
  }

  @Test
  void opsApiMain004ActualExternalMainRejectsMissingConfigAndArgv() throws Exception {
    for (List<String> arguments : List.of(List.<String>of(), List.of("override"))) {
      var command = new ArrayList<String>();
      command.add(Path.of(System.getProperty("java.home"), "bin/java").toString());
      // Preserve the existing coverage agent only; never pass credential/config JVM overrides.
      ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
          .filter(arg -> arg.startsWith("-javaagent:") && arg.contains("jacoco"))
          .forEach(command::add);
      command.add("--enable-native-access=ALL-UNNAMED");
      command.addAll(
          List.of("-cp", System.getProperty("java.class.path"), ApiProcessMain.class.getName()));
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
      assertEquals("API process stopped\n", Files.readString(stderr));
    }
  }
}
