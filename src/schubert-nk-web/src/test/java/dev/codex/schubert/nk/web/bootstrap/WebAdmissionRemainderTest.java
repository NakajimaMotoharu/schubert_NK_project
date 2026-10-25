package dev.codex.schubert.nk.web.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.NonSecretConfigSource;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.Security;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS343 independent fixed defaults and real isolated UNKNOWN; PG-D378/WEB-REM004..006. */
final class WebAdmissionRemainderTest {
  @TempDir Path temporary;
  private static final Map<String, String> ENV =
      Map.of(
          "SCHUBERT_NK_CONFIG_DIR",
          "/etc/schubert-nk",
          "CREDENTIALS_DIRECTORY",
          "/run/credentials/service");
  private static final NonSecretConfigSource DEFAULTS =
      service -> new ServiceConfigFiles.Contents("", "");
  // SS343 golden, independent of production DEFAULTS/canonical hash implementation.
  private static final String GOLDEN =
      """
      nk.db.connect-timeout=3s
      nk.db.pool.web.max=2
      nk.db.pool.web.min=1
      nk.db.url=jdbc:postgresql://127.0.0.1:5432/schubert_nk
      nk.monitoring.mode=STANDARD
      nk.mq.url=tcp://127.0.0.1:61616
      nk.protocol.version=001
      nk.time.display-zone=Asia/Tokyo
      nk.web.http.address=127.0.0.1
      nk.web.http.port=8080
      nk.web.management.port=8081
      nk.web.media.max-range-bytes=1048576
      nk.web.media.max-streams=20
      nk.web.mq.reply-timeout=2s
      nk.web.mq.wait.initial=12
      nk.web.mq.wait.max=20
      nk.web.session.idle-timeout=8h
      nk.web.session.max-per-user=2
      nk.web.storage.asset-root=/srv/schubert-nk/data/assets
      nk.web.storage.transfer-root=/srv/schubert-nk/data/transfer
      """;

  @Test
  void rem006AdmissionSuccessAndConfigOrReadFailureUseLiteralCodesWithoutStartup()
      throws Exception {
    int[] code = {50};
    var result = WebProcessMain.admittedConfiguration(new WebStartupInputs(DEFAULTS, ENV), code);
    String expected =
        HexFormat.of()
            .formatHex(
                MessageDigest.getInstance("SHA-256")
                    .digest(GOLDEN.getBytes(StandardCharsets.UTF_8)));
    assertEquals(expected, result.sha256());
    assertEquals(50, code[0]);
    for (String line : GOLDEN.split("\n")) {
      int split = line.indexOf('=');
      assertEquals(
          line.substring(split + 1), result.value().config().value(line.substring(0, split)));
    }
    NonSecretConfigSource invalid =
        service -> new ServiceConfigFiles.Contents("", "nk.web.unknown: invalid\n");
    assertEquals(
        "non-secret configuration unavailable",
        assertThrows(
                IOException.class,
                () ->
                    WebProcessMain.admittedConfiguration(new WebStartupInputs(invalid, ENV), code))
            .getMessage());
    assertEquals(70, code[0]);
    var failed = new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    NonSecretConfigSource broken =
        service -> {
          throw failed;
        };
    code[0] = 50;
    assertSame(
        failed,
        assertThrows(
            StorageIoException.class,
            () -> WebProcessMain.admittedConfiguration(new WebStartupInputs(broken, ENV), code)));
    assertEquals(50, code[0]);
    var callbacks = new AtomicInteger();
    WebProcessMain.Startup never = inputs -> callbacks.incrementAndGet();
    var main = new WebProcessMain();
    assertEquals(70, main.run(new String[0], ENV, invalid, never));
    assertEquals(50, main.run(new String[0], ENV, broken, never));
    assertEquals(0, callbacks.get());
  }

  @Test
  void rem006UnavailableHashProviderIsNotAConfigurationSuccess() throws Exception {
    isolated("hash", "HASH_UNAVAILABLE code70=true callback0=true\n", "");
  }

  @Test
  void rem004EveryUnconfirmedCloseRetainsTheActualBorrowedFrameAfterInterrupt() throws Exception {
    isolated(
        "unknown",
        "EXECUTION_UNKNOWN owners3=true interrupted=true outerClosed0=true\n",
        "WEB cleanup unconfirmed\nWEB cleanup unconfirmed\nWEB cleanup unconfirmed\n");
  }

  private void isolated(String mode, String expectedOut, String expectedErr) throws Exception {
    var command = new ArrayList<String>();
    command.add(Path.of(System.getProperty("java.home"), "bin/java").toString());
    ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
        .filter(s -> s.startsWith("-javaagent:") && s.contains("jacoco"))
        .forEach(command::add);
    command.addAll(
        List.of("-cp", System.getProperty("java.class.path"), Probe.class.getName(), mode));
    Path out = Files.createTempFile(temporary, "probe-", ".out");
    Path err = Files.createTempFile(temporary, "probe-", ".err");
    var builder =
        new ProcessBuilder(command).redirectOutput(out.toFile()).redirectError(err.toFile());
    builder.environment().clear();
    Process child = builder.start();
    try {
      assertTrue(child.waitFor(15, TimeUnit.SECONDS));
      assertEquals(0, child.exitValue());
      assertEquals(expectedOut, Files.readString(out));
      assertEquals(expectedErr, Files.readString(err));
    } finally {
      if (child.isAlive()) {
        child.destroyForcibly();
        assertTrue(child.waitFor(5, TimeUnit.SECONDS));
      }
    }
  }

  /** Test JVM has no native providers/credentials; exit does not normalize any real UNKNOWN. */
  public static final class Probe {
    private Probe() {}

    public static void main(String[] args) throws Exception {
      if (args[0].equals("hash")) {
        for (var provider : Security.getProviders())
          if (provider.getServices().stream()
              .anyMatch(
                  s ->
                      s.getType().equals("MessageDigest")
                          && s.getAlgorithm().equalsIgnoreCase("SHA-256")))
            Security.removeProvider(provider.getName());
        int[] code = {50};
        try {
          WebProcessMain.admittedConfiguration(new WebStartupInputs(DEFAULTS, ENV), code);
          throw new AssertionError("missing hash accepted");
        } catch (IOException rejected) {
          if (code[0] != 70
              || !"non-secret configuration unavailable".equals(rejected.getMessage())
              || rejected.getCause() != null
              || rejected.getSuppressed().length != 0)
            throw new AssertionError("hash failure differs");
        }
        System.out.println("HASH_UNAVAILABLE code70=true callback0=true");
        return;
      }
      var closed = new AtomicInteger();
      var stops = new AtomicInteger();
      List<Thread> owners = new ArrayList<>();
      for (Throwable fault :
          List.of(
              new IOException("synthetic private"),
              new IllegalStateException("synthetic private"),
              new AssertionError("synthetic private"))) {
        owners.add(
            Thread.ofPlatform()
                .daemon(true)
                .start(
                    () -> {
                      try {
                        WebRuntimeExecution.execute(
                            () -> {},
                            () -> {},
                            stops::incrementAndGet,
                            () -> {
                              if (fault instanceof IOException io) throw io;
                              if (fault instanceof RuntimeException runtime) throw runtime;
                              throw (Error) fault;
                            });
                      } catch (IOException escaped) {
                        throw new AssertionError("UNKNOWN returned", escaped);
                      } finally {
                        closed.incrementAndGet();
                      }
                    }));
      }
      retained(owners, closed);
      Thread.sleep(1200);
      retained(owners, closed);
      for (var owner : owners) owner.interrupt();
      long until = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
      while (owners.stream().anyMatch(Thread::isInterrupted) && System.nanoTime() < until)
        Thread.sleep(1);
      if (owners.stream().anyMatch(Thread::isInterrupted))
        throw new AssertionError("interrupt not consumed");
      Thread.sleep(1200);
      retained(owners, closed);
      if (stops.get() != 3) throw new AssertionError("stop not once per owner");
      System.out.println("EXECUTION_UNKNOWN owners3=true interrupted=true outerClosed0=true");
    }

    private static void retained(List<Thread> owners, AtomicInteger closed) throws Exception {
      long until = System.nanoTime() + TimeUnit.SECONDS.toNanos(3);
      while (System.nanoTime() < until) {
        if (closed.get() != 0 || owners.stream().anyMatch(t -> !t.isAlive()))
          throw new AssertionError("borrowed scope unwound");
        if (owners.stream()
            .allMatch(
                t ->
                    t.getState() == Thread.State.TIMED_WAITING
                        && Arrays.stream(t.getStackTrace())
                            .anyMatch(
                                f ->
                                    f.getClassName().equals(WebRuntimeExecution.class.getName())
                                        && f.getMethodName().equals("execute")))) return;
        Thread.sleep(1);
      }
      throw new AssertionError("owner not retained");
    }
  }
}
