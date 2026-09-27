package dev.codex.schubert.nk.bootstrap;

import com.google.gson.Strictness;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import java.io.IOException;
import java.io.StringReader;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.*;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Fixed thin-JAR manifest claims only; authentication/held file agreement are separate mandatory
 * gates. Never builds an oracle from the actual DB or from a caller-supplied approved boolean.
 * NK-OPS-001/SYS002/004/OPS009/DAT009/UI212/251/253/SS34311.1/SSC096/PG313;
 * PT-OPS-BOMPROFILE001..016. The original bytes, not serialization, are signed/digested.
 */
@NullMarked
final class ReleaseInventory {
  record Artifact(String path, long size, String sha256) {
    Artifact {
      requirePath(path);
      require(size >= 0);
      require(Objects.requireNonNull(sha256).matches("[0-9a-f]{64}"));
    }
  }

  record Dependency(String coordinate, List<String> paths) {
    Dependency {
      require(
          Objects.requireNonNull(coordinate)
              .matches(
                  "[A-Za-z0-9][A-Za-z0-9._-]{0,127}:[A-Za-z0-9][A-Za-z0-9._-]{0,127}:[A-Za-z0-9][A-Za-z0-9._-]{0,127}"));
      paths = List.copyOf(paths);
      require(!paths.isEmpty() && paths.size() <= 3);
      String previous = "";
      for (String path : paths) {
        requirePath(path);
        require(path.matches("(api|web|operations)/lib/[^/]+\\.jar"));
        require(path.compareTo(previous) > 0);
        previous = path;
      }
    }

    @Override
    public List<String> paths() {
      return List.copyOf(paths);
    }
  }

  private final String release;
  private final Map<String, String> versions, source, build, platform;
  private final List<Artifact> artifacts;
  private final List<Dependency> dependencies;
  private final List<SchemaHistoryAdmission.Row> migrations;

  private ReleaseInventory(
      String release,
      Map<String, String> versions,
      Map<String, String> source,
      Map<String, String> build,
      Map<String, String> platform,
      List<Artifact> artifacts,
      List<Dependency> dependencies,
      List<SchemaHistoryAdmission.Row> migrations) {
    requireToken(release);
    this.release = release;
    this.versions = Map.copyOf(versions);
    this.source = Map.copyOf(source);
    this.build = Map.copyOf(build);
    this.platform = Map.copyOf(platform);
    this.artifacts = List.copyOf(artifacts);
    this.dependencies = List.copyOf(dependencies);
    this.migrations = List.copyOf(migrations);
    versions.values().forEach(ReleaseInventory::requireToken);
    require(Objects.requireNonNull(source.get("commit")).matches("[0-9a-f]{40}"));
    for (String value : source.values()) requireText(value);
    build.values().forEach(ReleaseInventory::requireText);
    platform.values().forEach(ReleaseInventory::requireText);
    require("25".equals(platform.get("javaFeature")));
    new SchemaHistoryAdmission(this.migrations);
    require(this.migrations.size() > 1);
    require(Objects.equals(versions.get("schema"), this.migrations.getLast().version()));
    inventory();
  }

  static ReleaseInventory parse(byte[] original) throws IOException {
    Objects.requireNonNull(original, "original manifest");
    require(original.length > 0 && original.length <= 1_048_576);
    byte[] copy = original.clone();
    try {
      String text = StandardCharsets.UTF_8.newDecoder().decode(ByteBuffer.wrap(copy)).toString();
      require(!text.startsWith("\ufeff"));
      try (var reader = new JsonReader(new StringReader(text))) {
        reader.setStrictness(Strictness.STRICT);
        reader.setNestingLimit(4);
        reader.beginObject();
        key(reader, "format");
        require(string(reader).equals("NKRELEASE1"));
        key(reader, "release");
        String release = string(reader);
        key(reader, "versions");
        var versions =
            fields(reader, List.of("app", "protocol", "storage", "bootstrap", "schema", "config"));
        key(reader, "source");
        var source = fields(reader, List.of("commit", "tag"));
        key(reader, "build");
        var build = fields(reader, List.of("jdkVendor", "jdkVersion", "mavenVersion"));
        key(reader, "platform");
        var platform = new LinkedHashMap<String, String>();
        reader.beginObject();
        for (String name : List.of("osId", "osVersion", "architecture")) {
          key(reader, name);
          platform.put(name, string(reader));
        }
        key(reader, "javaFeature");
        platform.put("javaFeature", Long.toString(number(reader)));
        reader.endObject();
        key(reader, "dependencies");
        var dependencies = dependencies(reader);
        key(reader, "artifacts");
        var artifacts = artifacts(reader);
        key(reader, "migrations");
        var migrations = migrations(reader);
        reader.endObject();
        // Pinned Gson STRICT: after endObject, peek either returns EOF or throws for any
        // extra token (doPeek NONEMPTY_DOCUMENT/checkLenient). Keep the validating call;
        // do not add a redundant comparison whose false side cannot occur in this fixed reader.
        reader.peek();
        return new ReleaseInventory(
            release, versions, source, build, platform, artifacts, dependencies, migrations);
      }
    } catch (IOException | IllegalArgumentException | IllegalStateException invalid) {
      throw new IOException("release inventory unavailable");
    } finally {
      Arrays.fill(copy, (byte) 0);
    }
  }

  private static Map<String, String> fields(JsonReader r, List<String> names) throws IOException {
    var values = new LinkedHashMap<String, String>();
    r.beginObject();
    for (String name : names) {
      key(r, name);
      values.put(name, string(r));
    }
    r.endObject();
    return values;
  }

  private static List<Dependency> dependencies(JsonReader r) throws IOException {
    var values = new ArrayList<Dependency>();
    r.beginArray();
    String previous = "";
    while (r.hasNext()) {
      require(values.size() < 512);
      r.beginObject();
      key(r, "coordinate");
      String coordinate = string(r);
      require(coordinate.compareTo(previous) > 0);
      previous = coordinate;
      key(r, "paths");
      r.beginArray();
      var paths = new ArrayList<String>();
      while (r.hasNext()) {
        require(paths.size() < 3);
        paths.add(string(r));
      }
      r.endArray();
      r.endObject();
      values.add(new Dependency(coordinate, paths));
    }
    r.endArray();
    return values;
  }

  private static List<Artifact> artifacts(JsonReader r) throws IOException {
    var values = new ArrayList<Artifact>();
    r.beginArray();
    String previous = "";
    while (r.hasNext()) {
      require(values.size() < 2048);
      r.beginObject();
      key(r, "path");
      String path = string(r);
      require(path.compareTo(previous) > 0);
      previous = path;
      key(r, "size");
      long size = number(r);
      key(r, "sha256");
      String sha = string(r);
      r.endObject();
      values.add(new Artifact(path, size, sha));
    }
    r.endArray();
    return values;
  }

  private static List<SchemaHistoryAdmission.Row> migrations(JsonReader r) throws IOException {
    var values = new ArrayList<SchemaHistoryAdmission.Row>();
    r.beginArray();
    while (r.hasNext()) {
      require(values.size() < 1000);
      r.beginObject();
      key(r, "installedRank");
      int rank = integer(r);
      key(r, "version");
      @Nullable String version = nullableString(r);
      key(r, "type");
      String type = string(r);
      key(r, "script");
      String script = string(r);
      key(r, "checksum");
      @Nullable Integer checksum = nullableInteger(r);
      key(r, "success");
      require(r.peek() == JsonToken.BOOLEAN);
      boolean success = r.nextBoolean();
      r.endObject();
      values.add(new SchemaHistoryAdmission.Row(rank, version, type, script, checksum, success));
    }
    r.endArray();
    return values;
  }

  private static void key(JsonReader r, String expected) throws IOException {
    require(r.nextName().equals(expected));
  }

  private static String string(JsonReader r) throws IOException {
    require(r.peek() == JsonToken.STRING);
    return r.nextString();
  }

  private static @Nullable String nullableString(JsonReader r) throws IOException {
    if (r.peek() == JsonToken.NULL) {
      r.nextNull();
      return null;
    }
    return string(r);
  }

  private static @Nullable Integer nullableInteger(JsonReader r) throws IOException {
    if (r.peek() == JsonToken.NULL) {
      r.nextNull();
      return null;
    }
    return integer(r);
  }

  private static int integer(JsonReader r) throws IOException {
    long value = number(r);
    require(value >= Integer.MIN_VALUE && value <= Integer.MAX_VALUE);
    return (int) value;
  }

  private static long number(JsonReader r) throws IOException {
    require(r.peek() == JsonToken.NUMBER);
    String raw = r.nextString();
    require(raw.matches("0|-?[1-9][0-9]{0,18}"));
    return Long.parseLong(raw);
  }

  private void inventory() {
    var byPath = new HashMap<String, Artifact>();
    for (var a : artifacts) byPath.put(a.path(), a);
    require(
        byPath
            .keySet()
            .containsAll(Set.of("VERSION", "api/api.jar", "web/web.jar", "operations/batch.jar")));
    require(!byPath.containsKey("RELEASE-MANIFEST.json") && !byPath.containsKey("SHA256SUMS"));
    for (String path : byPath.keySet()) {
      int slash = path.indexOf('/');
      while (slash >= 0) {
        require(!byPath.containsKey(path.substring(0, slash)));
        slash = path.indexOf('/', slash + 1);
      }
    }
    var registered = new HashSet<String>();
    for (var dep : dependencies) {
      @Nullable Artifact first = null;
      for (String path : dep.paths()) {
        require(registered.add(path));
        var actual = byPath.get(path);
        if (actual == null) throw new IllegalArgumentException("missing release artifact");
        if (first == null) first = actual;
        else require(first.size() == actual.size() && first.sha256().equals(actual.sha256()));
      }
    }
    var actualLibs = new HashSet<String>();
    for (String path : byPath.keySet())
      if (path.matches("(api|web|operations)/lib/[^/]+")) {
        require(path.endsWith(".jar"));
        actualLibs.add(path);
      }
    require(registered.equals(actualLibs));
    for (String shared : List.of("protocol", "storage", "bootstrap")) {
      String coordinate =
          "dev.codex.schubert:schubert-nk-"
              + shared
              + ":"
              + Objects.requireNonNull(versions.get(shared));
      var match = dependencies.stream().filter(d -> d.coordinate().equals(coordinate)).toList();
      require(match.size() == 1);
      var roles = new HashSet<String>();
      for (String path : match.getFirst().paths())
        require(roles.add(path.substring(0, path.indexOf('/'))));
      require(
          roles.equals(
              shared.equals("protocol")
                  ? Set.of("api", "web")
                  : Set.of("api", "web", "operations")));
    }
    var sqlNames = new HashSet<String>();
    for (int i = 1; i < migrations.size(); i++)
      sqlNames.add("db/migration/" + migrations.get(i).script());
    var actualSql = new HashSet<String>();
    for (String path : byPath.keySet()) if (path.startsWith("db/migration/")) actualSql.add(path);
    require(sqlNames.equals(actualSql));
  }

  private static void requireToken(String value) {
    require(Objects.requireNonNull(value).matches("[A-Za-z0-9][A-Za-z0-9._-]{0,63}"));
  }

  private static void requireText(String value) {
    require(Objects.requireNonNull(value).matches("[\\x20-\\x7e]{1,128}"));
  }

  private static void requirePath(String value) {
    require(
        Objects.requireNonNull(value)
            .matches("[A-Za-z0-9][A-Za-z0-9._-]{0,200}(/[A-Za-z0-9][A-Za-z0-9._-]{0,200}){0,7}"));
  }

  private static void require(boolean valid) {
    if (!valid) throw new IllegalArgumentException("invalid release inventory");
  }

  String release() {
    return release;
  }

  Map<String, String> versions() {
    return Map.copyOf(versions);
  }

  Map<String, String> source() {
    return Map.copyOf(source);
  }

  Map<String, String> build() {
    return Map.copyOf(build);
  }

  Map<String, String> platform() {
    return Map.copyOf(platform);
  }

  List<Artifact> artifacts() {
    return List.copyOf(artifacts);
  }

  List<Dependency> dependencies() {
    return List.copyOf(dependencies);
  }

  List<SchemaHistoryAdmission.Row> migrations() {
    return List.copyOf(migrations);
  }
}
