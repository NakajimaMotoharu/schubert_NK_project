package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;

/** Literal JaCoCo0.8.15 public format/profile oracle; no production-generated expected. */
final class FixedNativeCoverageCheckpointTest {
  private static final String INV = "1234567890abcdef1234567890abcdef";
  private static final byte[] GOLDEN = {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1};

  public static final class PublicFixture {
    boolean reset = true;
    int reads;

    public String getVersion() {
      return "0.8.15";
    }

    public String getSessionId() {
      return "API-1234567890abcdef1234567890abcdef-root";
    }

    public byte[] getExecutionData(boolean value) {
      reset = value;
      reads++;
      return new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1};
    }
  }

  public static final class PublicRtFixture {
    public static Object getAgent() {
      return new PublicFixture();
    }
  }

  public static final class MetadataFixture {}

  @Test
  void common922001CurrentJvmFactoryRejectsMissingRoleWithoutCreatingAgentAuthority()
      throws Exception {
    var before = java.lang.management.ManagementFactory.getRuntimeMXBean().getInputArguments();
    assertTrue(
        before.stream()
            .noneMatch(option -> option.startsWith("-javaagent:/opt/pgpt-tools-pg390/")));
    agentRefused(
        () ->
            FixedNativeCoverageCheckpoint.fromCurrentJvm(
                null, FixedNativeCoverageProfile.Phase.ORDINARY, null));
    agentRefused(
        () ->
            FixedNativeCoverageCheckpoint.fromCurrentJvm(
                ServiceConfigFiles.Service.API, null, null));
    assertEquals(
        Optional.empty(),
        FixedNativeCoverageCheckpoint.fromCurrentJvm(
            ServiceConfigFiles.Service.API, FixedNativeCoverageProfile.Phase.ORDINARY, null));
    assertEquals(
        before, java.lang.management.ManagementFactory.getRuntimeMXBean().getInputArguments());
  }

  @Test
  void ncheck597005TerminalFactoryWithNoReservedAgentDoesNotCreateNativeAuthority()
      throws Exception {
    assertTrue(
        java.lang.management.ManagementFactory.getRuntimeMXBean().getInputArguments().stream()
            .noneMatch(option -> option.startsWith("-javaagent:/opt/pgpt-tools-pg390/")));
    for (var role : FixedNativeCoverageProfile.TerminalRole.values()) {
      assertEquals(
          Optional.empty(), FixedNativeCoverageCheckpoint.fromCurrentTerminalJvm(role, null));
    }
    agentRefused(() -> FixedNativeCoverageCheckpoint.fromCurrentTerminalJvm(null, null));
  }

  private static FixedNativeCoverageCheckpoint.PublicAgent.Classes fixtureClasses() {
    return name -> {
      assertTrue(Set.of("org.jacoco.agent.rt.RT", "org.jacoco.agent.rt.IAgent").contains(name));
      return name.endsWith(".RT") ? PublicRtFixture.class : PublicFixture.class;
    };
  }

  private static void agentRefused(org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(IOException.class, operation);
    assertEquals("fixed PT native capture unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void ncheck597001RealPublicReflectionReadsLiteralDataWithoutReset() throws Exception {
    var fixture = new PublicFixture();
    var sources = new ArrayList<Class<?>>();
    var invoked = new ArrayList<String>();
    var agent =
        new FixedNativeCoverageCheckpoint.PublicAgent(
            fixtureClasses(),
            sources::add,
            (method, target, arguments) -> {
              invoked.add(method.getName());
              if (method.getName().equals("getAgent")) {
                assertNull(target);
                assertEquals(0, arguments.length);
                return fixture;
              }
              assertSame(fixture, target);
              return method.invoke(target, arguments);
            });
    assertEquals("0.8.15", agent.version());
    assertEquals("API-1234567890abcdef1234567890abcdef-root", agent.session());
    assertArrayEquals(
        new byte[] {1, (byte) 0xc0, (byte) 0xc0, 0x10, 7, 0x10, 1},
        agent.executionDataWithoutReset());
    assertFalse(fixture.reset);
    assertEquals(1, fixture.reads);
    assertEquals(List.of(PublicRtFixture.class, PublicFixture.class), sources);
    assertEquals(List.of("getAgent", "getVersion", "getSessionId", "getExecutionData"), invoked);
  }

  @Test
  void ncheck597002ConstructorMissingNullTypeAndProviderFailuresNeverExposeRawCause() {
    FixedNativeCoverageCheckpoint.PublicAgent.Invocation reflection = (m, t, a) -> m.invoke(t, a);
    assertThrows(
        IllegalArgumentException.class,
        () -> new FixedNativeCoverageCheckpoint.PublicAgent(null, c -> {}, reflection));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FixedNativeCoverageCheckpoint.PublicAgent(fixtureClasses(), null, reflection));
    assertThrows(
        IllegalArgumentException.class,
        () -> new FixedNativeCoverageCheckpoint.PublicAgent(fixtureClasses(), c -> {}, null));
    for (String missing : List.of("org.jacoco.agent.rt.RT", "org.jacoco.agent.rt.IAgent")) {
      agentRefused(
          () ->
              new FixedNativeCoverageCheckpoint.PublicAgent(
                  name -> name.equals(missing) ? null : fixtureClasses().load(name),
                  c -> {},
                  reflection));
    }
    agentRefused(
        () ->
            new FixedNativeCoverageCheckpoint.PublicAgent(
                name -> {
                  throw new ClassNotFoundException("PRIVATE_CLASS");
                },
                c -> {},
                reflection));
    agentRefused(
        () ->
            new FixedNativeCoverageCheckpoint.PublicAgent(
                name -> PublicFixture.class, c -> {}, reflection));
    agentRefused(
        () ->
            new FixedNativeCoverageCheckpoint.PublicAgent(
                fixtureClasses(),
                c -> {
                  throw new IOException("PRIVATE_SOURCE");
                },
                reflection));
    agentRefused(
        () ->
            new FixedNativeCoverageCheckpoint.PublicAgent(
                fixtureClasses(),
                c -> {
                  throw new java.net.URISyntaxException("PRIVATE", "PRIVATE_URI");
                },
                reflection));
    for (Object invalid : Arrays.asList(null, "PRIVATE_AGENT")) {
      agentRefused(
          () ->
              new FixedNativeCoverageCheckpoint.PublicAgent(
                  fixtureClasses(), c -> {}, (m, t, a) -> invalid));
    }
    agentRefused(
        () ->
            new FixedNativeCoverageCheckpoint.PublicAgent(
                fixtureClasses(),
                c -> {},
                (m, t, a) -> {
                  throw new java.lang.reflect.InvocationTargetException(
                      new IllegalStateException("PRIVATE_AGENT"));
                }));
    agentRefused(
        () ->
            new FixedNativeCoverageCheckpoint.PublicAgent(
                name -> name.endsWith(".RT") ? PublicRtFixture.class : MetadataFixture.class,
                c -> {},
                (m, t, a) -> new MetadataFixture()));
    // Actual host agent/classpath is not the fixed native CodeSource; never claims native success.
    agentRefused(FixedNativeCoverageCheckpoint.PublicAgent::new);
  }

  @Test
  void ncheck597003NullWrongTypesAndReflectionFailuresAtEveryPublicGetterAreFixed()
      throws Exception {
    for (String method : List.of("getVersion", "getSessionId", "getExecutionData")) {
      for (int mode = 0; mode < 3; mode++) {
        int fault = mode;
        var agent =
            new FixedNativeCoverageCheckpoint.PublicAgent(
                fixtureClasses(),
                c -> {},
                (m, t, a) -> {
                  if (m.getName().equals(method)) {
                    if (fault == 0) return null;
                    if (fault == 1) return Integer.valueOf(7);
                    throw new IllegalAccessException("PRIVATE_INVOCATION");
                  }
                  return m.invoke(t, a);
                });
        agentRefused(
            () -> {
              if (method.equals("getVersion")) agent.version();
              else if (method.equals("getSessionId")) agent.session();
              else agent.executionDataWithoutReset();
            });
      }
    }
  }

  private static Class<?> metadataClass(java.security.@Nullable CodeSource source)
      throws Exception {
    String resource = "FixedNativeCoverageCheckpointTest$MetadataFixture.class";
    byte[] bytes;
    try (var input = FixedNativeCoverageCheckpointTest.class.getResourceAsStream(resource)) {
      assertNotNull(input);
      bytes = input.readAllBytes();
    }
    class Loader extends ClassLoader {
      Loader() {
        super(null);
      }

      Class<?> define() {
        return defineClass(
            MetadataFixture.class.getName(),
            bytes,
            0,
            bytes.length,
            new java.security.ProtectionDomain(source, null));
      }
    }
    return new Loader().define();
  }

  @Test
  void ncheck597004CodeSourceMetadataNullLocationForeignAndFixedPathAreSeparate() throws Exception {
    agentRefused(() -> FixedNativeCoverageCheckpoint.PublicAgent.requirePinnedSource(Object.class));
    agentRefused(
        () -> FixedNativeCoverageCheckpoint.PublicAgent.requirePinnedSource(metadataClass(null)));
    agentRefused(
        () ->
            FixedNativeCoverageCheckpoint.PublicAgent.requirePinnedSource(
                metadataClass(
                    new java.security.CodeSource(null, (java.security.cert.Certificate[]) null))));
    agentRefused(
        () ->
            FixedNativeCoverageCheckpoint.PublicAgent.requirePinnedSource(
                metadataClass(
                    new java.security.CodeSource(
                        java.nio.file.Path.of("/PUBLIC_WRONG/agent.jar").toUri().toURL(),
                        (java.security.cert.Certificate[]) null))));
    FixedNativeCoverageCheckpoint.PublicAgent.requirePinnedSource(
        metadataClass(
            new java.security.CodeSource(
                java.nio.file.Path.of("/opt/pgpt-tools-pg390/jacoco-agent.jar").toUri().toURL(),
                (java.security.cert.Certificate[]) null)));
    // Metadata-only path check is not hash/owner/real-Unit/authority acceptance.
  }

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
