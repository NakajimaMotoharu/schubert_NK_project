package dev.codex.schubert.nk.bootstrap;

import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.TimeUnit;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed names only; explicit service UID/GID/required groups, never all NSS memberships.
 * NK-OPS-001; SYS002/004,OPS009; UI212/251; SS311/342/343 SSC088; PG298; PT-OPS-SERVICEID-001..008.
 * Root and child independently resolve these non-secret values.
 */
@NullMarked
public final class FixedServiceIdentity {
  public record Value(long uid, long gid, List<Long> groups) {
    public Value {
      groups = List.copyOf(groups);
      if (uid < 1
          || uid > 4294967294L
          || gid < 1
          || gid > 4294967294L
          || groups.isEmpty()
          || groups.size() > 16
          || !groups.contains(gid))
        throw new IllegalArgumentException("invalid fixed service identity");
      long previous = 0;
      for (long group : groups) {
        if (group <= previous || group > 4294967294L)
          throw new IllegalArgumentException("invalid fixed service groups");
        previous = group;
      }
    }

    public String groupArgument() {
      return groups.stream()
          .map(Object::toString)
          .collect(java.util.stream.Collectors.joining(","));
    }

    @Override
    public String toString() {
      return "FixedServiceIdentity.Value[REDACTED]";
    }
  }

  @FunctionalInterface
  interface Query {
    byte[] read(List<String> command) throws IOException;
  }

  @FunctionalInterface
  interface Start {
    Process execute(List<String> command) throws IOException;
  }

  private final Query query;

  public FixedServiceIdentity() {
    this(new NativeQuery());
  }

  FixedServiceIdentity(Query query) {
    this.query = Objects.requireNonNull(query, "fixed NSS query");
  }

  /** SS343/SSC089: the named config group, not the smallest/any service group. */
  public long configurationGroup() throws IOException {
    try {
      return id(
          fields(query.read(List.of("/usr/bin/getent", "group", "schubert")), 4, "schubert")[2]);
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  public Value resolve(ServiceConfigFiles.Service service) throws IOException {
    Objects.requireNonNull(service, "service");
    try {
      String account = service == ServiceConfigFiles.Service.API ? "schubert-api" : "schubert-web";
      String[] passwd =
          fields(query.read(List.of("/usr/bin/getent", "passwd", account)), 7, account);
      long uid = id(passwd[2]), gid = id(passwd[3]);
      var names = new ArrayList<>(List.of(account, "schubert", "schubert-read"));
      if (service == ServiceConfigFiles.Service.API) names.add("schubert-web");
      var groups = new TreeSet<Long>();
      for (String name : names) {
        String[] group = fields(query.read(List.of("/usr/bin/getent", "group", name)), 4, name);
        long value = id(group[2]);
        if (name.equals(account)) require(value == gid);
        require(groups.add(value));
      }
      return new Value(uid, gid, List.copyOf(groups));
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  /** Backup-only fixed entry; does not extend the API/Web enum or inherit application groups. */
  public Value resolveBackup() throws IOException {
    return resolveMaintenance("schubert-backup", List.of("schubert-backup", "schubert"));
  }

  /** SSC119: dedicated Inspector, no API/Web supplementary membership inheritance. */
  public Value resolveInspector() throws IOException {
    return resolveMaintenance(
        "schubert-inbox-inspector",
        List.of("schubert-inbox-inspector", "schubert", "schubert-read"));
  }

  private Value resolveMaintenance(String account, List<String> names) throws IOException {
    try {
      String[] passwd =
          fields(query.read(List.of("/usr/bin/getent", "passwd", account)), 7, account);
      long uid = id(passwd[2]), gid = id(passwd[3]);
      var groups = new TreeSet<Long>();
      for (String name : names) {
        long value = id(fields(query.read(List.of("/usr/bin/getent", "group", name)), 4, name)[2]);
        if (name.equals(account)) require(value == gid);
        require(groups.add(value));
      }
      return new Value(uid, gid, List.copyOf(groups));
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  private static String[] fields(byte[] bytes, int count, String name) throws IOException {
    Objects.requireNonNull(bytes, "NSS bytes");
    require(bytes.length > 0 && bytes.length <= 1024);
    for (int i = 0; i < bytes.length - 1; i++) require(bytes[i] >= 32 && bytes[i] <= 126);
    require(bytes[bytes.length - 1] == 10);
    String[] values =
        new String(bytes, 0, bytes.length - 1, StandardCharsets.US_ASCII).split(":", -1);
    require(values.length == count && values[0].equals(name) && values[1].equals("x"));
    return values;
  }

  private static long id(String text) throws IOException {
    require(text.matches("[1-9][0-9]{0,9}"));
    long value = Long.parseLong(text);
    require(value <= 4294967294L);
    return value;
  }

  private static void require(boolean valid) throws IOException {
    if (!valid) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("service identity unavailable");
  }

  static final class NativeQuery implements Query {
    private final Start start;

    NativeQuery() {
      this(command -> builder(command).start());
    }

    NativeQuery(Start start) {
      this.start = Objects.requireNonNull(start, "NSS process");
    }

    static ProcessBuilder builder(List<String> command) {
      var b = new ProcessBuilder(command).redirectError(ProcessBuilder.Redirect.DISCARD);
      b.environment().clear();
      b.environment().putAll(Map.of("PATH", "/usr/bin:/bin", "LANG", "C", "LC_ALL", "C"));
      return b;
    }

    public byte[] read(List<String> command) throws IOException {
      Process p = Objects.requireNonNull(start.execute(command), "NSS process");
      return ResourceScope.use(
          () -> {
            if (p.isAlive()) p.destroy();
          },
          () -> {
            var output = Objects.requireNonNull(p.getInputStream(), "NSS stdout");
            return ResourceScope.use(
                output::close,
                () -> {
                  var input = Objects.requireNonNull(p.getOutputStream(), "NSS stdin");
                  return ResourceScope.use(
                      input::close,
                      () -> {
                        var error = Objects.requireNonNull(p.getErrorStream(), "NSS stderr");
                        return ResourceScope.use(
                            error::close,
                            () -> {
                              try {
                                if (!p.waitFor(5, TimeUnit.SECONDS) || p.exitValue() != 0)
                                  throw unavailable();
                              } catch (InterruptedException e) {
                                Thread.currentThread().interrupt();
                                throw unavailable();
                              }
                              return output.readNBytes(1025);
                            });
                      });
                });
          });
    }
  }
}
