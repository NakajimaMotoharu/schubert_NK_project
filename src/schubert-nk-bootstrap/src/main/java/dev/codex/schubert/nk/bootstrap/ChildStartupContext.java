package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.LinuxStartupAdmission;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
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
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Child's independent kernel/NSS/config/release binding AFTER native root proof/2FD admission.
 * Never a standalone authority: full root facts/current permit come from the admitted issuer.
 * NK-OPS-001; SYS002/004,OPS009; UI212/251; SS311/342/343 SSC086..088; PG299;
 * PT-OPS-CHILDCTX-001..008.
 */
@NullMarked
public final class ChildStartupContext {
  private static final java.lang.String LITERAL_LOADSTATE = "LoadState";

  private static final java.lang.String LITERAL_ACTIVESTATE = "ActiveState";

  private static final java.lang.String LITERAL_SUBSTATE = "SubState";

  private static final java.lang.String LITERAL_MAINPID = "MainPID";

  private static final java.lang.String LITERAL_INVOCATIONID = "InvocationID";

  private static final java.lang.String LITERAL_CONTROLGROUP = "ControlGroup";

  /** Maintenance parents only. It grants neither ordinary startup proof nor caller-selected PID. */
  public enum MaintenanceParent {
    MORNING("schubert-nk-morning-controller.service"),
    CLEANUP("schubert-nk-cleanup.service");
    private final String unit;

    MaintenanceParent(String unit) {
      this.unit = unit;
    }
  }

  private static final String A_KEY = "SCHUBERT_NK_STARTUP_ADMISSION_FD";
  private static final String P_KEY = "SCHUBERT_NK_STARTUP_PROOF_FD";

  public record Inputs(int admissionFd, int proofFd, String invocation) {
    public Inputs {
      Objects.requireNonNull(invocation, "manager invocation");
    }

    @Override
    public String toString() {
      return "ChildStartupContext.Inputs[REDACTED]";
    }
  }

  public record Observed(
      String boot,
      long pid,
      long startTicks,
      long uid,
      long gid,
      List<Long> groups,
      String cgroup,
      boolean zeroCapabilities,
      boolean noNewPrivileges) {
    public Observed {
      Objects.requireNonNull(boot, "boot");
      groups = List.copyOf(groups);
      Objects.requireNonNull(cgroup, "cgroup");
    }

    @Override
    public String toString() {
      return "ChildStartupContext.Observed[REDACTED]";
    }
  }

  interface Io {
    long pid();

    long uid();

    String filesystem() throws IOException;

    byte[] boot() throws IOException;

    byte[] stat(long pid) throws IOException;

    byte[] status(long pid) throws IOException;

    byte[] cgroup(long pid) throws IOException;

    default byte[] maintenanceUnit(MaintenanceParent parent) throws IOException {
      throw unavailable();
    }

    default byte[] inspectorUnit() throws IOException {
      throw unavailable();
    }

    default byte[] brokerUnit() throws IOException {
      throw unavailable();
    }

    default byte[] caddyUnit() throws IOException {
      throw unavailable();
    }
  }

  private final Io io;

  public ChildStartupContext() {
    this(new NativeIo());
  }

  ChildStartupContext(Io io) {
    this.io = Objects.requireNonNull(io, "child context IO");
  }

  /** BUG268: exact internal names only. Name recognition is never descriptor admission. */
  public static boolean isDescriptorKey(String key) {
    Objects.requireNonNull(key, "environment key");
    return A_KEY.equals(key) || P_KEY.equals(key);
  }

  public static Inputs inputs(Map<String, String> environment) throws IOException {
    Objects.requireNonNull(environment, "environment");
    for (String key : environment.keySet()) {
      Objects.requireNonNull(key, "environment key");
      if (key.toUpperCase(Locale.ROOT).startsWith("SCHUBERT_NK_STARTUP_"))
        require(key.equals(A_KEY) || key.equals(P_KEY));
    }
    int a = descriptor(environment.getOrDefault(A_KEY, ""));
    int proof = descriptor(environment.getOrDefault(P_KEY, ""));
    require(a != proof);
    String invocation = environment.getOrDefault("INVOCATION_ID", "");
    require(invocation.matches("(?!0{32}$)[0-9a-f]{32}"));
    return new Inputs(a, proof, invocation);
  }

  private static int descriptor(String value) throws IOException {
    Objects.requireNonNull(value, "descriptor input");
    require(value.matches("[1-9][0-9]{2,4}"));
    int fd = Integer.parseInt(value);
    require(fd >= 128 && fd <= 65535);
    return fd;
  }

  public Observed capture() throws IOException {
    return capture(io.pid(), false);
  }

  /** Nonsecret observations, not transferable authority; rechecked at each mutation. */
  public record InspectorIdentity(Observed child, Observed wrapper, String invocation) {
    public InspectorIdentity {
      Objects.requireNonNull(child, "Inspector child");
      Objects.requireNonNull(wrapper, "Inspector wrapper");
      Objects.requireNonNull(invocation, "Inspector Invocation");
    }

    @Override
    public String toString() {
      return "InspectorIdentity[REDACTED]";
    }
  }

  /** SSC119: actual shell MainPID and Java child are distinct, independently live actors. */
  public InspectorIdentity verifyInspector(
      UUID boot, String invocation, FixedServiceIdentity.Value fixed) throws IOException {
    Objects.requireNonNull(boot, "same maintenance boot");
    Objects.requireNonNull(invocation, "manager Invocation");
    Objects.requireNonNull(fixed, "dedicated Inspector NSS");
    byte[] first = new byte[0];
    byte[] second = new byte[0];
    try {
      require(!Thread.currentThread().isInterrupted());
      require(invocation.matches("(?!0{32}$)[0-9a-f]{32}"));
      var child = capture();
      requireInspectorActor(child, boot, fixed);
      first = Objects.requireNonNull(io.inspectorUnit(), "Inspector manager bytes");
      String source = text(first, 4096);
      require(source.endsWith("\n"));
      var values = new HashMap<String, String>();
      for (String line : source.substring(0, source.length() - 1).split("\n", -1)) {
        int separator = line.indexOf('=');
        require(separator > 0);
        require(
            values.putIfAbsent(line.substring(0, separator), line.substring(separator + 1))
                == null);
      }
      require(
          values
              .keySet()
              .equals(
                  Set.of(
                      "Id",
                      LITERAL_LOADSTATE,
                      LITERAL_ACTIVESTATE,
                      LITERAL_SUBSTATE,
                      LITERAL_MAINPID,
                      LITERAL_INVOCATIONID,
                      LITERAL_CONTROLGROUP)));
      require("schubert-nk-inbox-inspector.service".equals(values.get("Id")));
      require(
          "loaded".equals(values.get(LITERAL_LOADSTATE))
              && "activating".equals(values.get(LITERAL_ACTIVESTATE))
              && "start".equals(values.get(LITERAL_SUBSTATE)));
      require(invocation.equals(values.get(LITERAL_INVOCATIONID)));
      require(
          "/system.slice/schubert-nk-inbox-inspector.service"
              .equals(values.get(LITERAL_CONTROLGROUP)));
      long main =
          positive(Objects.requireNonNull(values.get(LITERAL_MAINPID)), Integer.MAX_VALUE, 10);
      require(main >= 2 && main != child.pid());
      var wrapper = capture(main, false);
      requireInspectorActor(wrapper, boot, fixed);
      require(wrapper.equals(capture(main, false)) && child.equals(capture()));
      second = Objects.requireNonNull(io.inspectorUnit(), "Inspector manager bytes");
      require(Arrays.equals(first, second) && !Thread.currentThread().isInterrupted());
      return new InspectorIdentity(child, wrapper, invocation);
    } catch (IOException known) {
      throw unavailable();
    } finally {
      Arrays.fill(first, (byte) 0);
      Arrays.fill(second, (byte) 0);
    }
  }

  private static void requireInspectorActor(
      Observed actor, UUID boot, FixedServiceIdentity.Value fixed) throws IOException {
    require(
        actor.boot().equals(boot.toString())
            && actor.uid() == fixed.uid()
            && actor.gid() == fixed.gid()
            && actor.groups().equals(fixed.groups())
            && actor.zeroCapabilities()
            && actor.noNewPrivileges()
            && actor.cgroup().equals("0::/system.slice/schubert-nk-inbox-inspector.service\n"));
  }

  /** SSC125/BROKERSTART001: Root reads the fixed daemon, never arbitrary process authority. */
  public Observed verifyBroker(UUID boot, String invocation, FixedServiceIdentity.Value fixed)
      throws IOException {
    return verifyDaemon(boot, invocation, fixed, false);
  }

  /** SSC178: Caddy daemon, never an API/Web Root identity or oneshot receipt. */
  public Observed verifyCaddy(UUID boot, String invocation, FixedServiceIdentity.Value fixed)
      throws IOException {
    return verifyDaemon(boot, invocation, fixed, true);
  }

  private Observed verifyDaemon(
      UUID boot, String invocation, FixedServiceIdentity.Value fixed, boolean caddy)
      throws IOException {
    Objects.requireNonNull(boot, "same broker boot");
    Objects.requireNonNull(invocation, "fresh broker Invocation");
    Objects.requireNonNull(fixed, "fixed broker NSS identity");
    require(io.uid() == 0 && invocation.matches("(?!0{32}$)[0-9a-f]{32}"));
    byte[] first = new byte[0];
    byte[] second = new byte[0];
    try {
      require(!Thread.currentThread().isInterrupted());
      first =
          Objects.requireNonNull(caddy ? io.caddyUnit() : io.brokerUnit(), "daemon manager bytes");
      String source = text(first, 4096);
      require(source.endsWith("\n"));
      var values = new HashMap<String, String>();
      for (String line : source.substring(0, source.length() - 1).split("\n", -1)) {
        int separator = line.indexOf('=');
        require(separator > 0);
        require(
            values.putIfAbsent(line.substring(0, separator), line.substring(separator + 1))
                == null);
      }
      require(
          values
              .keySet()
              .equals(
                  Set.of(
                      "Id",
                      LITERAL_LOADSTATE,
                      LITERAL_ACTIVESTATE,
                      LITERAL_SUBSTATE,
                      LITERAL_MAINPID,
                      LITERAL_INVOCATIONID,
                      LITERAL_CONTROLGROUP)));
      require(
          (caddy ? "caddy.service" : "artemis.service").equals(values.get("Id"))
              && "loaded".equals(values.get(LITERAL_LOADSTATE))
              && "active".equals(values.get(LITERAL_ACTIVESTATE))
              && "running".equals(values.get(LITERAL_SUBSTATE))
              && invocation.equals(values.get(LITERAL_INVOCATIONID))
              && (caddy ? "/system.slice/caddy.service" : "/system.slice/artemis.service")
                  .equals(values.get(LITERAL_CONTROLGROUP)));
      long pid =
          positive(Objects.requireNonNull(values.get(LITERAL_MAINPID)), Integer.MAX_VALUE, 10);
      require(pid >= 2);
      var actual = capture(pid, false, fixed.uid());
      require(
          actual.boot().equals(boot.toString())
              && actual.gid() == fixed.gid()
              && actual.groups().equals(fixed.groups())
              && actual.zeroCapabilities()
              && actual.noNewPrivileges()
              && actual
                  .cgroup()
                  .equals(
                      caddy
                          ? "0::/system.slice/caddy.service\n"
                          : "0::/system.slice/artemis.service\n"));
      require(actual.equals(capture(pid, false, fixed.uid())));
      second =
          Objects.requireNonNull(caddy ? io.caddyUnit() : io.brokerUnit(), "daemon manager bytes");
      require(Arrays.equals(first, second) && !Thread.currentThread().isInterrupted());
      return actual;
    } catch (IOException known) {
      throw unavailable();
    } finally {
      Arrays.fill(first, (byte) 0);
      Arrays.fill(second, (byte) 0);
    }
  }

  /** Root-issued claim is checked against manager and kernel twice, never treated as authority. */
  public void verifyMaintenanceParent(MaintenanceParent kind, MaintenanceOwnerFrame owner)
      throws IOException {
    Objects.requireNonNull(kind, "fixed maintenance parent");
    Objects.requireNonNull(owner, "held owner claim");
    var claimed =
        kind == MaintenanceParent.MORNING
            ? owner.morning()
            : owner.cleanup().orElseThrow(() -> unavailable());
    byte[] first = new byte[0];
    byte[] second = new byte[0];
    try {
      require(!Thread.currentThread().isInterrupted());
      first = Objects.requireNonNull(io.maintenanceUnit(kind), "maintenance manager bytes");
      String source = text(first, 4096);
      require(source.endsWith("\n"));
      var values = new HashMap<String, String>();
      for (String line : source.substring(0, source.length() - 1).split("\n", -1)) {
        int separator = line.indexOf('=');
        require(separator > 0);
        require(
            values.putIfAbsent(line.substring(0, separator), line.substring(separator + 1))
                == null);
      }
      require(
          values
              .keySet()
              .equals(
                  Set.of(
                      "Id",
                      LITERAL_LOADSTATE,
                      LITERAL_ACTIVESTATE,
                      LITERAL_SUBSTATE,
                      LITERAL_MAINPID,
                      LITERAL_INVOCATIONID,
                      LITERAL_CONTROLGROUP)));
      require(kind.unit.equals(values.get("Id")) && "loaded".equals(values.get(LITERAL_LOADSTATE)));
      require(
          "activating".equals(values.get(LITERAL_ACTIVESTATE))
              && "start".equals(values.get(LITERAL_SUBSTATE)));
      require(Long.toString(claimed.pid()).equals(values.get(LITERAL_MAINPID)));
      require(claimed.invocation().equals(values.get(LITERAL_INVOCATIONID)));
      String group = "/system.slice/" + kind.unit;
      require(group.equals(values.get(LITERAL_CONTROLGROUP)));
      var observed = capture(claimed.pid(), true);
      require(owner.boot().toString().equals(observed.boot()));
      require(claimed.startTicks() == observed.startTicks());
      require(observed.cgroup().equals("0::" + group + "\n") && observed.noNewPrivileges());
      require(observed.equals(capture(claimed.pid(), true)));
      second = Objects.requireNonNull(io.maintenanceUnit(kind), "maintenance manager bytes");
      require(Arrays.equals(first, second));
      require(!Thread.currentThread().isInterrupted());
    } catch (IOException known) {
      throw unavailable();
    } finally {
      Arrays.fill(first, (byte) 0);
      Arrays.fill(second, (byte) 0);
    }
  }

  private Observed capture(long pid, boolean maintenanceParent) throws IOException {
    return capture(pid, maintenanceParent, maintenanceParent ? 0 : io.uid());
  }

  private Observed capture(long pid, boolean maintenanceParent, long expectedUid)
      throws IOException {
    try {
      require("proc".equals(io.filesystem()));
      require(pid >= 2 && pid <= Integer.MAX_VALUE);
      String boot = text(io.boot(), 37);
      require(
          boot.matches(
              "(?!00000000-0000-0000-0000-000000000000\\n$)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\n"));
      String stat = text(io.stat(pid), 4096);
      require(stat.endsWith("\n") && stat.startsWith(pid + " ("));
      int close = stat.lastIndexOf(") ");
      require(close >= 3);
      String[] columns = stat.substring(close + 2, stat.length() - 1).split(" ", -1);
      require(columns.length >= 20);
      require(columns[0].matches("[RSIDTWtKP]"));
      long ticks = positive(columns[19], Long.MAX_VALUE, 19);
      Map<String, String> status = status(io.status(pid));
      long uid;
      long gid;
      if (maintenanceParent) {
        require(required(status, "Uid").matches("0\\s+0\\s+0\\s+0"));
        require(required(status, "Gid").matches("0\\s+0\\s+0\\s+0"));
        uid = 0;
        gid = 0;
      } else {
        uid = ids(required(status, "Uid"));
        gid = ids(required(status, "Gid"));
        require(uid == expectedUid);
      }
      var groups = new TreeSet<Long>();
      String groupValues = required(status, "Groups");
      // SSC122/BUG367: Linux supplementary groups may be empty for a genuine GID0 parent.
      // Missing remains invalid; ordinary child/NSS contracts are not widened or synthesized.
      for (String id :
          maintenanceParent && groupValues.isEmpty() ? new String[0] : groupValues.split("\\s+"))
        require(
            groups.add(maintenanceParent && id.equals("0") ? 0 : positive(id, 4294967294L, 10)));
      require(groups.size() <= 16);
      boolean zero = true;
      for (String cap : List.of("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb")) {
        String value = required(status, cap);
        require(value.matches("[0-9a-f]{16}"));
        zero &= value.equals("0000000000000000");
      }
      String nnp = required(status, "NoNewPrivs");
      require(nnp.equals("0") || nnp.equals("1"));
      return new Observed(
          boot.substring(0, 36),
          pid,
          ticks,
          uid,
          gid,
          List.copyOf(groups),
          text(io.cgroup(pid), 4096),
          zero,
          nnp.equals("1"));
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  public static void verify(
      ServiceConfigFiles.Service service,
      Inputs input,
      StartupProofFrame proof,
      LinuxStartupAdmission.Identity admission,
      Observed own,
      FixedServiceIdentity.Value fixed,
      String independentlyReadConfigHash,
      String independentlyReadReleaseHash)
      throws IOException {
    Objects.requireNonNull(service, "service");
    Objects.requireNonNull(input, "child input");
    Objects.requireNonNull(proof, "root proof");
    Objects.requireNonNull(admission, "native A identity");
    Objects.requireNonNull(own, "child observation");
    Objects.requireNonNull(fixed, "fixed NSS identity");
    Objects.requireNonNull(independentlyReadConfigHash, "config hash");
    Objects.requireNonNull(independentlyReadReleaseHash, "release hash");
    require(proof.value("service").equals(service.name()));
    require(
        admission.descriptor() == input.admissionFd()
            && proof.value("admission_fd").equals(Integer.toString(input.admissionFd())));
    require(
        proof.value("admission_device").equals(Long.toUnsignedString(admission.device()))
            && proof.value("admission_inode").equals(Long.toUnsignedString(admission.inode())));
    require(
        proof.value("boot_id").equals(own.boot())
            && proof.value("invocation_id").equals(input.invocation()));
    require(
        proof.value("pid").equals(Long.toString(own.pid()))
            && proof.value("start_ticks").equals(Long.toString(own.startTicks())));
    require(
        proof.value("service_uid").equals(Long.toString(fixed.uid())) && own.uid() == fixed.uid());
    require(
        proof.value("service_gid").equals(Long.toString(fixed.gid())) && own.gid() == fixed.gid());
    require(
        proof.value("service_groups").equals(fixed.groupArgument())
            && own.groups().equals(fixed.groups()));
    String unit =
        service == ServiceConfigFiles.Service.API
            ? "schubert-nk-api.service"
            : "schubert-nk-web.service";
    require(own.cgroup().equals("0::/system.slice/" + unit + "\n"));
    require(own.zeroCapabilities() && own.noNewPrivileges());
    require(
        proof.value("config_sha256").equals(independentlyReadConfigHash)
            && proof.value("release_sha256").equals(independentlyReadReleaseHash));
  }

  private static Map<String, String> status(byte[] input) throws IOException {
    String source = text(input, 65536);
    require(source.endsWith("\n"));
    var result = new HashMap<String, String>();
    for (String row : source.substring(0, source.length() - 1).split("\n", -1)) {
      int delimiter = row.indexOf(':');
      require(delimiter > 0);
      require(
          result.putIfAbsent(row.substring(0, delimiter), row.substring(delimiter + 1).trim())
              == null);
    }
    return result;
  }

  private static String required(Map<String, String> map, String key) throws IOException {
    String value = map.get(key);
    if (value == null) throw unavailable();
    return value;
  }

  private static long ids(String values) throws IOException {
    String[] fields = values.split("\\s+");
    require(fields.length == 4);
    long first = positive(fields[0], 4294967294L, 10);
    for (String value : fields) require(positive(value, 4294967294L, 10) == first);
    return first;
  }

  private static long positive(String value, long maximum, int digits) throws IOException {
    require(value.matches("[1-9][0-9]{0," + (digits - 1) + "}"));
    try {
      long parsed = Long.parseLong(value);
      require(parsed <= maximum);
      return parsed;
    } catch (NumberFormatException invalid) {
      throw unavailable();
    }
  }

  private static String text(byte[] input, int maximum) throws IOException {
    Objects.requireNonNull(input, "kernel bytes");
    require(input.length > 0 && input.length <= maximum);
    for (byte b : input) require(b == 10 || b == 9 || (b >= 32 && b <= 126));
    return new String(input, StandardCharsets.US_ASCII);
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("child startup context unavailable");
  }

  static final class NativeIo implements Io {
    private final LinuxInodeSecurity security = LinuxInodeSecurity.create();
    private final SystemManagerObservation manager;

    NativeIo() {
      this(SystemManagerObservation.create());
    }

    NativeIo(SystemManagerObservation manager) {
      this.manager = Objects.requireNonNull(manager, "fixed system manager reader");
    }

    public long pid() {
      return ProcessHandle.current().pid();
    }

    public long uid() {
      return security.effectiveUid();
    }

    public String filesystem() throws IOException {
      return Files.getFileStore(proc()).type();
    }

    public byte[] boot() throws IOException {
      return read(proc("sys", "kernel", "random", "boot_id"), 38);
    }

    public byte[] stat(long pid) throws IOException {
      return read(proc(Long.toString(pid), "stat"), 4097);
    }

    public byte[] status(long pid) throws IOException {
      return read(proc(Long.toString(pid), "status"), 65537);
    }

    public byte[] cgroup(long pid) throws IOException {
      return read(proc(Long.toString(pid), "cgroup"), 4097);
    }

    public byte[] maintenanceUnit(MaintenanceParent parent) throws IOException {
      return unit(SystemManagerObservation.Service.valueOf(parent.name()));
    }

    public byte[] inspectorUnit() throws IOException {
      return unit(SystemManagerObservation.Service.INSPECTOR);
    }

    public byte[] brokerUnit() throws IOException {
      return unit(SystemManagerObservation.Service.BROKER);
    }

    public byte[] caddyUnit() throws IOException {
      return unit(SystemManagerObservation.Service.CADDY);
    }

    private byte[] unit(SystemManagerObservation.Service fixedUnit) throws IOException {
      return manager.read(
          fixedUnit, "Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup");
    }

    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC086/088 fixed Linux proc only; private literal leaves and numeric PID; CHILDCTX008/native017")
    private static Path proc(String... segments) {
      Path path = Path.of("/", "proc");
      for (String segment : segments) path = path.resolve(segment);
      return path;
    }

    private static byte[] read(Path path, int limit) throws IOException {
      return ResourceScope.acquire(
          () -> Files.newInputStream(path, LinkOption.NOFOLLOW_LINKS),
          java.io.InputStream::close,
          input -> input.readNBytes(limit));
    }
  }
}
