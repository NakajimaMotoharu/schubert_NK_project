package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Root emitter's kernel proc / system manager / fixed Unit context, before opening host view.
 * NK-OPS-001; SYS-002/004,OPS-009; UI212/251; SS342/343 SSC086/087/104; PG296/326;
 * PT-OPS-ROOTCTX-001..009. This authenticates context only, never the complete startup permit.
 */
@NullMarked
public final class RootStartupContext {
  public enum Service {
    API("schubert-nk-api.service"),
    WEB("schubert-nk-web.service"),
    MORNING("schubert-nk-morning-controller.service"),
    CLEANUP("schubert-nk-cleanup.service");
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

  private Snapshot observe(Service service) throws IOException {
    require(io.effectiveUid() == 0);
    require("proc".equals(io.procFilesystem()));
    require("/usr/lib/systemd/systemd".equals(io.initExecutable()));
    String boot = ascii(io.boot(), 37);
    require(
        boot.matches(
            "(?!00000000-0000-0000-0000-000000000000\\n$)[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}\\n"));
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
                    "LoadState",
                    "ActiveState",
                    "SubState",
                    "MainPID",
                    "InvocationID",
                    "ControlGroup")));
    require(service.unit().equals(unit.get("Id")) && "loaded".equals(unit.get("LoadState")));
    require(Set.of("activating", "active").contains(unit.get("ActiveState")));
    require(Set.of("start", "running").contains(unit.get("SubState")));
    require(Long.toString(pid).equals(unit.get("MainPID")));
    require(invocation.equals(unit.get("InvocationID")) && group.equals(unit.get("ControlGroup")));
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

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("startup context unavailable");
  }

  static final class NativeIo implements Io {
    private final SystemctlStateSource.Start start;
    private final LinkRead link;

    interface LinkRead {
      Path read(Path path) throws IOException;
    }

    NativeIo() {
      this(
          command -> SystemctlStateSource.NativeProcess.builder(command).start(),
          Files::readSymbolicLink);
    }

    NativeIo(SystemctlStateSource.Start start) {
      this(start, Files::readSymbolicLink);
    }

    NativeIo(SystemctlStateSource.Start start, LinkRead link) {
      this.start = Objects.requireNonNull(start, "system manager query");
      this.link = Objects.requireNonNull(link, "kernel init executable");
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
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification = "SSC086/087 fixed kernel proc root; ROOTCTX008/native014")
    public String procFilesystem() throws IOException {
      return Files.getFileStore(Path.of("/", "proc")).type();
    }

    @Override
    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC086/087 fixed kernel PID1 exe exception, no user path; ROOTCTX002/008/native014")
    public String initExecutable() throws IOException {
      return Objects.requireNonNull(
              link.read(Path.of("/", "proc", "1", "exe")), "kernel executable")
          .toString();
    }

    @Override
    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification = "SSC086/087 fixed kernel boot_id, NOFOLLOW leaf; ROOTCTX002/008/native014")
    public byte[] boot() throws IOException {
      return read(Path.of("/", "proc", "sys", "kernel", "random", "boot_id"), 38);
    }

    @Override
    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC086/087 fixed kernel proc stat, validated PID and NOFOLLOW leaf; ROOTCTX003/008/native014")
    public byte[] stat(long pid) throws IOException {
      return read(Path.of("/", "proc", Long.toString(pid), "stat"), 4097);
    }

    @Override
    @SuppressFBWarnings(
        value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
        matchType = SuppressMatchType.EXACT,
        justification =
            "SSC086/087 fixed kernel proc cgroup, validated PID and NOFOLLOW leaf; ROOTCTX004/008/native014")
    public byte[] cgroup(long pid) throws IOException {
      return read(Path.of("/", "proc", Long.toString(pid), "cgroup"), 4097);
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
      Process process =
          Objects.requireNonNull(
              start.execute(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=Id,LoadState,ActiveState,SubState,MainPID,InvocationID,ControlGroup",
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
