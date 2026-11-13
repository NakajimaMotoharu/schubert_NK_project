package dev.codex.schubert.characterization;

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
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Stream;

public final class GateCli {
  private static final String VALUE_CHR_PROJECTROOT = "chr.projectRoot";
  private static final String FIELD_SOURCEAGGREGATESHA256 = "sourceAggregateSha256";
  private static final String FIELD_DOCUMENTAGGREGATESHA256 = "documentAggregateSha256";
  private static final String FIELD_MASTERFILECOUNT = "masterFileCount";
  private static final String FIELD_MASTERBYTES = "masterBytes";
  private static final String FIELD_STATUS = "status";
  private static final String VALUE_PASS = "PASS";
  private static final String VALUE_FAIL = "FAIL";
  private static final String FIELD_ARTIFACTS = "artifacts";
  private static final String FIELD_SCREENSHOTS = "screenshots";

  private static final int EXPECTED_REPEAT_FILE_COUNT = 28;
  private static final ObjectMapper JSON =
      new ObjectMapper()
          .enable(SerializationFeature.INDENT_OUTPUT)
          .enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS);
  private static final HexFormat HEX = HexFormat.of();
  private static final Set<Path> ACTIVE_OUTPUTS = ConcurrentHashMap.newKeySet();

  private GateCli() {}

  public static void main(String[] args) throws IOException, NoSuchAlgorithmException {
    if (args.length == 0) {
      throw new IllegalArgumentException("command is required");
    }
    switch (args[0]) {
      case "verify-source" ->
          verifySource(
              pathProperty(VALUE_CHR_PROJECTROOT),
              pathProperty("chr.currentRoot"),
              output(args, 1));
      case "preflight" -> preflight(pathProperty(VALUE_CHR_PROJECTROOT), output(args, 1));
      case "compare-current" ->
          compareCurrent(
              argument(args, 1, "first run"), argument(args, 2, "second run"), output(args, 3));
      case "compare-nk" ->
          compareNk(
              pathProperty(VALUE_CHR_PROJECTROOT),
              argument(args, 1, "current artifacts"),
              argument(args, 2, "NK artifacts"),
              argument(args, 3, "DIF observations"),
              output(args, 4));
      case "report" ->
          report(
              pathProperty(VALUE_CHR_PROJECTROOT),
              argument(args, 1, "first run"),
              argument(args, 2, "second run"),
              argument(args, 3, "comparison"),
              output(args, 4));
      case "promote-current" ->
          promoteCurrent(
              pathProperty(VALUE_CHR_PROJECTROOT),
              argument(args, 1, "source run"),
              argument(args, 2, "baseline"));
      default -> throw new IllegalArgumentException("unknown command: " + args[0]);
    }
  }

  private static Path argument(String[] args, int index, String label) {
    if (args.length <= index) {
      throw new IllegalArgumentException(label + " path is required");
    }
    return Path.of(args[index]).toAbsolutePath().normalize();
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

  static void verifySource(Path projectRoot, Path currentRoot, Path output)
      throws IOException, NoSuchAlgorithmException {
    JsonNode expected =
        JSON.readTree(
            projectRoot
                .resolve("program/characterization/tests/resources/fixtures/expected.json")
                .toFile());
    List<Path> sourceFiles = regularFiles(currentRoot.resolve("program/app/src"), path -> true);
    sourceFiles.add(currentRoot.resolve("program/database/schema.sql"));
    sourceFiles.add(currentRoot.resolve("program/database/load_scenario_data.sql"));
    sourceFiles.add(currentRoot.resolve("program/database/generate_scenario_sql.py"));
    List<Path> documents =
        regularFiles(
            currentRoot.resolve("documents"),
            path -> ArtifactComparator.requiredArtifactFileName(path).endsWith(".md"));
    TreeStats master = treeStats(currentRoot.resolve("data/master"));

    Map<String, Object> actual = new LinkedHashMap<>();
    actual.put("sourceFileCount", sourceFiles.size());
    actual.put(FIELD_SOURCEAGGREGATESHA256, aggregateHash(currentRoot, sourceFiles));
    actual.put("documentFileCount", documents.size());
    actual.put(FIELD_DOCUMENTAGGREGATESHA256, aggregateHash(currentRoot, documents));
    actual.put(FIELD_MASTERFILECOUNT, master.fileCount());
    actual.put(FIELD_MASTERBYTES, master.bytes());
    actual.put("masterSymlinks", master.symlinks());

    List<String> failures = new ArrayList<>();
    compare(expected, actual, "sourceFileCount", failures);
    compare(expected, actual, FIELD_SOURCEAGGREGATESHA256, failures);
    compare(expected, actual, "documentFileCount", failures);
    compare(expected, actual, FIELD_DOCUMENTAGGREGATESHA256, failures);
    compare(expected, actual, FIELD_MASTERFILECOUNT, failures);
    compare(expected, actual, FIELD_MASTERBYTES, failures);
    if (!master.symlinks().isEmpty()) {
      failures.add("masterSymlinks must be empty");
    }
    actual.put(FIELD_STATUS, failures.isEmpty() ? VALUE_PASS : VALUE_FAIL);
    actual.put("failures", failures);
    writeJson(output, actual);
    if (!failures.isEmpty()) {
      throw new IllegalStateException("source verification failed: " + failures);
    }
  }

  private static void compare(
      JsonNode expected, Map<String, Object> actual, String field, List<String> failures) {
    String expectedValue = expected.path(field).asText();
    String actualValue = String.valueOf(actual.get(field));
    if (!expectedValue.equals(actualValue)) {
      failures.add(field + " expected=" + expectedValue + " actual=" + actualValue);
    }
  }

  static void preflight(Path projectRoot, Path output)
      throws IOException, NoSuchAlgorithmException {
    Path currentRoot = pathProperty("chr.currentRoot");
    Path currentJar = pathProperty("chr.currentJar");
    Path assetRoot = pathProperty("chr.assetRoot");
    Path usersFile = pathProperty("chr.usersFile");
    Path javaExecutable = pathProperty("chr.javaExecutable");
    Path caddyExecutable = pathProperty("chr.caddyExecutable");
    Path runtimeRoot = pathProperty("chr.runtimeRoot");
    Path pgCtl = pathProperty("chr.pgCtl");
    Path pgData = pathProperty("chr.pgData");
    Path pgLog = pathProperty("chr.pgLog");
    Path pgSocket = pathProperty("chr.pgSocket");
    Path logParent = pgLog.getParent();
    if (logParent == null) {
      throw new IllegalArgumentException("chr.pgLog must name a file below a directory");
    }
    Files.createDirectories(runtimeRoot);
    Files.createDirectories(logParent);
    Files.createDirectories(pgSocket);

    List<String> failures = new ArrayList<>();
    requireFile(currentJar, "currentJar", failures);
    requireDirectory(assetRoot, "assetRoot", failures);
    requireFile(usersFile, "usersFile", failures);
    requireFile(javaExecutable, "javaExecutable", failures);
    requireFile(caddyExecutable, "caddyExecutable", failures);
    requireFile(pgCtl, "pgCtl", failures);
    requireDirectory(pgData, "pgData", failures);
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
    result.put(FIELD_STATUS, failures.isEmpty() ? VALUE_PASS : VALUE_FAIL);
    result.put("failures", failures);
    result.put("freeBytes", usableBytes);
    result.put("credentialPermission", isOwnerOnly(usersFile) ? "0600" : "INVALID");
    result.put("hostAllowlist", List.of("localhost", "127.0.0.1"));
    result.put("projectRoot", projectRoot.toString());
    result.put("runtimeRoot", runtimeRoot.toString());
    result.put("postgresControl", pgCtl.toString());
    result.put("postgresData", pgData.toString());
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
    Set<PosixFilePermission> permissions = Files.getPosixFilePermissions(path);
    return permissions.equals(
        Set.of(PosixFilePermission.OWNER_READ, PosixFilePermission.OWNER_WRITE));
  }

  static void compareCurrent(Path first, Path second, Path output)
      throws IOException, NoSuchAlgorithmException {
    Map<String, String> firstFiles = fileHashes(first.resolve(FIELD_ARTIFACTS));
    firstFiles.putAll(prefixed("screenshots/", fileHashes(first.resolve(FIELD_SCREENSHOTS))));
    addRunReportHashes(first, firstFiles);
    Map<String, String> secondFiles = fileHashes(second.resolve(FIELD_ARTIFACTS));
    secondFiles.putAll(prefixed("screenshots/", fileHashes(second.resolve(FIELD_SCREENSHOTS))));
    addRunReportHashes(second, secondFiles);
    List<String> missing =
        firstFiles.keySet().stream().filter(key -> !secondFiles.containsKey(key)).toList();
    List<String> extra =
        secondFiles.keySet().stream().filter(key -> !firstFiles.containsKey(key)).toList();
    List<String> changed =
        firstFiles.keySet().stream()
            .filter(secondFiles::containsKey)
            .filter(key -> !firstFiles.get(key).equals(secondFiles.get(key)))
            .toList();
    Map<String, Object> result = new LinkedHashMap<>();
    boolean complete =
        firstFiles.size() == EXPECTED_REPEAT_FILE_COUNT
            & secondFiles.size() == EXPECTED_REPEAT_FILE_COUNT;
    boolean unchanged = missing.isEmpty() & extra.isEmpty() & changed.isEmpty();
    result.put(FIELD_STATUS, complete & unchanged ? VALUE_PASS : VALUE_FAIL);
    result.put("expectedFileCount", EXPECTED_REPEAT_FILE_COUNT);
    result.put("firstFileCount", firstFiles.size());
    result.put("secondFileCount", secondFiles.size());
    result.put("missing", missing);
    result.put("extra", extra);
    result.put("changed", changed);
    writeJson(output, result);
    if (!VALUE_PASS.equals(result.get(FIELD_STATUS))) {
      throw new IllegalStateException("current repeat comparison failed");
    }
  }

  static void compareNk(
      Path projectRoot, Path currentArtifacts, Path nkArtifacts, Path observations, Path output)
      throws IOException {
    ArtifactComparator.ComparisonResult result =
        ArtifactComparator.compare(projectRoot, currentArtifacts, nkArtifacts, observations);
    writeJson(output, result);
    if (!result.passed()) {
      throw new IllegalStateException("NK artifact comparison failed: " + result.failures());
    }
  }

  private static void addRunReportHashes(Path run, Map<String, String> hashes)
      throws IOException, NoSuchAlgorithmException {
    for (String name : List.of("inventory.json", "supplemental.json")) {
      Path report = run.resolve(name);
      if (Files.isRegularFile(report, LinkOption.NOFOLLOW_LINKS)) {
        hashes.put(name, sha256(report));
      }
    }
  }

  static void report(Path projectRoot, Path first, Path second, Path comparison, Path output)
      throws IOException, NoSuchAlgorithmException {
    JsonNode compare = JSON.readTree(comparison.toFile());
    GateContractValidator.ValidationResult validation =
        GateContractValidator.validate(projectRoot, first, second, comparison);
    List<String> failures = new ArrayList<>(validation.failures());
    List<String> secretHits = secretScan(projectRoot, pathProperty("chr.usersFile"));
    if (!secretHits.isEmpty()) failures.add("SECRET_SCAN");

    boolean g01 =
        noneMatch(
            validation.failures(),
            "CONTRACT_",
            "SCHEMA_",
            "CATALOG_",
            "BROWSER_",
            "REQ_",
            "PREFLIGHT_");
    boolean g02 = noneMatch(validation.failures(), "run1_", "run2_");
    boolean g03 = noneMatch(validation.failures(), "COMPARE_", "INVENTORY_REPEAT_DIFF");
    boolean g04 =
        noneMatch(
            validation.failures(),
            "SOURCE_",
            "run1_INVENTORY_",
            "run2_INVENTORY_",
            "BASELINE_",
            "REVIEW_");
    boolean g05 = noneMatch(validation.failures(), "DIF_", "DIF-");
    boolean g06 =
        secretHits.isEmpty() && noneMatch(validation.failures(), "SOURCE_", "BASELINE_", "REVIEW_");

    Map<String, Object> result = new LinkedHashMap<>();
    result.put(FIELD_STATUS, failures.isEmpty() ? VALUE_PASS : VALUE_FAIL);
    result.put("generatedAt", Instant.now().toString());
    result.put("caseCoverage", g02 ? "24/24 PASS" : VALUE_FAIL);
    result.put("currentApplicable", g02 ? "23/23 PASS" : VALUE_FAIL);
    result.put("nkOnlyMetadata", g02 ? "CHR-N01 PASS" : VALUE_FAIL);
    result.put("repeatComparison", compare.path(FIELD_STATUS).asText());
    result.put("differenceCatalog", "DIF-001..016");
    result.put("secretScanHits", secretHits.size());
    result.put("contractMetrics", validation.metrics());
    result.put("failures", failures);
    result.put(
        "gates",
        Map.of(
            "CHR-G01", g01 ? VALUE_PASS : VALUE_FAIL,
            "CHR-G02", g02 ? VALUE_PASS : VALUE_FAIL,
            "CHR-G03", g03 ? VALUE_PASS : VALUE_FAIL,
            "CHR-G04", g04 ? VALUE_PASS : VALUE_FAIL,
            "CHR-G05", g05 ? VALUE_PASS : VALUE_FAIL,
            "CHR-G06", g06 ? VALUE_PASS : VALUE_FAIL));
    writeJson(output, result);
    if (!failures.isEmpty()) {
      throw new IllegalStateException("gate report failed: " + failures);
    }
  }

  private static boolean noneMatch(List<String> failures, String... prefixes) {
    return failures.stream()
        .noneMatch(failure -> java.util.Arrays.stream(prefixes).anyMatch(failure::startsWith));
  }

  static List<String> secretScan(Path projectRoot, Path usersFile) throws IOException {
    List<String> values =
        Files.readAllLines(usersFile, StandardCharsets.UTF_8).stream()
            .filter(line -> line.startsWith("user=") || line.startsWith("pass="))
            .map(line -> line.substring(line.indexOf('=') + 1))
            .filter(value -> !value.isBlank())
            .toList();
    List<String> hits = new ArrayList<>();
    for (Path root :
        List.of(
            projectRoot.resolve("program/characterization/baseline"),
            projectRoot.resolve("program/characterization/reports"))) {
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

  /** SS355 / PT-CHR-NUM001..005: pure numeric metadata, no publication or permission grant. */
  static BaselineNumbers baselineNumericMetadata(JsonNode expected, JsonNode browser) {
    if (expected == null || browser == null) {
      throw new IllegalArgumentException("baseline numeric documents are required");
    }
    return new BaselineNumbers(
        baselineLong(expected.path(FIELD_MASTERFILECOUNT)),
        baselineLong(expected.path(FIELD_MASTERBYTES)),
        baselineInt(browser.path("browserRevision")));
  }

  private static long baselineLong(JsonNode value) {
    if (!value.isIntegralNumber() || !value.canConvertToLong()) {
      throw new IllegalArgumentException("baseline numeric field must be a representable integer");
    }
    return value.longValue();
  }

  private static int baselineInt(JsonNode value) {
    if (!value.isIntegralNumber() || !value.canConvertToInt()) {
      throw new IllegalArgumentException("baseline numeric field must be a representable integer");
    }
    return value.intValue();
  }

  record BaselineNumbers(long masterFileCount, long masterBytes, int browserRevision) {
    BaselineNumbers {
      if (masterFileCount < 0 || masterBytes < 0 || browserRevision < 1) {
        throw new IllegalArgumentException("invalid baseline numeric metadata");
      }
    }
  }

  static void promoteCurrent(Path projectRoot, Path sourceRun, Path baseline)
      throws IOException, NoSuchAlgorithmException {
    if (sourceRun == null)
      throw new IllegalArgumentException("sourceRun must name a run directory");
    Path runName = sourceRun.getFileName();
    if (runName == null) throw new IllegalArgumentException("sourceRun must name a run directory");
    String gateCommit = System.getProperty("chr.gateCommit", "");
    if (!gateCommit.matches("[0-9a-f]{7,40}")) {
      throw new IllegalArgumentException(
          "chr.gateCommit must be a 7 to 40 character lowercase Git commit");
    }
    if (Files.exists(baseline)) {
      try (Stream<Path> contents = Files.list(baseline)) {
        if (contents.findAny().isPresent()) {
          throw new IllegalStateException("baseline already exists and is not empty");
        }
      }
    }
    JsonNode expected =
        JSON.readTree(
            projectRoot
                .resolve("program/characterization/tests/resources/fixtures/expected.json")
                .toFile());
    JsonNode differences =
        JSON.readTree(
            projectRoot
                .resolve("program/characterization/tests/resources/cases/dif-allowlist.json")
                .toFile());
    JsonNode browser =
        JSON.readTree(
            projectRoot
                .resolve("program/characterization/tests/resources/browser/manifest.json")
                .toFile());
    BaselineNumbers numbers = baselineNumericMetadata(expected, browser);
    Map<String, Object> manifest = new LinkedHashMap<>();
    manifest.put("schemaVersion", 2);
    manifest.put("target", "current");
    manifest.put("sourceRun", runName.toString());
    manifest.put("caseCount", caseIds(sourceRun.resolve(FIELD_ARTIFACTS)).size());
    manifest.put(
        "screenshotFileCount",
        regularFiles(sourceRun.resolve(FIELD_SCREENSHOTS), path -> true).size());
    manifest.put("differenceCount", differences.path("differences").size());
    manifest.put(FIELD_SOURCEAGGREGATESHA256, expected.path(FIELD_SOURCEAGGREGATESHA256).asText());
    manifest.put(
        FIELD_DOCUMENTAGGREGATESHA256, expected.path(FIELD_DOCUMENTAGGREGATESHA256).asText());
    manifest.put(FIELD_MASTERFILECOUNT, numbers.masterFileCount());
    manifest.put(FIELD_MASTERBYTES, numbers.masterBytes());
    manifest.put(
        "environment",
        Map.of(
            "javaVersion", System.getProperty("java.version"),
            "javaVendor", System.getProperty("java.vendor"),
            "playwrightJava", browser.path("playwrightJava").asText(),
            "browser", browser.path("browser").asText(),
            "browserRevision", numbers.browserRevision(),
            "locale", browser.path("locale").asText(),
            "timezone", browser.path("timezone").asText()));
    manifest.put("gateCommit", gateCommit);
    copyTree(sourceRun.resolve(FIELD_ARTIFACTS), baseline.resolve(FIELD_ARTIFACTS));
    copyTree(sourceRun.resolve(FIELD_SCREENSHOTS), baseline.resolve(FIELD_SCREENSHOTS));
    writeJson(baseline.resolve("manifest.json"), manifest);
  }

  private static void copyTree(Path source, Path destination) throws IOException {
    try (Stream<Path> paths = Files.walk(source)) {
      for (Path path : paths.sorted().toList()) {
        if (Files.isSymbolicLink(path)) {
          throw new IOException("symbolic link is not allowed in baseline source: " + path);
        }
        Path target = destination.resolve(source.relativize(path).toString());
        if (Files.isDirectory(path, LinkOption.NOFOLLOW_LINKS)) Files.createDirectories(target);
        else Files.copy(path, target, StandardCopyOption.COPY_ATTRIBUTES);
      }
    }
  }

  static List<String> caseIds(Path artifactRoot) throws IOException {
    if (!Files.isDirectory(artifactRoot)) return List.of();
    try (Stream<Path> files = Files.list(artifactRoot)) {
      return files
          .filter(
              path ->
                  ArtifactComparator.requiredArtifactFileName(path)
                      .matches("CHR-[A-Z][0-9]{2}\\.json"))
          .map(path -> ArtifactComparator.requiredArtifactFileName(path).replace(".json", ""))
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

  static Map<String, String> fileHashes(Path root) throws IOException, NoSuchAlgorithmException {
    Map<String, String> result = new TreeMap<>();
    if (!Files.isDirectory(root)) return result;
    for (Path file : regularFiles(root, path -> true)) {
      result.put(root.relativize(file).toString().replace('\\', '/'), sha256(file));
    }
    return result;
  }

  static List<Path> regularFiles(Path root, java.util.function.Predicate<Path> filter)
      throws IOException {
    if (!Files.isDirectory(root)) return new ArrayList<>();
    try (Stream<Path> paths = Files.walk(root)) {
      return new ArrayList<>(
          paths
              .filter(path -> Files.isRegularFile(path, LinkOption.NOFOLLOW_LINKS))
              .filter(filter)
              .toList());
    }
  }

  static TreeStats treeStats(Path root) throws IOException {
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

  private static String aggregateHash(Path root, List<Path> files)
      throws IOException, NoSuchAlgorithmException {
    List<Path> sorted =
        files.stream()
            .sorted(
                Comparator.comparing(
                    path -> root.relativize(path).toString().replace('\\', '/'),
                    GateCli::compareUtf8))
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
    return java.util.Arrays.compareUnsigned(
        left.getBytes(StandardCharsets.UTF_8), right.getBytes(StandardCharsets.UTF_8));
  }

  static String sha256(Path file) throws IOException, NoSuchAlgorithmException {
    if (file == null) throw new IllegalArgumentException("hash source is required");
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var input = Files.newInputStream(file)) {
      byte[] buffer = new byte[1024 * 1024];
      for (int read = input.read(buffer); read >= 0; read = input.read(buffer)) {
        digest.update(buffer, 0, read);
      }
    }
    return HEX.formatHex(digest.digest());
  }

  static void writeJson(Path output, Object value) throws IOException {
    if (output == null) throw new IllegalArgumentException("output is required");
    Path normalized = output.toAbsolutePath().normalize();
    Path parent = normalized.getParent();
    if (parent == null)
      throw new IllegalArgumentException("output must name a file below a directory");
    if (!ACTIVE_OUTPUTS.add(normalized)) {
      throw new IllegalStateException(
          "concurrent write to the same output is not allowed: " + normalized);
    }
    Path temporary = normalized.resolveSibling(normalized.getFileName() + ".part");
    try {
      Files.createDirectories(parent);
      JSON.writeValue(temporary.toFile(), value);
      Files.move(
          temporary,
          normalized,
          StandardCopyOption.REPLACE_EXISTING,
          StandardCopyOption.ATOMIC_MOVE);
    } finally {
      try {
        Files.deleteIfExists(temporary);
      } finally {
        ACTIVE_OUTPUTS.remove(normalized);
      }
    }
  }

  record TreeStats(long fileCount, long bytes, List<String> symlinks) {}
}
