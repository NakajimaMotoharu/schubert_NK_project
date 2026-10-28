package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.Proxy;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.NoSuchFileException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Same captured Root-to-ordinary generation, owned loopback socket and signed information.
 * Observation only, never permit/intent retirement or parent completion authority. NK-OPS-001;
 * SYS002/004,OPS009/UI212/251/SS342/343 SSC164; PT-OPS-READY428001..006.
 */
@NullMarked
public final class MorningServiceReadiness {
  private static final int JSON_OPENING_DELIMITER_LENGTH = 1;
  private static final int MAXIMUM_SOCKET_DIRECTORY_ENTRIES = 65536;
  private static final int SUCCESS_HTTP_STATUS = 200;

  private static final java.lang.String LITERAL_SERVICE_OBSERVATION_UNAVAILABLE =
      "service observation unavailable";

  @FunctionalInterface
  interface Guard {
    void check() throws IOException;
  }

  interface Io {
    byte[] status() throws IOException;

    byte[] command() throws IOException;

    Set<String> sockets() throws IOException;

    Response get(String path) throws IOException;
  }

  record Response(int status, String body) {
    Response {
      Objects.requireNonNull(body);
    }
  }

  private final Guard guard;
  private final Io io;
  private final FixedServiceIdentity.Value identity;
  private final String main;
  private final String information;

  public static MorningServiceReadiness create(
      RootStartupContext root,
      RootStartupContext.Snapshot morning,
      RootStartupContext.Snapshot captured,
      Map<String, String> information)
      throws IOException {
    Objects.requireNonNull(root);
    Objects.requireNonNull(morning);
    Objects.requireNonNull(captured);
    var service =
        switch (captured.service()) {
          case API -> ServiceConfigFiles.Service.API;
          case WEB -> ServiceConfigFiles.Service.WEB;
          default -> throw new IllegalArgumentException("fixed service required");
        };
    root.recheckServiceGeneration(morning, captured);
    return new MorningServiceReadiness(
        () -> root.recheckServiceGeneration(morning, captured),
        new NativeIo(captured.pid(), service == ServiceConfigFiles.Service.API ? 8091 : 8081),
        new FixedServiceIdentity().resolve(service),
        service == ServiceConfigFiles.Service.API
            ? "dev.codex.schubert.nk.api.bootstrap.ApiProcessMain"
            : "dev.codex.schubert.nk.web.bootstrap.WebProcessMain",
        information);
  }

  MorningServiceReadiness(
      Guard guard,
      Io io,
      FixedServiceIdentity.Value identity,
      String main,
      Map<String, String> information) {
    this.guard = Objects.requireNonNull(guard);
    this.io = Objects.requireNonNull(io);
    this.identity = Objects.requireNonNull(identity);
    this.main = Objects.requireNonNull(main);
    var keys = List.of("commit", "app", "config", "schema", "protocol");
    if (!Objects.requireNonNull(information).keySet().equals(Set.copyOf(keys)))
      throw new IllegalArgumentException("invalid public information");
    var json = new StringBuilder("{");
    for (String key : keys) {
      String value = Objects.requireNonNull(information.get(key));
      if (!(key.equals("commit")
          ? value.matches("[0-9a-f]{40}")
          : value.matches("[A-Za-z0-9][A-Za-z0-9._+\\-]{0,127}")))
        throw new IllegalArgumentException("invalid public information");
      if (json.length() > JSON_OPENING_DELIMITER_LENGTH) json.append(',');
      json.append('"').append(key).append("\":\"").append(value).append('"');
    }
    this.information = json.append('}').toString();
  }

  /** Not-yet-ready is false; IO/identity uncertainty never becomes success. */
  public boolean ready() throws IOException {
    guard.check();
    if (!ordinary()) return false;
    var before = Set.copyOf(Objects.requireNonNull(io.sockets()));
    if (before.isEmpty()) return false;
    var health = Objects.requireNonNull(io.get("/actuator/health/readiness"));
    var info = Objects.requireNonNull(io.get("/actuator/info"));
    if (health.status() != 200
        || !health.body().equals("{\"status\":\"UP\"}")
        || info.status() != 200
        || !info.body().equals(information)) return false;
    guard.check();
    if (!ordinary()) return false;
    var after = Set.copyOf(Objects.requireNonNull(io.sockets()));
    guard.check();
    return before.stream().anyMatch(after::contains);
  }

  private boolean ordinary() throws IOException {
    String status = ascii(Objects.requireNonNull(io.status()), 16384);
    var fields = new HashMap<String, String>();
    for (String line : status.split("\n")) {
      int colon = line.indexOf(':');
      if (colon > 0
          && fields.put(line.substring(0, colon), line.substring(colon + 1).trim()) != null)
        return false;
    }
    String uid = String.join(" ", Collections.nCopies(4, Long.toString(identity.uid())));
    String gid = String.join(" ", Collections.nCopies(4, Long.toString(identity.gid())));
    String groups =
        identity.groups().stream()
            .map(Object::toString)
            .collect(java.util.stream.Collectors.joining(" "));
    if (!uid.equals(normal(fields.getOrDefault("Uid", "")))
        || !gid.equals(normal(fields.getOrDefault("Gid", "")))
        || !groups.equals(normal(fields.getOrDefault("Groups", "")))
        || !"1".equals(fields.get("NoNewPrivs"))) return false;
    for (String cap : List.of("CapInh", "CapPrm", "CapEff", "CapBnd", "CapAmb"))
      if (!"0000000000000000".equals(fields.get(cap))) return false;
    byte[] command = Objects.requireNonNull(io.command());
    try {
      if (command.length == 0 || command.length > 16384 || command[command.length - 1] != 0)
        return false;
      String text = new String(command, StandardCharsets.US_ASCII);
      return Arrays.stream(text.split("\u0000", -1)).filter(main::equals).count() == 1;
    } finally {
      Arrays.fill(command, (byte) 0);
    }
  }

  private static String normal(String value) {
    return value.trim().replaceAll("\\s+", " ");
  }

  private static String ascii(byte[] bytes, int maximum) throws IOException {
    if (bytes.length > maximum) throw new IOException(LITERAL_SERVICE_OBSERVATION_UNAVAILABLE);
    for (byte value : bytes)
      if (value < 0 || value == 0) throw new IOException(LITERAL_SERVICE_OBSERVATION_UNAVAILABLE);
    return new String(bytes, StandardCharsets.US_ASCII);
  }

  static Set<String> listeners(String table, Set<String> descriptors, int port, boolean ipv6) {
    Objects.requireNonNull(table);
    Objects.requireNonNull(descriptors);
    String address =
        (ipv6 ? "0000000000000000FFFF00000100007F:" : "0100007F:")
            + String.format(Locale.ROOT, "%04X", port);
    var owned = new HashSet<String>();
    for (String line : table.split("\n")) {
      String[] fields = line.trim().split("\\s+");
      if (fields.length >= 10
          && fields[1].equals(address)
          && fields[3].equals("0A")
          && fields[9].matches("[1-9][0-9]{0,19}")
          && descriptors.contains(fields[9])) owned.add(fields[9]);
    }
    return Set.copyOf(owned);
  }

  static final class NativeIo implements Io {
    private final Path proc;
    private final int port;

    NativeIo(long pid, int port) {
      if (pid < 2 || pid > Integer.MAX_VALUE || (port != 8091 && port != 8081))
        throw new IllegalArgumentException("fixed service required");
      this.proc = Path.of("/proc", Long.toString(pid));
      this.port = port;
    }

    public byte[] status() throws IOException {
      return read(proc.resolve("status"), 16384);
    }

    public byte[] command() throws IOException {
      return read(proc.resolve("cmdline"), 16384);
    }

    static byte[] read(Path path, int limit) throws IOException {
      return ResourceScope.acquire(
          () -> Files.newInputStream(path, LinkOption.NOFOLLOW_LINKS),
          java.io.InputStream::close,
          input -> {
            byte[] bytes = input.readNBytes(limit + 1);
            if (bytes.length > limit)
              throw new IOException(LITERAL_SERVICE_OBSERVATION_UNAVAILABLE);
            return bytes;
          });
    }

    public Set<String> sockets() throws IOException {
      var descriptors = new HashSet<String>();
      try (var entries = Files.newDirectoryStream(proc.resolve("fd"))) {
        int count = 0;
        for (Path entry : entries) {
          // PG-D802/2472: compare the incremented count without embedding the mutation.
          count++;
          if (count > MAXIMUM_SOCKET_DIRECTORY_ENTRIES)
            throw new IOException(LITERAL_SERVICE_OBSERVATION_UNAVAILABLE);
          try {
            String target = Files.readSymbolicLink(entry).toString();
            if (target.matches("socket:\\[[1-9][0-9]{0,19}\\]"))
              descriptors.add(target.substring(8, target.length() - 1));
          } catch (NoSuchFileException gone) {
            /* Kernel FD closed; cannot become owned evidence. */
          }
        }
      }
      var owned =
          new HashSet<>(
              listeners(
                  ascii(read(proc.resolve("net/tcp"), 2_097_152), 2_097_152),
                  descriptors,
                  port,
                  false));
      owned.addAll(
          listeners(
              ascii(read(proc.resolve("net/tcp6"), 2_097_152), 2_097_152),
              descriptors,
              port,
              true));
      return Set.copyOf(owned);
    }

    public Response get(String path) throws IOException {
      if (!Set.of("/actuator/health/readiness", "/actuator/info").contains(path))
        throw new IllegalArgumentException("fixed management path required");
      var connection =
          (HttpURLConnection)
              URI.create("http://127.0.0.1:" + port + path).toURL().openConnection(Proxy.NO_PROXY);
      try {
        connection.setInstanceFollowRedirects(false);
        connection.setConnectTimeout(500);
        connection.setReadTimeout(500);
        int status = connection.getResponseCode();
        if (status != SUCCESS_HTTP_STATUS) return new Response(status, "");
        return ResourceScope.acquire(
            connection::getInputStream,
            java.io.InputStream::close,
            input -> new Response(status, ascii(input.readNBytes(4097), 4096)));
      } finally {
        connection.disconnect();
      }
    }
  }
}
