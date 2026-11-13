package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** SS341/342/SSC101 independent fixed-policy oracle; does not issue stop. */
final class MaintenanceUnitStopPolicyTest {
  private static final List<String> NAMES =
      List.of(
          "caddy.service",
          "schubert-nk-web.service",
          "schubert-nk-api.service",
          "schubert-nk-cleanup.service",
          "schubert-nk-inbox-inspector.service",
          "schubert-nk-expiry-cleanup.service",
          "schubert-nk-backup.service",
          "artemis.service");

  private enum NativePoint {
    START,
    WAIT
  }

  /** MPOL008/BUG2782: declared query faults never become ordinary sanitized success/failure. */
  @Test
  void mpol008NativePortFatalGraphsPreserveIdentityAndEveryOwnedPostcondition() {
    for (var point : NativePoint.values()) {
      for (int graph = 0; graph < 3; graph++) {
        var marker = new AssertionError("public fatal query marker");
        var failure = new StopGateException(StopGateFailure.TIMEOUT);
        switch (graph) {
          case 0 -> failure.initCause(marker);
          case 1 -> failure.addSuppressed(marker);
          default -> {
            var cycle = new IllegalStateException("public cyclic query fault");
            failure.initCause(cycle);
            cycle.initCause(failure);
            cycle.addSuppressed(marker);
          }
        }
        var child = new InspectorUnitProbeFixture.Child(policy("caddy.service"));
        child.hook =
            (name, count) -> {
              if (point == NativePoint.WAIT && name.equals("wait")) throw failure;
            };
        var starts = new AtomicInteger();
        var reader =
            new InspectorUnitProbe.NativeReader(
                command -> {
                  assertEquals(
                      List.of(
                          "/usr/bin/systemctl",
                          "--system",
                          "--no-pager",
                          "--no-ask-password",
                          "show",
                          "--property=Id,LoadState,KillMode,SendSIGKILL",
                          "caddy.service"),
                      command);
                  starts.incrementAndGet();
                  if (point == NativePoint.START) throw failure;
                  return child;
                });
        assertSame(
            marker,
            assertThrows(
                AssertionError.class,
                () ->
                    new MaintenanceUnitStopPolicy(
                            new MaintenanceUnitStopPolicy.NativeSource(reader))
                        .requireSafe(MaintenanceUnit.CADDY)));
        assertEquals(1, starts.get());
        assertEquals(0, marker.getSuppressed().length);
        if (point == NativePoint.START) {
          assertEquals(List.of(), child.order);
          assertEquals(0, child.destroyed);
          assertEquals(0, child.output.closed);
          assertEquals(0, child.input.closed);
          assertEquals(0, child.error.closed);
        } else {
          child.allClosed();
          child.wiped();
          assertEquals(1, child.destroyed);
          assertEquals(
              List.of(
                  "get.stdout",
                  "get.stdin",
                  "get.stderr",
                  "stdin.close",
                  "stderr.close",
                  "wait",
                  "stdout.close",
                  "alive",
                  "destroy"),
              child.order);
        }
      }
    }
  }

  private static byte[] policy(String name) {
    return ("Id=" + name + "\nLoadState=loaded\nKillMode=control-group\nSendSIGKILL=no\n")
        .getBytes(StandardCharsets.US_ASCII);
  }

  private static StopGateException rejected(MaintenanceUnit unit, byte[] value) {
    var failure =
        assertThrows(
            StopGateException.class,
            () -> new MaintenanceUnitStopPolicy(fixed -> value).requireSafe(unit));
    assertEquals(StopGateFailure.MALFORMED_STATE, failure.reason());
    assertArrayEquals(new byte[value.length], value);
    return failure;
  }

  @Test
  void mpol001AllEightFixedPolicyAndOrderIndependent() {
    assertEquals(NAMES.size(), MaintenanceUnit.values().length);
    for (int i = 0; i < NAMES.size(); i++) {
      var unit = MaintenanceUnit.values()[i];
      assertEquals(NAMES.get(i), unit.serviceName());
      byte[] bytes = policy(NAMES.get(i));
      new MaintenanceUnitStopPolicy(
              fixed -> {
                assertSame(unit, fixed);
                return bytes;
              })
          .requireSafe(unit);
      assertArrayEquals(new byte[bytes.length], bytes);
      byte[] reordered =
          ("SendSIGKILL=no\nKillMode=control-group\nLoadState=loaded\nId=" + NAMES.get(i) + "\n")
              .getBytes(StandardCharsets.US_ASCII);
      new MaintenanceUnitStopPolicy(fixed -> reordered).requireSafe(unit);
      assertArrayEquals(new byte[reordered.length], reordered);
    }
  }

  @Test
  void mpol002MissingDuplicateUnknownAndLineStructure() {
    String good = new String(policy(NAMES.get(0)), StandardCharsets.US_ASCII);
    for (String bad :
        List.of(
            good.replace("LoadState=loaded\n", ""),
            good.replace("LoadState=loaded", "Id=loaded"),
            good.replace("LoadState", "Unknown"),
            good.replace("Id=", "=Id="),
            good.replace("KillMode=", "KillMode=="),
            good.substring(0, good.length() - 1),
            good + "x",
            good + "\n",
            good + "Extra=no\n")) {
      rejected(MaintenanceUnit.CADDY, bad.getBytes(StandardCharsets.US_ASCII));
    }
  }

  @Test
  void mpol003ByteAndNullBounds() {
    rejected(MaintenanceUnit.CADDY, new byte[0]);
    rejected(MaintenanceUnit.CADDY, new byte[512]);
    rejected(MaintenanceUnit.CADDY, new byte[513]);
    byte[] good = policy(NAMES.get(0));
    for (int position = 0; position < good.length; position++) {
      for (byte bad : new byte[] {0, 13, 31, 127, (byte) 0x80}) {
        byte[] mutated = good.clone();
        mutated[position] = bad;
        rejected(MaintenanceUnit.CADDY, mutated);
      }
    }
    assertThrows(NullPointerException.class, () -> new MaintenanceUnitStopPolicy(null));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitStopPolicy(fixed -> good).requireSafe(null));
    assertThrows(
        NullPointerException.class,
        () -> new MaintenanceUnitStopPolicy(fixed -> null).requireSafe(MaintenanceUnit.CADDY));
    assertThrows(
        NullPointerException.class, () -> new MaintenanceUnitStopPolicy.NativeSource(null));
  }

  @Test
  void mpol004WrongIdLoadKillAndAutomaticSigkillRefused() {
    String good = new String(policy(NAMES.get(0)), StandardCharsets.US_ASCII);
    for (String bad :
        List.of(
            good.replace("Id=caddy.service", "Id=schubert-nk-web.service"),
            good.replace("LoadState=loaded", "LoadState=not-found"),
            good.replace("LoadState=loaded", "LoadState=masked"),
            good.replace("KillMode=control-group", "KillMode=process"),
            good.replace("KillMode=control-group", "KillMode=mixed"),
            good.replace("SendSIGKILL=no", "SendSIGKILL=yes"),
            good.replace("SendSIGKILL=no", "SendSIGKILL="))) {
      rejected(MaintenanceUnit.CADDY, bad.getBytes(StandardCharsets.US_ASCII));
    }
  }

  @Test
  void mpol005FixedNativeQueryAndAllProcessOwners() {
    for (int i = 0; i < NAMES.size(); i++) {
      var unit = MaintenanceUnit.values()[i];
      var child = new InspectorUnitProbeFixture.Child(policy(NAMES.get(i)));
      var reader =
          new InspectorUnitProbe.NativeReader(
              command -> {
                assertEquals(
                    List.of(
                        "/usr/bin/systemctl",
                        "--system",
                        "--no-pager",
                        "--no-ask-password",
                        "show",
                        "--property=Id,LoadState,KillMode,SendSIGKILL",
                        NAMES.get(unit.ordinal())),
                    command);
                return child;
              });
      new MaintenanceUnitStopPolicy(new MaintenanceUnitStopPolicy.NativeSource(reader))
          .requireSafe(unit);
      child.allClosed();
      child.wiped();
    }
  }

  @Test
  void mpol006KnownUnknownNullAndInterrupts() {
    byte[] afterRead = policy(NAMES.get(0));
    try {
      Thread.currentThread().interrupt();
      int[] calls = {0};
      var failure =
          assertThrows(
              StopGateException.class,
              () ->
                  new MaintenanceUnitStopPolicy(
                          fixed -> {
                            calls[0]++;
                            return afterRead;
                          })
                      .requireSafe(MaintenanceUnit.CADDY));
      assertEquals(StopGateFailure.INTERRUPTED, failure.reason());
      assertEquals(0, calls[0]);
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
    try {
      var failure =
          assertThrows(
              StopGateException.class,
              () ->
                  new MaintenanceUnitStopPolicy(
                          fixed -> {
                            Thread.currentThread().interrupt();
                            return afterRead;
                          })
                      .requireSafe(MaintenanceUnit.CADDY));
      assertEquals(StopGateFailure.INTERRUPTED, failure.reason());
      assertTrue(Thread.currentThread().isInterrupted());
      assertArrayEquals(new byte[afterRead.length], afterRead);
    } finally {
      Thread.interrupted();
    }
    var known = new StopGateException(StopGateFailure.COMMAND_FAILURE);
    assertSame(
        known,
        assertThrows(
            StopGateException.class,
            () ->
                new MaintenanceUnitStopPolicy(
                        fixed -> {
                          throw known;
                        })
                    .requireSafe(MaintenanceUnit.CADDY)));
    var unknown = new IllegalStateException("public unknown");
    assertSame(
        unknown,
        assertThrows(
            IllegalStateException.class,
            () ->
                new MaintenanceUnitStopPolicy(
                        fixed -> {
                          throw unknown;
                        })
                    .requireSafe(MaintenanceUnit.CADDY)));
  }

  @Test
  void mpol007IndependentParallelAndNoStopAuthority() throws Exception {
    assertNotNull(MaintenanceUnitStopPolicy.create());
    var pool = Executors.newFixedThreadPool(8);
    try {
      var tasks = new ArrayList<Callable<Boolean>>();
      for (int i = 0; i < 64; i++) {
        final int index = i % NAMES.size();
        tasks.add(
            () -> {
              byte[] input = policy(NAMES.get(index));
              new MaintenanceUnitStopPolicy(fixed -> input)
                  .requireSafe(MaintenanceUnit.values()[index]);
              return Arrays.equals(input, new byte[input.length]);
            });
      }
      for (var result : pool.invokeAll(tasks, 5, TimeUnit.SECONDS))
        assertTrue(result.get(5, TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(5, TimeUnit.SECONDS));
    }
    // This reader only requests systemctl show. No fixed policy vector can dispatch stop.
    assertEquals("Id,LoadState,KillMode,SendSIGKILL", MaintenanceUnitStopPolicy.PROPERTIES);
  }
}
