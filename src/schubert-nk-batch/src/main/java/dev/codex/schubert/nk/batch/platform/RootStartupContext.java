package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Root emitter's kernel proc / system manager / fixed Unit context, before opening host view.
 * NK-OPS-001; SYS-002/004,OPS-009; UI212/251; SS342/343 SSC086/087/104; PG296/326;
 * PT-OPS-ROOTCTX-001..009. This authenticates context only, never the complete startup permit.
 */
@NullMarked
public final class RootStartupContext {
  private static final java.lang.String LITERAL_PROC = "proc";

  private static final java.lang.String LITERAL_LOADSTATE = "LoadState";

  private static final java.lang.String LITERAL_ACTIVESTATE = "ActiveState";

  private static final java.lang.String LITERAL_SUBSTATE = "SubState";

  private static final java.lang.String LITERAL_MAINPID = "MainPID";

  private static final java.lang.String LITERAL_INVOCATIONID = "InvocationID";

  private static final java.lang.String LITERAL_CONTROLGROUP = "ControlGroup";

  private static final java.lang.String LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME =
      "DMI_HARDCODED_ABSOLUTE_FILENAME";

  public enum Service {
    API("schubert-nk-api.service"),
    WEB("schubert-nk-web.service"),
    MORNING("schubert-nk-morning-controller.service"),
    CLEANUP("schubert-nk-cleanup.service"),
    EXPIRY("schubert-nk-expiry-cleanup.service");
    private final String unit;

    Service(String unit) {
      this.unit = unit;
    }

    public String unit() {
      return unit;
    }
  }

  public record Snapshot(
      Service service,
      String boot,
      String invocation,
      long pid,
      long startTicks,
      long initStartTicks,
      String controlGroup) {
    public Snapshot {
      Objects.requireNonNull(service, "service");
      Objects.requireNonNull(boot, "boot");
      Objects.requireNonNull(invocation, "invocation");
      Objects.requireNonNull(controlGroup, "cgroup");
    }

    @Override
    public String toString() {
      return "RootStartupContext.Snapshot[REDACTED]";
    }
  }

  interface Io {
    long effectiveUid();

    long pid();

    String procFilesystem() throws IOException;

    String initExecutable() throws IOException;

    byte[] boot() throws IOException;

    byte[] stat(long pid) throws IOException;

    byte[] cgroup(long pid) throws IOException;

    byte[] unit(Service service) throws IOException;

    default long serviceRootUid(long pid) throws IOException {
      throw unavailable();
    }

    default byte[] unitDeadline(Service service) throws IOException {
      throw unavailable();
    }

    String invocation();
  }

  private final Io io;

  public static RootStartupContext create() {
    return new RootStartupContext(new NativeIo());
  }

  RootStartupContext(Io io) {
    this.io = Objects.requireNonNull(io, "root context IO");
  }

  public Snapshot capture(Service service) throws IOException {
    Objects.requireNonNull(service, "service");
    try {
      Snapshot first = observe(service);
      require(first.equals(observe(service)));
      return first;
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  public void recheck(Snapshot expected) throws IOException {
    Objects.requireNonNull(expected, "expected root context");
    require(expected.equals(capture(expected.service())));
  }

  /** SSC137: Morning observes only the two fixed Root phases, never a caller-provided PID/Unit. */
  public Snapshot captureServiceRoot(Snapshot morning, Service target) throws IOException {
    Objects.requireNonNull(morning, "same Morning parent");
    Objects.requireNonNull(target, "fixed service Root");
    require(
        morning.service() == Service.MORNING && (target == Service.API || target == Service.WEB));
    recheck(morning);
    Snapshot first = observeServiceRoot(morning, target);
    require(first.equals(observeServiceRoot(morning, target)));
    recheck(morning);
    return first;
  }

  /** Captured Root PID disappearance only, never a receipt or whole-Unit-empty claim. */
  public boolean serviceGenerationExited(Snapshot morning, Snapshot captured) throws IOException {
    Objects.requireNonNull(morning);
    Objects.requireNonNull(captured);
    require(
        morning.service() == Service.MORNING
            && (captured.service() == Service.API || captured.service() == Service.WEB)
            && morning.boot().equals(captured.boot())
            && captured.pid() > 1
            && captured.pid() != morning.pid()
            && captured.controlGroup().equals("/system.slice/" + captured.service().unit()));
    recheck(morning);
    boolean first = missingGeneration(captured);
    recheck(morning);
    boolean second = missingGeneration(captured);
    require(!first || second);
    recheck(morning);
    // After the race guard, first=true implies second=true; both reads remain mandatory.
    return first;
  }

  private boolean missingGeneration(Snapshot captured) throws IOException {
    byte[] bytes = new byte[0];
    try {
      bytes = Objects.requireNonNull(io.stat(captured.pid()));
      require(start(bytes, captured.pid()) == captured.startTicks());
      return false;
    } catch (java.nio.file.NoSuchFileException gone) {
      return true;
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  private Snapshot observeServiceRoot(Snapshot morning, Service target) throws IOException {
    return observeService(morning, target, true);
  }

  /** SSC164: generation data only; ordinary identity/readiness is separately mandatory. */
  public void recheckServiceGeneration(Snapshot morning, Snapshot captured) throws IOException {
    Objects.requireNonNull(morning);
    Objects.requireNonNull(captured);
    require(
        morning.service() == Service.MORNING
            && (captured.service() == Service.API || captured.service() == Service.WEB)
            && morning.boot().equals(captured.boot())
            && morning.initStartTicks() == captured.initStartTicks());
    recheck(morning);
    require(captured.equals(observeService(morning, captured.service(), false)));
    require(captured.equals(observeService(morning, captured.service(), false)));
    recheck(morning);
  }

  private Snapshot observeService(Snapshot morning, Service target, boolean rootPhase)
      throws IOException {
    require(io.effectiveUid() == 0);
    require(
        LITERAL_PROC.equals(io.procFilesystem())
            && "/usr/lib/systemd/systemd".equals(io.initExecutable()));
    require(ascii(io.boot(), 37).equals(morning.boot() + "\n"));
    require(start(io.stat(1), 1) == morning.initStartTicks());
    byte[] first = Objects.requireNonNull(io.unit(target));
    try {
      var unit = properties(first);
      require(
          unit.keySet()
              .equals(
                  Set.of(
                      "Id",
                      LITERAL_LOADSTATE,
                      LITERAL_ACTIVESTATE,
                      LITERAL_SUBSTATE,
                      LITERAL_MAINPID,
                      LITERAL_INVOCATIONID,
                      LITERAL_CONTROLGROUP)));
      String group = "/system.slice/" + target.unit();
      require(
          target.unit().equals(unit.get("Id"))
              && "loaded".equals(unit.get(LITERAL_LOADSTATE))
              && Set.of("activating", "active").contains(unit.get(LITERAL_ACTIVESTATE))
              && Set.of("start", "running").contains(unit.get(LITERAL_SUBSTATE))
              && group.equals(unit.get(LITERAL_CONTROLGROUP)));
      String pidText = Objects.requireNonNull(unit.get(LITERAL_MAINPID));
      String invocation = Objects.requireNonNull(unit.get(LITERAL_INVOCATIONID));
      require(pidText.matches("[1-9][0-9]{0,9}") && invocation.matches("(?!0{32}$)[0-9a-f]{32}"));
      long pid = Long.parseLong(pidText); // The preceding 1..10 decimal digits always fit a long.
      require(
          pid >= 2
              && pid <= Integer.MAX_VALUE
              && pid != morning.pid()
              && !invocation.equals(morning.invocation()));
      long ticks = start(io.stat(pid), pid);
      require(ascii(io.cgroup(pid), 4096).equals("0::" + group + "\n"));
      if (rootPhase) require(io.serviceRootUid(pid) == 0);
      long afterTicks = start(io.stat(pid), pid);
      byte[] second = Objects.requireNonNull(io.unit(target));
      try {
        require(ticks == afterTicks && Arrays.equals(first, second));
      } finally {
        Arrays.fill(second, (byte) 0);
      }
      return new Snapshot(
          target, morning.boot(), invocation, pid, ticks, morning.initStartTicks(), group);
    } finally {
      Arrays.fill(first, (byte) 0);
    }
  }

  /** SSC119: systemd's outer start deadline must not be extended by the Java entry clock. */
  public long maintenanceDeadline(Snapshot morning, long parentDeadline) throws IOException {
    Objects.requireNonNull(morning, "same Morning context");
    require(morning.service() == Service.MORNING && parentDeadline > 0);
    return fixedDeadline(morning, parentDeadline, 1_800_000_000_000L);
  }

  /** Actual service Root Unit start clock, never a freshly restarted 120s budget. SSC137. */
  public long serviceRootDeadline(Snapshot self, long parentDeadline) throws IOException {
    Objects.requireNonNull(self);
    require((self.service() == Service.API || self.service() == Service.WEB) && parentDeadline > 0);
    return fixedDeadline(self, parentDeadline, 120_000_000_000L);
  }

  /** Parent-side fixed service budget; never reinterprets the child as the calling Root. */
  public long serviceGenerationDeadline(Snapshot morning, Snapshot captured, long parentDeadline)
      throws IOException {
    require(parentDeadline > 0);
    return fixedDeadline(
        captured,
        parentDeadline,
        120_000_000_000L,
        () -> recheckServiceGeneration(morning, captured));
  }

  @FunctionalInterface
  private interface Verification {
    void check() throws IOException;
  }

  private long fixedDeadline(Snapshot morning, long parentDeadline, long duration)
      throws IOException {
    return fixedDeadline(morning, parentDeadline, duration, () -> recheck(morning));
  }

  private long fixedDeadline(
      Snapshot morning, long parentDeadline, long duration, Verification guard) throws IOException {
    guard.check();
    byte[] first = new byte[0];
    byte[] second = new byte[0];
    try {
      first = Objects.requireNonNull(io.unitDeadline(morning.service()), "deadline manager bytes");
      var values = properties(first);
      require(
          values
              .keySet()
              .equals(
                  Set.of(
                      "Id",
                      LITERAL_INVOCATIONID,
                      LITERAL_MAINPID,
                      "ExecMainStartTimestampMonotonic")));
      require(morning.service().unit().equals(values.get("Id")));
      require(morning.invocation().equals(values.get(LITERAL_INVOCATIONID)));
      require(Long.toString(morning.pid()).equals(values.get(LITERAL_MAINPID)));
      String start = Objects.requireNonNull(values.get("ExecMainStartTimestampMonotonic"));
      require(start.matches("[1-9][0-9]{0,19}"));
      long started = Math.multiplyExact(Long.parseLong(start), 1000L);
      long unitDeadline = Math.addExact(started, duration);
      require(parentDeadline > started);
      guard.check();
      second = Objects.requireNonNull(io.unitDeadline(morning.service()), "deadline manager bytes");
      require(Arrays.equals(first, second));
      guard.check();
      return Math.min(parentDeadline, unitDeadline);
    } catch (IOException | IllegalArgumentException | ArithmeticException invalid) {
      throw unavailable();
    } finally {
      Arrays.fill(first, (byte) 0);
      Arrays.fill(second, (byte) 0);
    }
  }

  private Snapshot observe(Service service) throws IOException {
    require(io.effectiveUid() == 0);
    require(LITERAL_PROC.equals(io.procFilesystem()));
    require("/usr/lib/systemd/systemd".equals(io.initExecutable()));
    String boot = ascii(io.boot(), 37);
    require(
        boot.matches(
            "(?!00000000-0000-0000-0000-000000000000\\n"
                + "$)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\n"));
    long pid = io.pid();
    require(pid >= 2 && pid <= Integer.MAX_VALUE);
    long initStart = start(io.stat(1), 1);
    long ownStart = start(io.stat(pid), pid);
    String group = "/system.slice/" + service.unit();
    require(ascii(io.cgroup(pid), 4096).equals("0::" + group + "\n"));
    String invocation = io.invocation();
    require(invocation.matches("(?!0{32}$)[0-9a-f]{32}"));
    Map<String, String> unit = properties(io.unit(service));
    require(
        unit.keySet()
            .equals(
                Set.of(
                    "Id",
                    LITERAL_LOADSTATE,
                    LITERAL_ACTIVESTATE,
                    LITERAL_SUBSTATE,
                    LITERAL_MAINPID,
                    LITERAL_INVOCATIONID,
                    LITERAL_CONTROLGROUP)));
    require(service.unit().equals(unit.get("Id")) && "loaded".equals(unit.get(LITERAL_LOADSTATE)));
    require(Set.of("activating", "active").contains(unit.get(LITERAL_ACTIVESTATE)));
    require(Set.of("start", "running").contains(unit.get(LITERAL_SUBSTATE)));
    require(Long.toString(pid).equals(unit.get(LITERAL_MAINPID)));
    require(
        invocation.equals(unit.get(LITERAL_INVOCATIONID))
            && group.equals(unit.get(LITERAL_CONTROLGROUP)));
    return new Snapshot(
        service, boot.substring(0, 36), invocation, pid, ownStart, initStart, group);
  }

  private static Map<String, String> properties(byte[] input) throws IOException {
    String text = ascii(input, 4096);
    require(text.endsWith("\n"));
    var result = new HashMap<String, String>();
    for (String line : text.substring(0, text.length() - 1).split("\n", -1)) {
      int separator = line.indexOf('=');
      require(separator > 0);
      require(
          result.putIfAbsent(line.substring(0, separator), line.substring(separator + 1)) == null);
    }
    return result;
  }

  private static long start(byte[] bytes, long pid) throws IOException {
    String text = ascii(bytes, 4096);
    require(text.endsWith("\n"));
    require(text.startsWith(pid + " ("));
    int delimiter = text.lastIndexOf(") ");
    require(delimiter >= 3);
    String[] fields = text.substring(delimiter + 2, text.length() - 1).split(" ", -1);
    require(
        fields.length >= 20
            && fields[0].matches("[RSIDTWtKP]")
            && fields[19].matches("[1-9][0-9]{0,18}"));
    try {
      return Long.parseLong(fields[19]);
    } catch (NumberFormatException invalid) {
      throw unavailable();
    }
  }

  private static String ascii(byte[] bytes, int maximum) throws IOException {
    Objects.requireNonNull(bytes, "kernel observation");
    require(bytes.length > 0 && bytes.length <= maximum);
    for (byte b : bytes) require(b == 10 || (b >= 32 && b <= 126));
    return new String(bytes, StandardCharsets.US_ASCII);
  }

  static long rootUid(byte[] bytes) throws IOException {
    Objects.requireNonNull(bytes, "kernel status");
    require(bytes.length > 0 && bytes.length <= 16384);
    for (byte value : bytes) require(value == 9 || value == 10 || (value >= 32 && value <= 126));
    String status = new String(bytes, StandardCharsets.US_ASCII);
    require(status.endsWith("\n"));
    String found = "";
    for (String line : status.split("\n", -1)) {
      if (line.startsWith("Uid:")) {
        require(found.isEmpty());
        found = line;
      }
    }
    require(found.matches("Uid:[ \\t]+0[ \\t]+0[ \\t]+0[ \\t]+0"));
    return 0;
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("startup context unavailable");
  }

  static final class NativeIo implements Io {
    private final UnitQuery query;
    private final LinkRead link;

    interface LinkRead {
      Path read(Path path) throws IOException;
    }

    @FunctionalInterface
    interface UnitQuery {
      byte[] read(Service service, String fields) throws IOException;
    }

    NativeIo() {
      this(LinuxSystemdQuery.create()::read, Files::readSymbolicLink);
    }

    NativeIo(SystemctlStateSource.Start start) {
      this(start, Files::readSymbolicLink);
    }

    NativeIo(SystemctlStateSource.Start start, LinkRead link) {
      this(processQuery(start), link);
    }

    private NativeIo(UnitQuery query, LinkRead link) {
      this.query = Objects.requireNonNull(query, "system manager query");
      this.link = Objects.requireNonNull(link, "kernel init executable");
    }

    private static UnitQuery processQuery(SystemctlStateSource.Start start) {
      Objects.requireNonNull(start, "system manager query");
      return (service, fields) -> queryUnit(start, service, fields);
    }

    private final LinuxInodeSecurity security = LinuxInodeSecurity.create();

    @Override
    public long effectiveUid() {
      return security.effectiveUid();
    }

    @Override
    public long pid() {
      return ProcessHandle.current().pid();
    }

    @Override
    @SuppressFBWarnings(
        value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
        matchType = SuppressMatchType.EXACT,
        justification = "SSC086/087 fixed kernel proc root; ROOTCTX008/native014")
    public String procFilesystem() throws IOException {
      return Files.getFileStore(Path.of("/", LITERAL_PROC)).type();
    }

    @Override
    @SuppressFBWarnings(
        value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC086/087 fixed kernel PID1 exe exception, no user path; ROOTCTX002/008/native014")
    public String initExecutable() throws IOException {
      return Objects.requireNonNull(
              link.read(Path.of("/", LITERAL_PROC, "1", "exe")), "kernel executable")
          .toString();
    }

    @Override
    @SuppressFBWarnings(
        value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
        matchType = SuppressMatchType.EXACT,
        justification = "SSC086/087 fixed kernel boot_id, NOFOLLOW leaf; ROOTCTX002/008/native014")
    public byte[] boot() throws IOException {
      return read(Path.of("/", LITERAL_PROC, "sys", "kernel", "random", "boot_id"), 38);
    }

    @Override
    @SuppressFBWarnings(
        value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC086/087 fixed kernel proc stat, validated PID and NOFOLLOW leaf;"
                + " ROOTCTX003/008/native014")
    public byte[] stat(long pid) throws IOException {
      return read(Path.of("/", LITERAL_PROC, Long.toString(pid), "stat"), 4097);
    }

    @Override
    @SuppressFBWarnings(
        value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC086/087 fixed kernel proc cgroup, validated PID and NOFOLLOW leaf;"
                + " ROOTCTX004/008/native014")
    public byte[] cgroup(long pid) throws IOException {
      return read(Path.of("/", LITERAL_PROC, Long.toString(pid), "cgroup"), 4097);
    }

    @Override
    @SuppressFBWarnings(
        value = LITERAL_DMI_HARDCODED_ABSOLUTE_FILENAME,
        matchType = SuppressMatchType.EXACT,
        justification = "SSC137 fixed service Root kernel status, positive validated PID only")
    public long serviceRootUid(long pid) throws IOException {
      require(pid >= 2 && pid <= Integer.MAX_VALUE);
      byte[] bytes = read(Path.of("/", LITERAL_PROC, Long.toString(pid), "status"), 16385);
      try {
        return rootUid(bytes);
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
    }

    @Override
    public String invocation() {
      return System.getenv().getOrDefault("INVOCATION_ID", "");
    }

    private static byte[] read(Path path, int maximum) throws IOException {
      var input = Files.newInputStream(path, LinkOption.NOFOLLOW_LINKS);
      return dev.codex.schubert.nk.storage.ResourceScope.use(
          input::close, () -> input.readNBytes(maximum));
    }

    @Override
    public byte[] unit(Service service) throws IOException {
      return query.read(
          service, "Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup");
    }

    @Override
    public byte[] unitDeadline(Service service) throws IOException {
      return query.read(service, "Id,InvocationID,MainPID,ExecMainStartTimestampMonotonic");
    }

    private static byte[] queryUnit(
        SystemctlStateSource.Start start, Service service, String fields) throws IOException {
      Process process =
          Objects.requireNonNull(
              start.execute(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=" + fields,
                      service.unit())),
              "system manager process");
      return dev.codex.schubert.nk.storage.ResourceScope.use(
          () -> {
            if (process.isAlive()) process.destroy();
          },
          () -> {
            var stdout = Objects.requireNonNull(process.getInputStream(), "system manager stdout");
            return dev.codex.schubert.nk.storage.ResourceScope.use(
                stdout::close,
                () -> {
                  var stdin =
                      Objects.requireNonNull(process.getOutputStream(), "system manager stdin");
                  return dev.codex.schubert.nk.storage.ResourceScope.use(
                      stdin::close,
                      () -> {
                        var stderr =
                            Objects.requireNonNull(
                                process.getErrorStream(), "system manager stderr");
                        return dev.codex.schubert.nk.storage.ResourceScope.use(
                            stderr::close,
                            () -> {
                              try {
                                if (!process.waitFor(5, TimeUnit.SECONDS)
                                    || process.exitValue() != 0) throw unavailable();
                              } catch (InterruptedException interrupted) {
                                Thread.currentThread().interrupt();
                                throw unavailable();
                              }
                              return stdout.readNBytes(4097);
                            });
                      });
                });
          });
    }
  }
}
