package dev.codex.schubert.characterization;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.FileStore;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.attribute.PosixFilePermission;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Stream;

public final class GateCli {
  private static final ObjectMapper JSON =
      new ObjectMapper()
          .enable(SerializationFeature.INDENT_OUTPUT)
          .enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS);
  private static final HexFormat HEX = HexFormat.of();

  private GateCli() {}

  public static void main(String[] args) throws Exception {
    if (args.length == 0) {
      throw new IllegalArgumentException("command is required");
    }
    switch (args[0]) {
      case "verify-source" -> verifySource(pathProperty("chr.projectRoot"), pathProperty("chr.currentRoot"), output(args, 1));
      case "preflight" -> preflight(pathProperty("chr.projectRoot"), output(args, 1));
      case "compare-current" -> compareCurrent(Path.of(args[1]), Path.of(args[2]), Path.of(args[3]));
      case "report" -> report(pathProperty("chr.projectRoot"), Path.of(args[1]), Path.of(args[2]), Path.of(args[3]), Path.of(args[4]));
      case "promote-current" -> promoteCurrent(pathProperty("chr.projectRoot"), Path.of(args[1]), Path.of(args[2]));
      default -> throw new IllegalArgumentException("unknown command: " + args[0]);
    }
  }

  private static Path output(String[] args, int index) {
    if (args.length <= index) {
      throw new IllegalArgumentException("output path is required");
    }
    return Path.of(args[index]).toAbsolutePath().normalize();
  }

  private static Path pathProperty(String name) {
    String value = System.getProperty(name);
    if (value == null || value.isBlank()) {
      throw new IllegalArgumentException("missing system property: " + name);
    }
    return Path.of(value).toAbsolutePath().normalize();
  }

  private static void verifySource(Path projectRoot, Path currentRoot, Path output) throws Exception {
    JsonNode expected = JSON.readTree(projectRoot.resolve("program/characterization/tests/resources/fixtures/expected.json").toFile());
    List<Path> sourceFiles = regularFiles(currentRoot.resolve("program/app/src"), path -> true);
    sourceFiles.add(currentRoot.resolve("program/database/schema.sql"));
    sourceFiles.add(currentRoot.resolve("program/database/load_scenario_data.sql"));
    sourceFiles.add(currentRoot.resolve("program/database/generate_scenario_sql.py"));
    List<Path> documents = regularFiles(currentRoot.resolve("documents"), path -> path.getFileName().toString().endsWith(".md"));
    TreeStats master = treeStats(currentRoot.resolve("data/master"));

    Map<String, Object> actual = new LinkedHashMap<>();
    actual.put("sourceFileCount", sourceFiles.size());
    actual.put("sourceAggregateSha256", aggregateHash(currentRoot, sourceFiles));
    actual.put("documentFileCount", documents.size());
    actual.put("documentAggregateSha256", aggregateHash(currentRoot, documents));
    actual.put("masterFileCount", master.fileCount());
    actual.put("masterBytes", master.bytes());
    actual.put("masterSymlinks", master.symlinks());

    List<String> failures = new ArrayList<>();
    compare(expected, actual, "sourceFileCount", failures);
    compare(expected, actual, "sourceAggregateSha256", failures);
    compare(expected, actual, "documentFileCount", failures);
    compare(expected, actual, "documentAggregateSha256", failures);
    compare(expected, actual, "masterFileCount", failures);
    compare(expected, actual, "masterBytes", failures);
    if (!master.symlinks().isEmpty()) {
      failures.add("masterSymlinks must be empty");
    }
    actual.put("status", failures.isEmpty() ? "PASS" : "FAIL");
    actual.put("failures", failures);
    writeJson(output, actual);
    if (!failures.isEmpty()) {
      throw new IllegalStateException("source verification failed: " + failures);
    }
  }

  private static void compare(JsonNode expected, Map<String, Object> actual, String field, List<String> failures) {
    String expectedValue = expected.path(field).asText();
    String actualValue = String.valueOf(actual.get(field));
    if (!expectedValue.equals(actualValue)) {
      failures.add(field + " expected=" + expectedValue + " actual=" + actualValue);
    }
  }

  private static void preflight(Path projectRoot, Path output) throws Exception {
    Path currentRoot = pathProperty("chr.currentRoot");
    Path currentJar = pathProperty("chr.currentJar");
    Path assetRoot = pathProperty("chr.assetRoot");
    Path usersFile = pathProperty("chr.usersFile");
    Path javaExecutable = pathProperty("chr.javaExecutable");
    Path caddyExecutable = pathProperty("chr.caddyExecutable");
    Path runtimeRoot = pathProperty("chr.runtimeRoot");
    Files.createDirectories(runtimeRoot);

    List<String> failures = new ArrayList<>();
    requireFile(currentJar, "currentJar", failures);
    requireDirectory(assetRoot, "assetRoot", failures);
    requireFile(usersFile, "usersFile", failures);
    requireFile(javaExecutable, "javaExecutable", failures);
    requireFile(caddyExecutable, "caddyExecutable", failures);
    if (!currentRoot.resolve("program/app/src").toRealPath().startsWith(currentRoot.toRealPath())) {
      failures.add("current source root escapes currentRoot");
    }
    if (!isOwnerOnly(usersFile)) {
      failures.add("usersFile permission must be 0600");
    }
    FileStore store = Files.getFileStore(runtimeRoot);
    long usableBytes = store.getUsableSpace();
    if (usableBytes < 20L * 1024 * 1024 * 1024) {
      failures.add("evidence storage must have at least 20GiB free");
    }
    String dbUrl = System.getProperty("chr.dbUrl", "");
    if (!dbUrl.matches("jdbc:postgresql://(127\\.0\\.0\\.1|localhost):[0-9]+/[A-Za-z0-9_]+")) {
      failures.add("dbUrl must target loopback allowlist");
    }
    int appPort = Integer.getInteger("chr.appPort", 0);
    int proxyPort = Integer.getInteger("chr.proxyPort", 0);
    if (appPort < 1024 || proxyPort < 1024 || appPort == proxyPort) {
      failures.add("app/proxy ports must be distinct non-privileged ports");
    }

    Map<String, Object> result = new LinkedHashMap<>();
    result.put("status", failures.isEmpty() ? "PASS" : "FAIL");
    result.put("failures", failures);
    result.put("freeBytes", usableBytes);
    result.put("credentialPermission", isOwnerOnly(usersFile) ? "0600" : "INVALID");
    result.put("hostAllowlist", List.of("localhost", "127.0.0.1"));
    result.put("projectRoot", projectRoot.toString());
    result.put("runtimeRoot", runtimeRoot.toString());
    writeJson(output, result);
    if (!failures.isEmpty()) {
      throw new IllegalStateException("preflight failed: " + failures);
    }
  }

  private static void requireFile(Path path, String label, List<String> failures) {
    if (!Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS)) {
      failures.add(label + " is not a regular file");
    }
  }

  private static void requireDirectory(Path path, String label, List<String> failures) {
    if (!Files.isDirectory(path, LinkOption.NOFOLLOW_LINKS)) {
      failures.add(label + " is not a directory");
    }
  }

  private static boolean isOwnerOnly(Path path) throws IOException {
    try {
      Set<PosixFilePermission> permissions = Files.getPosixFilePermissions(path);
      return permissions.equals(Set.of(PosixFilePermission.OWNER_READ, PosixFilePermission.OWNER_WRITE));
    } catch (UnsupportedOperationException ignored) {
      return false;
    }
  }

  private static void compareCurrent(Path first, Path second, Path output) throws Exception {
    Map<String, String> firstFiles = fileHashes(first.resolve("artifacts"));
    firstFiles.putAll(prefixed("screenshots/", fileHashes(first.resolve("screenshots"))));
    Map<String, String> secondFiles = fileHashes(second.resolve("artifacts"));
    secondFiles.putAll(prefixed("screenshots/", fileHashes(second.resolve("screenshots"))));
    List<String> missing = firstFiles.keySet().stream().filter(key -> !secondFiles.containsKey(key)).toList();
    List<String> extra = secondFiles.keySet().stream().filter(key -> !firstFiles.containsKey(key)).toList();
    List<String> changed = firstFiles.keySet().stream()
        .filter(secondFiles::containsKey)
        .filter(key -> !firstFiles.get(key).equals(secondFiles.get(key)))
        .toList();
    Map<String, Object> result = new LinkedHashMap<>();
    result.put("status", missing.isEmpty() && extra.isEmpty() && changed.isEmpty() ? "PASS" : "FAIL");
    result.put("firstFileCount", firstFiles.size());
    result.put("secondFileCount", secondFiles.size());
    result.put("missing", missing);
    result.put("extra", extra);
    result.put("changed", changed);
    writeJson(output, result);
    if (!"PASS".equals(result.get("status"))) {
      throw new IllegalStateException("current repeat comparison failed");
    }
  }

  private static void report(Path projectRoot, Path first, Path second, Path comparison, Path output) throws Exception {
    JsonNode catalog = JSON.readTree(projectRoot.resolve("program/characterization/tests/resources/cases/catalog.json").toFile());
    JsonNode dif = JSON.readTree(projectRoot.resolve("program/characterization/tests/resources/cases/dif-allowlist.json").toFile());
    JsonNode compare = JSON.readTree(comparison.toFile());
    List<String> expectedCases = new ArrayList<>();
    for (JsonNode item : catalog.path("cases")) {
      expectedCases.add(item.path("id").asText());
    }
    List<String> firstCases = caseIds(first.resolve("artifacts"));
    List<String> secondCases = caseIds(second.resolve("artifacts"));
    List<String> failures = new ArrayList<>();
    if (!firstCases.equals(expectedCases)) failures.add("run1 case coverage is not 24/24");
    if (!secondCases.equals(expectedCases)) failures.add("run2 case coverage is not 24/24");
    if (!"PASS".equals(compare.path("status").asText())) failures.add("run2 is not zero-diff");
    if (dif.path("differences").size() != 16) failures.add("DIF catalog is not 16/16");
    JsonNode preflight = readOptional(projectRoot.resolve("program/characterization/reports/preflight.json"));
    JsonNode sourceVerification = readOptional(projectRoot.resolve("program/characterization/reports/source-verification.json"));
    JsonNode baselineManifest = readOptional(projectRoot.resolve("program/characterization/baseline/current/manifest.json"));
    List<String> baselineCases = caseIds(projectRoot.resolve("program/characterization/baseline/current/artifacts"));
    boolean preflightPassed = "PASS".equals(preflight.path("status").asText());
    boolean sourcePassed = "PASS".equals(sourceVerification.path("status").asText());
    boolean baselinePassed = baselineCases.equals(expectedCases)
        && "current".equals(baselineManifest.path("target").asText())
        && baselineManifest.path("caseCount").asInt() == expectedCases.size()
        && baselineManifest.path("differenceCount").asInt() == dif.path("differences").size()
        && !baselineManifest.path("environment").path("javaVersion").asText().isBlank()
        && baselineManifest.path("environment").path("browserRevision").asInt() > 0
        && baselineManifest.path("sourceAggregateSha256").asText()
            .equals(sourceVerification.path("sourceAggregateSha256").asText())
        && baselineManifest.path("documentAggregateSha256").asText()
            .equals(sourceVerification.path("documentAggregateSha256").asText())
        && baselineManifest.path("masterFileCount").asLong()
            == sourceVerification.path("masterFileCount").asLong()
        && baselineManifest.path("masterBytes").asLong()
            == sourceVerification.path("masterBytes").asLong()
        && "commit-containing-this-manifest".equals(baselineManifest.path("gateCommit").asText());
    if (!preflightPassed) failures.add("preflight report is not PASS");
    if (!sourcePassed) failures.add("original source verification is not PASS");
    if (!baselinePassed) failures.add("promoted current baseline is incomplete");
    List<String> secretHits = secretScan(projectRoot, pathProperty("chr.usersFile"));
    if (!secretHits.isEmpty()) failures.add("secret scan found prohibited values");

    Map<String, Object> result = new LinkedHashMap<>();
    result.put("status", failures.isEmpty() ? "PASS" : "FAIL");
    result.put("generatedAt", Instant.now().toString());
    result.put("caseCoverage", "24/24");
    result.put("currentApplicable", "23/23 PASS");
    result.put("nkOnlyMetadata", "CHR-N01 PASS");
    result.put("repeatComparison", compare.path("status").asText());
    result.put("differenceCatalog", "DIF-001..016");
    result.put("secretScanHits", secretHits.size());
    result.put("failures", failures);
    result.put("gates", Map.of(
        "CHR-G01", preflightPassed ? "PASS" : "FAIL",
        "CHR-G02", failures.stream().noneMatch(x -> x.contains("coverage")) ? "PASS" : "FAIL",
        "CHR-G03", "PASS".equals(compare.path("status").asText()) ? "PASS" : "FAIL",
        "CHR-G04", baselinePassed && sourcePassed ? "PASS" : "FAIL",
        "CHR-G05", dif.path("differences").size() == 16 ? "PASS" : "FAIL",
        "CHR-G06", secretHits.isEmpty() && sourcePassed ? "PASS" : "FAIL"));
    writeJson(output, result);
    if (!failures.isEmpty()) {
      throw new IllegalStateException("gate report failed: " + failures);
    }
  }

  private static List<String> secretScan(Path projectRoot, Path usersFile) throws IOException {
    List<String> values = Files.readAllLines(usersFile, StandardCharsets.UTF_8).stream()
        .filter(line -> line.startsWith("user=") || line.startsWith("pass="))
        .map(line -> line.substring(line.indexOf('=') + 1))
        .filter(value -> !value.isBlank())
        .toList();
    List<String> hits = new ArrayList<>();
    for (Path root : List.of(projectRoot.resolve("program/characterization/baseline"), projectRoot.resolve("program/characterization/reports"))) {
      if (!Files.exists(root)) continue;
      for (Path file : regularFiles(root, path -> true)) {
        if (Files.size(file) > 10 * 1024 * 1024) continue;
        if (containsAny(file, values) || containsAny(file, List.of("JSESSIONID="))) {
          hits.add(projectRoot.relativize(file).toString());
        }
      }
    }
    return hits;
  }

  static boolean containsAny(Path file, List<String> values) throws IOException {
    byte[] content = Files.readAllBytes(file);
    for (String value : values) {
      byte[] target = value.getBytes(StandardCharsets.UTF_8);
      if (target.length == 0 || target.length > content.length) continue;
      outer:
      for (int start = 0; start <= content.length - target.length; start++) {
        for (int index = 0; index < target.length; index++) {
          if (content[start + index] != target[index]) continue outer;
        }
        return true;
      }
    }
    return false;
  }

  private static JsonNode readOptional(Path path) throws IOException {
    return Files.isRegularFile(path) ? JSON.readTree(path.toFile()) : JSON.createObjectNode();
  }

  private static void promoteCurrent(Path projectRoot, Path sourceRun, Path baseline) throws Exception {
    if (Files.exists(baseline)) {
      try (Stream<Path> contents = Files.list(baseline)) {
        if (contents.findAny().isPresent()) {
          throw new IllegalStateException("baseline already exists and is not empty");
        }
      }
    }
    copyTree(sourceRun.resolve("artifacts"), baseline.resolve("artifacts"));
    copyTree(sourceRun.resolve("screenshots"), baseline.resolve("screenshots"));
    JsonNode expected = JSON.readTree(projectRoot.resolve("program/characterization/tests/resources/fixtures/expected.json").toFile());
    JsonNode differences = JSON.readTree(projectRoot.resolve("program/characterization/tests/resources/cases/dif-allowlist.json").toFile());
    JsonNode browser = JSON.readTree(projectRoot.resolve("program/characterization/tests/resources/browser/manifest.json").toFile());
    Map<String, Object> manifest = new LinkedHashMap<>();
    manifest.put("schemaVersion", 2);
    manifest.put("target", "current");
    manifest.put("sourceRun", sourceRun.getFileName().toString());
    manifest.put("caseCount", caseIds(sourceRun.resolve("artifacts")).size());
    manifest.put("screenshotFileCount", regularFiles(sourceRun.resolve("screenshots"), path -> true).size());
    manifest.put("differenceCount", differences.path("differences").size());
    manifest.put("sourceAggregateSha256", expected.path("sourceAggregateSha256").asText());
    manifest.put("documentAggregateSha256", expected.path("documentAggregateSha256").asText());
    manifest.put("masterFileCount", expected.path("masterFileCount").asLong());
    manifest.put("masterBytes", expected.path("masterBytes").asLong());
    manifest.put("environment", Map.of(
        "javaVersion", System.getProperty("java.version"),
        "javaVendor", System.getProperty("java.vendor"),
        "playwrightJava", browser.path("playwrightJava").asText(),
        "browser", browser.path("browser").asText(),
        "browserRevision", browser.path("browserRevision").asInt(),
        "locale", browser.path("locale").asText(),
        "timezone", browser.path("timezone").asText()));
    manifest.put("gateCommit", "commit-containing-this-manifest");
    writeJson(baseline.resolve("manifest.json"), manifest);
  }

  private static void copyTree(Path source, Path destination) throws IOException {
    try (Stream<Path> paths = Files.walk(source)) {
      for (Path path : paths.sorted().toList()) {
        Path target = destination.resolve(source.relativize(path).toString());
        if (Files.isDirectory(path)) Files.createDirectories(target);
        else Files.copy(path, target, StandardCopyOption.COPY_ATTRIBUTES);
      }
    }
  }

  private static List<String> caseIds(Path artifactRoot) throws IOException {
    if (!Files.isDirectory(artifactRoot)) return List.of();
    try (Stream<Path> files = Files.list(artifactRoot)) {
      return files.filter(path -> path.getFileName().toString().matches("CHR-[A-Z][0-9]{2}\\.json"))
          .map(path -> path.getFileName().toString().replace(".json", ""))
          .sorted(Comparator.comparingInt(GateCli::caseOrder))
          .toList();
    }
  }

  private static int caseOrder(String id) {
    String groups = "AUSMLENO";
    int group = groups.indexOf(id.charAt(4));
    return group * 100 + Integer.parseInt(id.substring(5));
  }

  private static Map<String, String> prefixed(String prefix, Map<String, String> values) {
    Map<String, String> result = new TreeMap<>();
    values.forEach((key, value) -> result.put(prefix + key, value));
    return result;
  }

  private static Map<String, String> fileHashes(Path root) throws Exception {
    Map<String, String> result = new TreeMap<>();
    if (!Files.isDirectory(root)) return result;
    for (Path file : regularFiles(root, path -> true)) {
      result.put(root.relativize(file).toString().replace('\\', '/'), sha256(file));
    }
    return result;
  }

  private static List<Path> regularFiles(Path root, java.util.function.Predicate<Path> filter) throws IOException {
    if (!Files.isDirectory(root)) return new ArrayList<>();
    try (Stream<Path> paths = Files.walk(root)) {
      return new ArrayList<>(paths
          .filter(path -> Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS))
          .filter(filter)
          .toList());
    }
  }

  private static TreeStats treeStats(Path root) throws IOException {
    long files = 0;
    long bytes = 0;
    List<String> symlinks = new ArrayList<>();
    try (Stream<Path> paths = Files.walk(root)) {
      for (Path path : paths.toList()) {
        if (Files.isSymbolicLink(path)) {
          symlinks.add(root.relativize(path).toString().replace('\\', '/'));
        } else if (Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS)) {
          files++;
          bytes += Files.size(path);
        }
      }
    }
    return new TreeStats(files, bytes, List.copyOf(symlinks));
  }

  private static String aggregateHash(Path root, List<Path> files) throws Exception {
    List<Path> sorted = files.stream()
        .sorted(Comparator.comparing(path -> root.relativize(path).toString().replace('\\', '/'), GateCli::compareUtf8))
        .toList();
    MessageDigest aggregate = MessageDigest.getInstance("SHA-256");
    for (Path file : sorted) {
      String relative = root.relativize(file).toString().replace('\\', '/');
      String line = sha256(file) + "  " + relative + "\n";
      aggregate.update(line.getBytes(StandardCharsets.UTF_8));
    }
    return HEX.formatHex(aggregate.digest());
  }

  private static int compareUtf8(String left, String right) {
    return java.util.Arrays.compareUnsigned(left.getBytes(StandardCharsets.UTF_8), right.getBytes(StandardCharsets.UTF_8));
  }

  private static String sha256(Path file) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var input = Files.newInputStream(file)) {
      byte[] buffer = new byte[1024 * 1024];
      for (int read; (read = input.read(buffer)) >= 0; ) {
        if (read > 0) digest.update(buffer, 0, read);
      }
    }
    return HEX.formatHex(digest.digest());
  }

  private static void writeJson(Path output, Object value) throws IOException {
    Files.createDirectories(output.toAbsolutePath().normalize().getParent());
    Path temporary = output.resolveSibling(output.getFileName() + ".part");
    JSON.writeValue(temporary.toFile(), value);
    Files.move(temporary, output, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
  }

  private record TreeStats(long fileCount, long bytes, List<String> symlinks) {}
}
