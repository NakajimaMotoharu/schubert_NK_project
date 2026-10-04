package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.batch.file.CaddyPublicConfiguration;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import javax.net.ssl.HttpsURLConnection;
import org.jspecify.annotations.NullMarked;

/** Same-parent fixed Caddy daemon/validate/owned TLS login proof. SS342/SSC178/CADDY455. */
@NullMarked
public final class MorningCaddyReadiness {
  @FunctionalInterface
  interface Guard {
    void check() throws IOException;
  }

  interface Io {
    Map<String, String> manager() throws IOException;

    ChildStartupContext.Observed actor(String invocation) throws IOException;

    Set<String> sockets(long pid) throws IOException;

    int login() throws IOException;
  }

  private final Guard guard;
  private final Io io;
  private final String invocation;
  private final long pid;
  private final ChildStartupContext.Observed captured;

  public static MorningCaddyReadiness create(
      RootStartupContext root, RootStartupContext.Snapshot morning, MorningParentBudget budget)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(budget);
    if (morning.service() != RootStartupContext.Service.MORNING) throw unavailable();
    return new MorningCaddyReadiness(
        () -> {
          budget.requireWithin();
          root.recheck(morning);
        },
        new NativeIo(root, morning));
  }

  MorningCaddyReadiness(Guard guard, Io io) throws IOException {
    this.guard = Objects.requireNonNull(guard);
    this.io = Objects.requireNonNull(io);
    guard.check();
    var manager = Objects.requireNonNull(io.manager());
    profile(manager);
    invocation = Objects.requireNonNull(manager.get("InvocationID"));
    pid = Long.parseLong(Objects.requireNonNull(manager.get("MainPID")));
    captured = Objects.requireNonNull(io.actor(invocation));
    if (captured.pid() != pid) throw unavailable();
    guard.check();
    if (!manager.equals(io.manager())) throw unavailable();
  }

  /** Manager-active is insufficient: verified CA/hostname HTTPS200 and same owned listener. */
  public boolean ready() throws IOException {
    guard.check();
    var before = Objects.requireNonNull(io.manager());
    profile(before);
    if (!invocation.equals(before.get("InvocationID"))
        || !Long.toString(pid).equals(before.get("MainPID"))
        || !captured.equals(io.actor(invocation))) throw unavailable();
    var sockets = Set.copyOf(Objects.requireNonNull(io.sockets(pid)));
    if (sockets.isEmpty()) return false;
    if (io.login() != 200) return false;
    guard.check();
    if (!captured.equals(io.actor(invocation)) || !before.equals(io.manager())) throw unavailable();
    var after = Set.copyOf(Objects.requireNonNull(io.sockets(pid)));
    guard.check();
    return sockets.stream().anyMatch(after::contains);
  }

  static void profile(Map<String, String> values) throws IOException {
    configuration(values);
    if (!"active".equals(values.get("ActiveState")) || !"running".equals(values.get("SubState")))
      throw unavailable();
    String pidText = Objects.requireNonNull(values.get("MainPID"));
    if (!pidText.matches("[1-9][0-9]{0,9}")
        || Long.parseLong(pidText) < 2
        || Long.parseLong(pidText) > Integer.MAX_VALUE
        || !Objects.requireNonNull(values.get("InvocationID")).matches("(?!0{32}$)[0-9a-f]{32}"))
      throw unavailable();
    String pre = Objects.requireNonNull(values.get("ExecStartPre"));
    if (!pre.matches(
            "\\{ path=/usr/bin/caddy ; argv\\[\\]=/usr/bin/caddy validate --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=\\[[^\\]\\n]+\\] ; stop_time=\\[[^\\]\\n]+\\] ; pid=[1-9][0-9]{0,9} ; code=exited ; status=0/0 \\}")
        || pre.contains("[n/a]")) throw unavailable();
    String start = Objects.requireNonNull(values.get("ExecStart"));
    if (!start.matches(
        "\\{ path=/usr/bin/caddy ; argv\\[\\]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=\\[[^\\]\\n]+\\] ; stop_time=\\[n/a\\] ; pid="
            + pidText
            + " ; code=\\(null\\) ; status=0/0 \\}")) throw unavailable();
  }

  /** Same effective daemon configuration even before any ExecStartPre has run. */
  static void configuration(Map<String, String> values) throws IOException {
    Objects.requireNonNull(values);
    var fixed =
        Map.ofEntries(
            Map.entry("Id", "caddy.service"),
            Map.entry("LoadState", "loaded"),
            Map.entry("Job", ""),
            Map.entry("Type", "notify"),
            Map.entry("Restart", "no"),
            Map.entry("KillMode", "control-group"),
            Map.entry("SendSIGKILL", "no"),
            Map.entry("NoNewPrivileges", "yes"),
            Map.entry("CapabilityBoundingSet", ""),
            Map.entry("AmbientCapabilities", ""),
            Map.entry("User", "caddy"),
            Map.entry("Group", "caddy"),
            Map.entry("SupplementaryGroups", ""),
            Map.entry("TimeoutStartUSec", "30s"),
            Map.entry("TimeoutStopUSec", "30s"));
    var keys = new HashSet<>(fixed.keySet());
    keys.addAll(
        List.of("MainPID", "InvocationID", "ExecStartPre", "ExecStart", "ActiveState", "SubState"));
    if (!values.keySet().equals(keys)) throw unavailable();
    for (var entry : fixed.entrySet())
      if (!entry.getValue().equals(values.get(entry.getKey()))) throw unavailable();
    String pre = Objects.requireNonNull(values.get("ExecStartPre"));
    if (!pre.startsWith(
            "{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy validate --config /etc/caddy/Caddyfile ; ignore_errors=no ; ")
        || pre.indexOf('}') != pre.length() - 1) throw unavailable();
    String start = Objects.requireNonNull(values.get("ExecStart"));
    if (!start.startsWith(
            "{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ; ignore_errors=no ; ")
        || start.indexOf('}') != start.length() - 1) throw unavailable();
  }

  public static void requireConfiguration(
      RootStartupContext root, RootStartupContext.Snapshot morning) throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    root.recheck(morning);
    var io = new NativeIo(root, morning);
    var before = io.manager();
    configuration(before);
    if (!"inactive".equals(before.get("ActiveState"))
        || !"dead".equals(before.get("SubState"))
        || !"0".equals(before.get("MainPID"))
        || !"".equals(before.get("InvocationID"))
        || !before.equals(io.manager())) throw unavailable();
    root.recheck(morning);
  }

  static Set<String> listeners(
      String table, Set<String> descriptors, String address, boolean ipv6) {
    Objects.requireNonNull(table);
    Objects.requireNonNull(descriptors);
    Objects.requireNonNull(address);
    var owned = new HashSet<String>();
    for (String line : table.split("\n")) {
      String[] fields = line.trim().split("\\s+");
      if (fields.length >= 10
          && fields[1].equals(address + ":D778")
          && fields[3].equals("0A")
          && fields[9].matches("[1-9][0-9]{0,19}")
          && descriptors.contains(fields[9])) owned.add(fields[9]);
    }
    return Set.copyOf(owned);
  }

  static String kernelAddress(byte[] address) {
    if (address.length != 4 && address.length != 16)
      throw new IllegalArgumentException("literal IP required");
    var text = new StringBuilder();
    for (int group = 0; group < address.length; group += 4)
      for (int index = group + 3; index >= group; index--)
        text.append(String.format(Locale.ROOT, "%02X", address[index] & 255));
    return text.toString();
  }

  private static IOException unavailable() {
    return new IOException("Caddy readiness unavailable");
  }

  private static final class NativeIo implements Io {
    private final RootStartupContext root;
    private final RootStartupContext.Snapshot morning;
    private final URI site;

    NativeIo(RootStartupContext root, RootStartupContext.Snapshot morning) throws IOException {
      this.root = root;
      this.morning = morning;
      site = CaddyPublicConfiguration.site(root, morning);
    }

    public Map<String, String> manager() throws IOException {
      byte[] bytes =
          new InspectorUnitProbe.NativeReader()
              .execute(
                  List.of(
                      "/usr/bin/systemctl",
                      "--system",
                      "--no-pager",
                      "--no-ask-password",
                      "show",
                      "--property=Id,LoadState,ActiveState,SubState,MainPID,InvocationID,Job,Type,Restart,KillMode,SendSIGKILL,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,User,Group,SupplementaryGroups,TimeoutStartUSec,TimeoutStopUSec,ExecStartPre,ExecStart",
                      "caddy.service"),
                  8192);
      if (bytes.length == 0 || bytes[bytes.length - 1] != '\n') throw unavailable();
      var values = new HashMap<String, String>();
      for (String line :
          new String(bytes, StandardCharsets.US_ASCII).stripTrailing().split("\n", -1)) {
        int separator = line.indexOf('=');
        if (separator < 1
            || values.putIfAbsent(line.substring(0, separator), line.substring(separator + 1))
                != null) throw unavailable();
      }
      return Map.copyOf(values);
    }

    public ChildStartupContext.Observed actor(String invocation) throws IOException {
      root.recheck(morning);
      var actor =
          new ChildStartupContext()
              .verifyCaddy(
                  UUID.fromString(morning.boot()),
                  invocation,
                  new FixedServiceIdentity().resolveCaddy());
      byte[] command =
          MorningServiceReadiness.NativeIo.read(
              Path.of("/proc", Long.toString(actor.pid()), "cmdline"), 16384);
      if (!Arrays.equals(
          command,
          "/usr/bin/caddy\0run\0--config\0/etc/caddy/Caddyfile\0"
              .getBytes(StandardCharsets.US_ASCII))) throw unavailable();
      root.recheck(morning);
      return actor;
    }

    public Set<String> sockets(long pid) throws IOException {
      var proc = Path.of("/proc", Long.toString(pid));
      var descriptors = new HashSet<String>();
      try (var entries = Files.newDirectoryStream(proc.resolve("fd"))) {
        int count = 0;
        for (Path entry : entries) {
          if (++count > 65536) throw unavailable();
          try {
            String target = Files.readSymbolicLink(entry).toString();
            if (target.matches("socket:\\[[1-9][0-9]{0,19}\\]"))
              descriptors.add(target.substring(8, target.length() - 1));
          } catch (NoSuchFileException gone) {
            /* Never counts as owned evidence. */
          }
        }
      }
      byte[] literal = InetAddress.getByName(site.getHost()).getAddress();
      String family = literal.length == 4 ? "tcp" : "tcp6";
      var owned =
          new HashSet<>(
              listeners(
                  new String(
                      MorningServiceReadiness.NativeIo.read(
                          proc.resolve("net/" + family), 2_097_152),
                      StandardCharsets.US_ASCII),
                  descriptors,
                  kernelAddress(literal),
                  literal.length == 16));
      if (literal.length == 4) {
        byte[] mapped = new byte[16];
        mapped[10] = (byte) 255;
        mapped[11] = (byte) 255;
        System.arraycopy(literal, 0, mapped, 12, 4);
        owned.addAll(
            listeners(
                new String(
                    MorningServiceReadiness.NativeIo.read(proc.resolve("net/tcp6"), 2_097_152),
                    StandardCharsets.US_ASCII),
                descriptors,
                kernelAddress(mapped),
                true));
      }
      return Set.copyOf(owned);
    }

    public int login() throws IOException {
      var connection = (HttpsURLConnection) site.toURL().openConnection(Proxy.NO_PROXY);
      connection.setSSLSocketFactory(
          CaddyPublicConfiguration.tls(root, morning).getSocketFactory());
      connection.setInstanceFollowRedirects(false);
      connection.setUseCaches(false);
      connection.setConnectTimeout(1000);
      connection.setReadTimeout(1000);
      connection.setRequestMethod("GET");
      try {
        int status = connection.getResponseCode();
        var input = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
        if (input != null) ResourceScope.use(input::close, () -> Boolean.TRUE);
        return status;
      } finally {
        connection.disconnect();
      }
    }
  }
}
