package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.batch.file.CaddyPublicConfiguration;
import dev.codex.schubert.nk.bootstrap.ChildStartupContext;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.ResourceScope;
import java.io.IOException;
import java.io.InputStream;
import java.net.InetAddress;
import java.net.Proxy;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import javax.net.ssl.HttpsURLConnection;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/** Same-parent fixed Caddy daemon/validate/owned TLS login proof. SS342/SSC178/CADDY455. */
@NullMarked
public final class MorningCaddyReadiness {
  private static final int IPV4_ADDRESS_BYTES = 4;
  private static final int MAXIMUM_SOCKET_DIRECTORY_ENTRIES = 65536;
  private static final int SUCCESS_HTTP_STATUS = 200;

  /** SSC308/PT-CADDYSTREAM001-006: nullable HTTP body, never nullable common ownership. */
  static void closeLoginInput(ResourceScope.Acquire<InputStream, IOException> open)
      throws IOException {
    Objects.requireNonNull(open, "Caddy response stream source");
    InputStream absent = InputStream.nullInputStream();
    ResourceScope.<InputStream, Boolean, IOException>acquire(
        () -> {
          InputStream input = open.open();
          return input == null ? absent : input;
        },
        InputStream::close,
        ignored -> Boolean.TRUE);
  }

  private static final java.lang.String LITERAL_INVOCATIONID = "InvocationID";

  private static final java.lang.String LITERAL_MAINPID = "MainPID";

  private static final java.lang.String LITERAL_EXECMAINCODE = "ExecMainCode";

  private static final java.lang.String LITERAL_EXECSTARTPRE = "ExecStartPre";

  private static final java.lang.String LITERAL_EXECSTART = "ExecStart";

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
    return create(root, morning, budget, "");
  }

  /** SSC180: prior cold generation is a rejection constraint, never startup authority. */
  public static MorningCaddyReadiness create(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      MorningParentBudget budget,
      String previousInvocation)
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
        new NativeIo(root, morning),
        previousInvocation);
  }

  MorningCaddyReadiness(Guard guard, Io io) throws IOException {
    this(guard, io, "");
  }

  MorningCaddyReadiness(Guard guard, Io io, String previousInvocation) throws IOException {
    this.guard = Objects.requireNonNull(guard);
    this.io = Objects.requireNonNull(io);
    Objects.requireNonNull(previousInvocation);
    if (!previousInvocation.isEmpty() && !generation(previousInvocation)) throw unavailable();
    guard.check();
    var manager = Objects.requireNonNull(io.manager());
    profile(manager);
    invocation = Objects.requireNonNull(manager.get(LITERAL_INVOCATIONID));
    if (invocation.equals(previousInvocation)) throw unavailable();
    pid = Long.parseLong(Objects.requireNonNull(manager.get(LITERAL_MAINPID)));
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
    if (!invocation.equals(before.get(LITERAL_INVOCATIONID))
        || !Long.toString(pid).equals(before.get(LITERAL_MAINPID))
        || !captured.equals(io.actor(invocation))) throw unavailable();
    var sockets = Set.copyOf(Objects.requireNonNull(io.sockets(pid)));
    if (sockets.isEmpty()) return false;
    if (io.login() != SUCCESS_HTTP_STATUS) return false;
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
    if (!"success".equals(values.get("Result"))
        || !"0".equals(values.get(LITERAL_EXECMAINCODE))
        || !"0".equals(values.get("ExecMainStatus"))
        || number(values.get("ExecMainStartTimestampMonotonic")).signum() == 0
        || number(values.get("ExecMainExitTimestampMonotonic")).signum() != 0) throw unavailable();
    String pidText = Objects.requireNonNull(values.get(LITERAL_MAINPID));
    if (!pidText.matches("[1-9][0-9]{0,9}")
        || Long.parseLong(pidText) < 2
        || Long.parseLong(pidText) > Integer.MAX_VALUE
        || !Objects.requireNonNull(values.get(LITERAL_INVOCATIONID))
            .matches("(?!0{32}$)[0-9a-f]{32}")) throw unavailable();
    String pre = Objects.requireNonNull(values.get(LITERAL_EXECSTARTPRE));
    if (!pre.matches(
            "\\{ path=/usr/bin/caddy ; argv\\[\\]=/usr/bin/caddy validate --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=\\[[^\\]\\n]+\\] ; stop_time=\\[[^\\]\\n]+\\] ; pid=[1-9][0-9]{0,9} ; code=exited ; status=0(?:/0)? \\}")
        || pre.contains("[n/a]")) throw unavailable();
    String start = Objects.requireNonNull(values.get(LITERAL_EXECSTART));
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
        List.of(
            LITERAL_MAINPID,
            LITERAL_INVOCATIONID,
            LITERAL_EXECSTARTPRE,
            LITERAL_EXECSTART,
            "ActiveState",
            "SubState",
            "Result",
            LITERAL_EXECMAINCODE,
            "ExecMainStatus",
            "ExecMainStartTimestampMonotonic",
            "ExecMainExitTimestampMonotonic"));
    if (!values.keySet().equals(keys)) throw unavailable();
    for (var entry : fixed.entrySet())
      if (!entry.getValue().equals(values.get(entry.getKey()))) throw unavailable();
    String pre = Objects.requireNonNull(values.get(LITERAL_EXECSTARTPRE));
    if (!pre.startsWith(
            "{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy validate --config /etc/caddy/Caddyfile ; ignore_errors=no ; ")
        || pre.indexOf('}') != pre.length() - 1) throw unavailable();
    String start = Objects.requireNonNull(values.get(LITERAL_EXECSTART));
    if (!start.startsWith(
            "{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy run --config /etc/caddy/Caddyfile ; ignore_errors=no ; ")
        || start.indexOf('}') != start.length() - 1) throw unavailable();
  }

  public static void requireConfiguration(
      RootStartupContext root, RootStartupContext.Snapshot morning) throws IOException {
    coldInvocation(root, morning);
  }

  /** Continuous actual parent and whole-kernel observation, first boot or normal history. */
  public static String coldInvocation(RootStartupContext root, RootStartupContext.Snapshot morning)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    root.recheck(morning);
    var io = new NativeIo(root, morning);
    var before = io.manager();
    String previous = cold(before);
    var terminal = MaintenanceUnitTermination.create(root, morning, MaintenanceUnit.CADDY);
    var first = terminal.quiescentObservation().orElseThrow(MorningCaddyReadiness::unavailable);
    var second = terminal.quiescentObservation().orElseThrow(MorningCaddyReadiness::unavailable);
    if (!previous.equals(first.manager().observedValues().get(10))
        || !first.manager().matches(second.manager())
        || first.leafPresent() != second.leafPresent()
        || !first.directories().equals(second.directories())
        || !before.equals(io.manager())) throw unavailable();
    root.recheck(morning);
    return previous;
  }

  static String cold(Map<String, String> before) throws IOException {
    configuration(before);
    if (!"inactive".equals(before.get("ActiveState"))
        || !"dead".equals(before.get("SubState"))
        || !"0".equals(before.get(LITERAL_MAINPID))
        || !"success".equals(before.get("Result"))
        || !"0".equals(before.get("ExecMainStatus"))) throw unavailable();
    String invocation = Objects.requireNonNull(before.get(LITERAL_INVOCATIONID));
    var start = number(before.get("ExecMainStartTimestampMonotonic"));
    var ended = number(before.get("ExecMainExitTimestampMonotonic"));
    String pre = Objects.requireNonNull(before.get(LITERAL_EXECSTARTPRE));
    String run = Objects.requireNonNull(before.get(LITERAL_EXECSTART));
    if (invocation.isEmpty()) {
      if (!"0".equals(before.get(LITERAL_EXECMAINCODE))
          || start.signum() != 0
          || ended.signum() != 0
          || !unused(pre, "validate")
          || !unused(run, "run")) throw unavailable();
    } else if (!generation(invocation)
        || !"1".equals(before.get(LITERAL_EXECMAINCODE))
        || start.signum() == 0
        || ended.compareTo(start) < 0
        || !((normal(pre, "validate") && normal(run, "run"))
            // SS342/SSC192: reload-cleared auxiliary data rejects the old generation only.
            // It is not evidence of validation, readiness, ownership, or normal outer close.
            || (unused(pre, "validate") && unused(run, "run")))) throw unavailable();
    return invocation;
  }

  private static boolean generation(String value) {
    return value.matches("(?!0{32}$)[0-9a-f]{32}");
  }

  private static java.math.BigInteger number(@Nullable String value) throws IOException {
    if (value == null || !value.matches("0|[1-9][0-9]{0,19}")) throw unavailable();
    var number = new java.math.BigInteger(value);
    if (number.compareTo(new java.math.BigInteger("18446744073709551615")) > 0) throw unavailable();
    return number;
  }

  private static boolean unused(String value, String operation) {
    return value.equals(
        "{ path=/usr/bin/caddy ; argv[]=/usr/bin/caddy "
            + operation
            + " --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }");
  }

  private static boolean normal(String value, String operation) {
    var match =
        java.util.regex.Pattern.compile(
                "\\{ path=/usr/bin/caddy ; argv\\[\\]=/usr/bin/caddy "
                    + operation
                    + " --config /etc/caddy/Caddyfile ; ignore_errors=no ; start_time=\\[[^\\]\\n]+\\] ; stop_time=\\[[^\\]\\n]+\\] ; pid=([1-9][0-9]{0,9}) ; code=exited ; status=0(?:/0)? \\}")
            .matcher(value);
    if (!match.matches() || value.contains("[n/a]")) return false;
    // This mandatory capture participates in every successful match; no optional group exists.
    long process = Long.parseLong(Objects.requireNonNull(match.group(1)));
    return process >= 2 && process <= Integer.MAX_VALUE;
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
                      "--property=Id,LoadState,ActiveState,SubState,MainPID,InvocationID,Job,Type,Restart,KillMode,SendSIGKILL,NoNewPrivileges,CapabilityBoundingSet,AmbientCapabilities,User,Group,SupplementaryGroups,TimeoutStartUSec,TimeoutStopUSec,ExecStartPre,ExecStart,Result,ExecMainCode,ExecMainStatus,ExecMainStartTimestampMonotonic,ExecMainExitTimestampMonotonic",
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
          // PG-D802/2472: retain the post-increment limit and the same failure catalog.
          count++;
          if (count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES) throw unavailable();
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
      if (literal.length == IPV4_ADDRESS_BYTES) {
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
        closeLoginInput(
            () -> status >= 400 ? connection.getErrorStream() : connection.getInputStream());
        return status;
      } finally {
        connection.disconnect();
      }
    }
  }
}
