package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
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
    TERMINAL,
    CLOSING
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
  private boolean terminalCompleted;

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
              && profile.phase() != FixedNativeCoverageProfile.Phase.ROOT)
          || (point == Point.CLOSING && !profile.supportsClosing()))
        throw new IllegalArgumentException("fixed PT checkpoint point required");
      if (!attempted.add(point)) throw unavailable();
      if (point == Point.CLOSING) require(terminalCompleted);
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
      String suffix =
          switch (point) {
            case BEFORE_EXEC -> ".before-exec.exec";
            case TERMINAL -> ".terminal.exec";
            case CLOSING -> ".closing.exec";
          };
      export.write(profile.invocation() + suffix, value.clone());
      if (point == Point.TERMINAL) terminalCompleted = true;
    }
  }

  static void require(boolean value) throws IOException {
    if (!value) throw unavailable();
  }

  static IOException unavailable() {
    return new IOException("fixed PT native capture unavailable");
  }

  /** Only documented PUBLIC RT/IAgent methods, no private reflection, attach, reset or sockets. */
  // PG-D395 / NCHECK597: internal data-provider ports, never startup authority.
  static final class PublicAgent implements Agent {
    @FunctionalInterface
    interface Classes {
      @Nullable Class<?> load(String name) throws ClassNotFoundException;
    }

    @FunctionalInterface
    interface Sources {
      void verify(Class<?> type) throws IOException, java.net.URISyntaxException;
    }

    @FunctionalInterface
    interface Invocation {
      @Nullable Object invoke(Method method, @Nullable Object target, Object[] arguments)
          throws ReflectiveOperationException;
    }

    private final Object agent;
    private final Method retainedVersion;
    private final Method retainedSession;
    private final Method data;
    private final Invocation invocation;

    PublicAgent() throws IOException {
      this(
          name -> Class.forName(name, true, ClassLoader.getSystemClassLoader()),
          PublicAgent::requirePinnedSource,
          (method, target, arguments) -> method.invoke(target, arguments));
    }

    PublicAgent(@Nullable Classes classes, @Nullable Sources sources, @Nullable Invocation invoke)
        throws IOException {
      if (classes == null || sources == null || invoke == null)
        throw new IllegalArgumentException("fixed PT agent dependencies required");
      invocation = invoke;
      try {
        var rt = classes.load("org.jacoco.agent.rt.RT");
        var type = classes.load("org.jacoco.agent.rt.IAgent");
        if (rt == null || type == null) throw unavailable();
        sources.verify(rt);
        sources.verify(type);
        Object actual = invocation.invoke(rt.getMethod("getAgent"), null, new Object[0]);
        if (actual == null || !type.isInstance(actual)) throw unavailable();
        agent = actual;
        retainedVersion = type.getMethod("getVersion");
        retainedSession = type.getMethod("getSessionId");
        data = type.getMethod("getExecutionData", boolean.class);
      } catch (ReflectiveOperationException | java.net.URISyntaxException | IOException failure) {
        StorageIoException.preserveFatal(failure);
        throw unavailable();
      }
    }

    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC193/PG-D375 fixed Linux pinned agent CodeSource only; NCHECK193/NEXPORT193/native; no arbitrary path or coverage exclusion")
    static void requirePinnedSource(Class<?> type) throws IOException, java.net.URISyntaxException {
      var source = type.getProtectionDomain().getCodeSource();
      if (source == null || source.getLocation() == null) throw unavailable();
      require(
          Path.of(source.getLocation().toURI())
              .equals(Path.of(FixedNativeCoverageProfile.AGENT_PATH)));
    }

    @Override
    public String version() throws IOException {
      return string(retainedVersion);
    }

    @Override
    public String session() throws IOException {
      return string(retainedSession);
    }

    private String string(Method method) throws IOException {
      try {
        Object value = invocation.invoke(method, agent, new Object[0]);
        if (!(value instanceof String text)) throw unavailable();
        return text;
      } catch (ReflectiveOperationException failure) {
        StorageIoException.preserveFatal(failure);
        throw unavailable();
      }
    }

    @Override
    public byte[] executionDataWithoutReset() throws IOException {
      try {
        Object value = invocation.invoke(data, agent, new Object[] {false});
        if (!(value instanceof byte[] bytes)) throw unavailable();
        return bytes;
      } catch (ReflectiveOperationException failure) {
        StorageIoException.preserveFatal(failure);
        throw unavailable();
      }
    }
  }
}
