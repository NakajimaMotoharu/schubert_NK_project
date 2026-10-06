package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.lang.reflect.Method;
import java.nio.file.Path;
import java.util.EnumSet;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * SSC193 isolated-PT only public agent export. Not a readiness, normal termination or source/run
 * qualification authority. Root caller retains original owner/budget across before-exec capture;
 * ordinary caller invokes terminal only after every owned application scope actually returns.
 * NK-OPS-001 / SYS002004,OPS009,TST004 / UI212251 / SS342343451 / PT-OPS-NCHECK193001..006.
 */
@NullMarked
public final class FixedNativeCoverageCheckpoint {
  public enum Point {
    BEFORE_EXEC,
    TERMINAL
  }

  static final String VERSION = "0.8.15.202606040825";
  static final int MAX_BYTES = 16 * 1024 * 1024;

  interface Agent {
    String version() throws IOException;

    String session() throws IOException;

    byte @Nullable [] executionDataWithoutReset() throws IOException;
  }

  @FunctionalInterface
  interface Export {
    void write(String name, byte[] bytes) throws IOException;
  }

  private final Object lock = new Object();
  private final FixedNativeCoverageProfile profile;
  private final Agent agent;
  private final Export export;
  private final EnumSet<Point> attempted = EnumSet.noneOf(Point.class);

  FixedNativeCoverageCheckpoint(
      @Nullable FixedNativeCoverageProfile profile,
      @Nullable Agent agent,
      @Nullable Export export) {
    if (profile == null || agent == null || export == null)
      throw new IllegalArgumentException("fixed PT checkpoint dependencies required");
    this.profile = profile;
    this.agent = agent;
    this.export = export;
  }

  /** Default does not load agent classes, open outputs, or change environment/argv. */
  public static Optional<FixedNativeCoverageCheckpoint> fromCurrentJvm(
      ServiceConfigFiles.Service service,
      FixedNativeCoverageProfile.Phase phase,
      @Nullable String admittedInvocation)
      throws IOException {
    Optional<FixedNativeCoverageProfile> profile;
    try {
      profile =
          FixedNativeCoverageProfile.parse(
              service,
              phase,
              admittedInvocation,
              ManagementFactory.getRuntimeMXBean().getInputArguments());
    } catch (IllegalArgumentException failure) {
      throw unavailable();
    }
    return open(profile);
  }

  /** SSC196: terminal-only real Unit actors; never ordinary startup proof/forwarding. */
  public static Optional<FixedNativeCoverageCheckpoint> fromCurrentTerminalJvm(
      FixedNativeCoverageProfile.TerminalRole role, @Nullable String admittedInvocation)
      throws IOException {
    Optional<FixedNativeCoverageProfile> profile;
    try {
      profile =
          FixedNativeCoverageProfile.parseTerminal(
              role, admittedInvocation, ManagementFactory.getRuntimeMXBean().getInputArguments());
    } catch (IllegalArgumentException failure) {
      throw unavailable();
    }
    return open(profile);
  }

  private static Optional<FixedNativeCoverageCheckpoint> open(
      Optional<FixedNativeCoverageProfile> profile) throws IOException {
    if (profile.isEmpty()) return Optional.empty();
    NativeCoveragePrivateFile.verifyPinnedAgent();
    var value = profile.orElseThrow();
    return Optional.of(
        new FixedNativeCoverageCheckpoint(
            value,
            new PublicAgent(),
            (name, bytes) -> NativeCoveragePrivateFile.export(value, name, bytes)));
  }

  public FixedNativeCoverageProfile ordinaryProfile() {
    return profile.forOrdinary();
  }

  /** Attempt is consumed BEFORE any agent/I/O call; unknown or partial capture is never retried. */
  public void capture(@Nullable Point point) throws IOException {
    synchronized (lock) {
      if (point == null
          || (point == Point.BEFORE_EXEC
              && profile.phase() != FixedNativeCoverageProfile.Phase.ROOT))
        throw new IllegalArgumentException("fixed PT checkpoint point required");
      if (!attempted.add(point)) throw unavailable();
      require(VERSION.equals(agent.version()) && profile.sessionId().equals(agent.session()));
      byte[] value = agent.executionDataWithoutReset();
      if (value == null || value.length < 5 || value.length > MAX_BYTES) throw unavailable();
      // Independent collector validates the full session/class byte stream, never this header
      // alone.
      require(
          value[0] == 1
              && value[1] == (byte) 0xc0
              && value[2] == (byte) 0xc0
              && value[3] == 0x10
              && value[4] == 7);
      require(VERSION.equals(agent.version()) && profile.sessionId().equals(agent.session()));
      String suffix = point == Point.BEFORE_EXEC ? ".before-exec.exec" : ".terminal.exec";
      export.write(profile.invocation() + suffix, value.clone());
    }
  }

  static void require(boolean value) throws IOException {
    if (!value) throw unavailable();
  }

  static IOException unavailable() {
    return new IOException("fixed PT native capture unavailable");
  }

  /** Only documented PUBLIC RT/IAgent methods, no private reflection, attach, reset or sockets. */
  private static final class PublicAgent implements Agent {
    private final Object agent;
    private final Method version;
    private final Method session;
    private final Method data;

    PublicAgent() throws IOException {
      try {
        var loader = ClassLoader.getSystemClassLoader();
        var rt = Class.forName("org.jacoco.agent.rt.RT", true, loader);
        var type = Class.forName("org.jacoco.agent.rt.IAgent", true, loader);
        requirePinnedSource(rt);
        requirePinnedSource(type);
        Object actual = rt.getMethod("getAgent").invoke(null);
        if (actual == null || !type.isInstance(actual)) throw unavailable();
        agent = actual;
        version = type.getMethod("getVersion");
        session = type.getMethod("getSessionId");
        data = type.getMethod("getExecutionData", boolean.class);
      } catch (ReflectiveOperationException | java.net.URISyntaxException failure) {
        throw unavailable();
      }
    }

    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC193/PG-D375 fixed Linux pinned agent CodeSource only; NCHECK193/NEXPORT193/native; no arbitrary path or coverage exclusion")
    private static void requirePinnedSource(Class<?> type)
        throws IOException, java.net.URISyntaxException {
      var source = type.getProtectionDomain().getCodeSource();
      if (source == null || source.getLocation() == null) throw unavailable();
      require(
          Path.of(source.getLocation().toURI())
              .equals(Path.of(FixedNativeCoverageProfile.AGENT_PATH)));
    }

    @Override
    public String version() throws IOException {
      return string(version);
    }

    @Override
    public String session() throws IOException {
      return string(session);
    }

    private String string(Method method) throws IOException {
      try {
        Object value = method.invoke(agent);
        if (!(value instanceof String text)) throw unavailable();
        return text;
      } catch (ReflectiveOperationException failure) {
        throw unavailable();
      }
    }

    @Override
    public byte[] executionDataWithoutReset() throws IOException {
      try {
        Object value = data.invoke(agent, false);
        if (!(value instanceof byte[] bytes)) throw unavailable();
        return bytes;
      } catch (ReflectiveOperationException failure) {
        throw unavailable();
      }
    }
  }
}
