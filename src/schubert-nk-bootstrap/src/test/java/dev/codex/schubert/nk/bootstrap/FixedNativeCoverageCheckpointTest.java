package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** Literal JaCoCo0.8.15 public format/profile oracle; no production-generated expected. */
final class FixedNativeCoverageCheckpointTest {
  private static final String INV = "1234567890abcdef1234567890abcdef";
  private static final byte[] GOLDEN = {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1};

  private static FixedNativeCoverageProfile profile(
      ServiceConfigFiles.Service service, FixedNativeCoverageProfile.Phase phase) {
    String suffix = phase == FixedNativeCoverageProfile.Phase.ROOT ? "root" : "ordinary";
    return FixedNativeCoverageProfile.parse(
            service,
            phase,
            INV,
            List.of(
                "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid="
                    + service.name()
                    + "-"
                    + INV
                    + "-"
                    + suffix))
        .orElseThrow();
  }

  @Test
  void ncheck193001DefaultDoesNotLoadReservedAgentOrOutput() throws Exception {
    for (var service : ServiceConfigFiles.Service.values())
      for (var phase : FixedNativeCoverageProfile.Phase.values())
        assertTrue(FixedNativeCoverageCheckpoint.fromCurrentJvm(service, phase, null).isEmpty());
  }

  @Test
  void ncheck193002FourRolesAndTwoRootPointsHaveIndependentNamesAndNoReset() throws Exception {
    for (var service : ServiceConfigFiles.Service.values())
      for (var phase : FixedNativeCoverageProfile.Phase.values()) {
        var agent =
            new Agent(
                service.name()
                    + "-"
                    + INV
                    + "-"
                    + (phase == FixedNativeCoverageProfile.Phase.ROOT ? "root" : "ordinary"));
        var outputs = new LinkedHashMap<String, byte[]>();
        var checkpoint =
            new FixedNativeCoverageCheckpoint(
                profile(service, phase),
                agent,
                (name, bytes) -> {
                  assertNull(outputs.put(name, bytes.clone()));
                  bytes[0] = 9;
                });
        if (phase == FixedNativeCoverageProfile.Phase.ROOT)
          checkpoint.capture(FixedNativeCoverageCheckpoint.Point.BEFORE_EXEC);
        checkpoint.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL);
        assertEquals(
            phase == FixedNativeCoverageProfile.Phase.ROOT
                ? List.of(INV + ".before-exec.exec", INV + ".terminal.exec")
                : List.of(INV + ".terminal.exec"),
            List.copyOf(outputs.keySet()));
        for (byte[] value : outputs.values()) assertArrayEquals(GOLDEN, value);
        assertArrayEquals(GOLDEN, agent.bytes);
        assertEquals(outputs.size(), agent.dataCalls);
        assertEquals(
            "-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar=output=none,append=false,dumponexit=false,sessionid="
                + service.name()
                + "-"
                + INV
                + "-ordinary",
            checkpoint.ordinaryProfile().argument());
        assertThrows(
            IOException.class,
            () -> checkpoint.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL));
        assertEquals(outputs.size(), agent.dataCalls);
      }
  }

  @Test
  void ncheck193003UnknownVersionSessionNullShortLargeHeaderAndChangedSessionReject()
      throws Exception {
    for (String fault :
        List.of(
            "version",
            "session",
            "changedVersion",
            "changedSession",
            "null",
            "short",
            "large",
            "header0",
            "header1",
            "header2",
            "header3",
            "header4")) {
      var agent = new Agent("API-" + INV + "-root");
      agent.fault = fault;
      if (fault.equals("version")) agent.version = "0.8.15.unknown";
      if (fault.equals("session")) agent.session = "WEB-" + INV + "-root";
      if (fault.equals("null")) agent.bytes = null;
      if (fault.equals("short")) agent.bytes = new byte[4];
      if (fault.equals("large")) agent.bytes = new byte[16 * 1024 * 1024 + 1];
      if (fault.startsWith("header")) agent.bytes[Integer.parseInt(fault.substring(6))] ^= 1;
      AtomicInteger exports = new AtomicInteger();
      var actual =
          new FixedNativeCoverageCheckpoint(
              profile(ServiceConfigFiles.Service.API, FixedNativeCoverageProfile.Phase.ROOT),
              agent,
              (name, bytes) -> exports.incrementAndGet());
      var error =
          assertThrows(
              IOException.class,
              () -> actual.capture(FixedNativeCoverageCheckpoint.Point.BEFORE_EXEC),
              fault);
      assertEquals("fixed PT native capture unavailable", error.getMessage());
      assertNull(error.getCause());
      assertEquals(0, exports.get());
      int before = agent.dataCalls;
      assertThrows(
          IOException.class, () -> actual.capture(FixedNativeCoverageCheckpoint.Point.BEFORE_EXEC));
      assertEquals(before, agent.dataCalls);
    }
  }

  @Test
  void ncheck193004NullAndOrdinaryBeforeExecCannotConsumeOrExport() throws Exception {
    var p = profile(ServiceConfigFiles.Service.API, FixedNativeCoverageProfile.Phase.ORDINARY);
    var agent = new Agent("API-" + INV + "-ordinary");
    FixedNativeCoverageCheckpoint.Export export = (name, bytes) -> assertArrayEquals(GOLDEN, bytes);
    assertThrows(
        IllegalArgumentException.class,
        () -> new FixedNativeCoverageCheckpoint(null, agent, export));
    assertThrows(
        IllegalArgumentException.class, () -> new FixedNativeCoverageCheckpoint(p, null, export));
    assertThrows(
        IllegalArgumentException.class, () -> new FixedNativeCoverageCheckpoint(p, agent, null));
    var actual = new FixedNativeCoverageCheckpoint(p, agent, export);
    assertThrows(IllegalArgumentException.class, () -> actual.capture(null));
    assertThrows(
        IllegalArgumentException.class,
        () -> actual.capture(FixedNativeCoverageCheckpoint.Point.BEFORE_EXEC));
    assertEquals(0, agent.dataCalls);
    actual.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL);
    assertEquals(1, agent.dataCalls);
  }

  @Test
  void ncheck193005KnownOrUnknownExportNeverRetriesOrNormalizes() {
    for (boolean unknown : List.of(false, true)) {
      var known = new IOException("synthetic private IO");
      var original = new IllegalStateException("synthetic unknown export");
      AtomicInteger exports = new AtomicInteger();
      var actual =
          new FixedNativeCoverageCheckpoint(
              profile(ServiceConfigFiles.Service.API, FixedNativeCoverageProfile.Phase.ROOT),
              new Agent("API-" + INV + "-root"),
              (name, bytes) -> {
                exports.incrementAndGet();
                if (unknown) throw original;
                throw known;
              });
      if (unknown)
        assertSame(
            original,
            assertThrows(
                IllegalStateException.class,
                () -> actual.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL)));
      else
        assertSame(
            known,
            assertThrows(
                IOException.class,
                () -> actual.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL)));
      assertThrows(
          IOException.class, () -> actual.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL));
      assertEquals(1, exports.get());
    }
  }

  @Test
  void ncheck193006ConcurrentCaptureHasExactlyOneDataAndExport() throws Exception {
    var agent = new Agent("WEB-" + INV + "-ordinary");
    AtomicInteger exports = new AtomicInteger();
    var actual =
        new FixedNativeCoverageCheckpoint(
            profile(ServiceConfigFiles.Service.WEB, FixedNativeCoverageProfile.Phase.ORDINARY),
            agent,
            (name, bytes) -> exports.incrementAndGet());
    try (var pool = Executors.newFixedThreadPool(4)) {
      var results = new ArrayList<Future<Boolean>>();
      for (int n = 0; n < 32; n++)
        results.add(
            pool.submit(
                () -> {
                  try {
                    actual.capture(FixedNativeCoverageCheckpoint.Point.TERMINAL);
                    return true;
                  } catch (IOException consumed) {
                    assertEquals("fixed PT native capture unavailable", consumed.getMessage());
                    return false;
                  }
                }));
      int winners = 0;
      for (var result : results) if (result.get(5, TimeUnit.SECONDS)) winners++;
      assertEquals(1, winners);
      assertEquals(1, agent.dataCalls);
      assertEquals(1, exports.get());
    }
  }

  private static final class Agent implements FixedNativeCoverageCheckpoint.Agent {
    String version = "0.8.15.202606040825";
    String session;
    String fault = "";
    byte @Nullable [] bytes = GOLDEN.clone();
    int dataCalls;

    Agent(String session) {
      this.session = session;
    }

    @Override
    public String version() {
      return version;
    }

    @Override
    public String session() {
      return session;
    }

    @Override
    public byte @Nullable [] executionDataWithoutReset() {
      dataCalls++;
      if (fault.equals("changedSession")) session = "changed";
      if (fault.equals("changedVersion")) version = "changed";
      return bytes;
    }
  }
}
