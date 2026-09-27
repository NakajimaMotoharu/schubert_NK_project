package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.*;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Child's independent kernel/NSS/config/release binding AFTER native root proof/2FD admission.
 * Never a standalone authority: full root facts/current permit come from the admitted issuer.
 * NK-OPS-001; SYS002/004,OPS009; UI212/251; SS311/342/343 SSC086..088; PG299;
 * PT-OPS-CHILDCTX-001..008.
 */
@NullMarked
public final class ChildStartupContext {
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
  }

  private final Io io;

  public ChildStartupContext() {
    this(new NativeIo());
  }

  ChildStartupContext(Io io) {
    this.io = Objects.requireNonNull(io, "child context IO");
  }

  public static Inputs inputs(Map<String, String> environment) throws IOException {
    Objects.requireNonNull(environment, "environment");
    for (String key : environment.keySet()) {
      Objects.requireNonNull(key, "environment key");
      if (key.toUpperCase(Locale.ROOT).startsWith("SCHUBERT_NK_STARTUP_"))
        require(key.equals(A_KEY) || key.equals(P_KEY));
    }
    int a = descriptor(environment.getOrDefault(A_KEY, "")),
        proof = descriptor(environment.getOrDefault(P_KEY, ""));
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
    try {
      require("proc".equals(io.filesystem()));
      long pid = io.pid();
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
      long uid = ids(required(status, "Uid")), gid = ids(required(status, "Gid"));
      require(uid == io.uid());
      var groups = new TreeSet<Long>();
      for (String id : required(status, "Groups").split("\\s+"))
        require(groups.add(positive(id, 4294967294L, 10)));
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
      var input = Files.newInputStream(path, LinkOption.NOFOLLOW_LINKS);
      return ResourceScope.use(input::close, () -> input.readNBytes(limit));
    }
  }
}
