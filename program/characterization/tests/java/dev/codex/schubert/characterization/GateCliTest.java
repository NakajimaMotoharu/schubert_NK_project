package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermission;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Contract tests for BUG-001/YKT-001 gate orchestration. Program: NK-CHR-001. */
class GateCliTest {
  private static final ObjectMapper JSON = new ObjectMapper();
  private static final HexFormat HEX = HexFormat.of();
  private static final Path SOURCE_ROOT =
      Path.of(System.getProperty("chr.unitProjectRoot")).toAbsolutePath().normalize();

  @TempDir Path temporaryDirectory;

  @Test
  void mainRejectsMissingUnknownAndIncompleteCommands() throws Exception {
    assertThrows(IllegalArgumentException.class, () -> GateCli.main(new String[0]));
    assertThrows(IllegalArgumentException.class, () -> GateCli.main(new String[] {"unknown"}));

    Map<String, String> missingProjectRoot = new LinkedHashMap<>();
    missingProjectRoot.put("chr.projectRoot", null);
    withProperties(
        missingProjectRoot,
        () ->
            assertThrows(
                IllegalArgumentException.class,
                () -> GateCli.main(new String[] {"verify-source", "unused.json"})));
    withProperties(
        Map.of("chr.projectRoot", "  "),
        () ->
            assertThrows(
                IllegalArgumentException.class,
                () -> GateCli.main(new String[] {"verify-source", "unused.json"})));
    assertThrows(
        IllegalArgumentException.class,
        () -> GateCli.main(new String[] {"compare-current", temporaryDirectory.toString()}));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            GateCli.main(
                new String[] {
                  "compare-current", temporaryDirectory.toString(), temporaryDirectory.toString()
                }));
  }

  @Test
  void verifySourceAcceptsIndependentInventoryAndRejectsDriftAndSymlink() throws Exception {
    Path project = temporaryDirectory.resolve("source-project");
    Path current = temporaryDirectory.resolve("source-current");
    Path sourceA = write(current.resolve("program/app/src/a/A.java"), "class A {}\n");
    Path sourceB = write(current.resolve("program/app/src/日本語/B.java"), "class B {}\n");
    Path schema = write(current.resolve("program/database/schema.sql"), "schema\n");
    Path load = write(current.resolve("program/database/load_scenario_data.sql"), "load\n");
    Path generator =
        write(current.resolve("program/database/generate_scenario_sql.py"), "generate\n");
    Path document = write(current.resolve("documents/001.md"), "# document\n");
    write(current.resolve("documents/ignored.txt"), "not a design document\n");
    Path masterA = write(current.resolve("data/master/a.bin"), "abc");
    Path masterB = write(current.resolve("data/master/nested/b.bin"), "12345");

    Map<String, Object> expected = new LinkedHashMap<>();
    expected.put("sourceFileCount", 5);
    expected.put(
        "sourceAggregateSha256",
        aggregateBySpecification(current, List.of(sourceA, sourceB, schema, load, generator)));
    expected.put("documentFileCount", 1);
    expected.put("documentAggregateSha256", aggregateBySpecification(current, List.of(document)));
    expected.put("masterFileCount", 2);
    expected.put("masterBytes", Files.size(masterA) + Files.size(masterB));
    writeJson(
        project.resolve("program/characterization/tests/resources/fixtures/expected.json"),
        expected);

    Path passOutput = temporaryDirectory.resolve("source-pass.json");
    withProperties(
        Map.of("chr.projectRoot", project.toString(), "chr.currentRoot", current.toString()),
        () -> GateCli.main(new String[] {"verify-source", passOutput.toString()}));
    JsonNode pass = JSON.readTree(passOutput.toFile());
    assertEquals("PASS", pass.path("status").asText());
    assertEquals(5, pass.path("sourceFileCount").asInt());
    assertEquals(2, pass.path("masterFileCount").asInt());

    Path outside = write(temporaryDirectory.resolve("outside.bin"), "outside");
    Files.createSymbolicLink(current.resolve("data/master/link.bin"), outside);
    expected.put("sourceFileCount", 999);
    writeJson(
        project.resolve("program/characterization/tests/resources/fixtures/expected.json"),
        expected);
    Path failOutput = temporaryDirectory.resolve("source-fail.json");
    withProperties(
        Map.of("chr.projectRoot", project.toString(), "chr.currentRoot", current.toString()),
        () ->
            assertThrows(
                IllegalStateException.class,
                () -> GateCli.main(new String[] {"verify-source", failOutput.toString()})));
    JsonNode fail = JSON.readTree(failOutput.toFile());
    assertEquals("FAIL", fail.path("status").asText());
    assertTrue(
        strings(fail.path("failures")).stream()
            .anyMatch(value -> value.startsWith("sourceFileCount expected=")));
    assertTrue(strings(fail.path("failures")).contains("masterSymlinks must be empty"));
  }

  @Test
  void preflightValidatesFilesPermissionsStorageNetworkAndPorts() throws Exception {
    Path highDiskRuntime =
        SOURCE_ROOT
            .resolve("program/characterization/target/preflight-test")
            .resolve(UUID.randomUUID().toString());
    try {
      PreflightFixture valid = preflightFixture("valid", highDiskRuntime);
      Path passOutput = temporaryDirectory.resolve("preflight-pass.json");
      withProperties(
          valid.properties(),
          () -> GateCli.main(new String[] {"preflight", passOutput.toString()}));
      JsonNode pass = JSON.readTree(passOutput.toFile());
      assertEquals("PASS", pass.path("status").asText());
      assertEquals("0600", pass.path("credentialPermission").asText());

      PreflightFixture invalid =
          preflightFixture("invalid", temporaryDirectory.resolve("low-disk-runtime"));
      Path externalSource = temporaryDirectory.resolve("external-source");
      Files.createDirectories(externalSource);
      Path source = invalid.currentRoot().resolve("program/app/src");
      Files.delete(source);
      Files.createSymbolicLink(source, externalSource);
      Path notAssetDirectory = write(temporaryDirectory.resolve("not-assets"), "file");
      Path notPgDirectory = write(temporaryDirectory.resolve("not-pgdata"), "file");
      Files.setPosixFilePermissions(
          invalid.usersFile(),
          Set.of(
              PosixFilePermission.OWNER_READ,
              PosixFilePermission.OWNER_WRITE,
              PosixFilePermission.GROUP_READ));
      Map<String, String> invalidProperties = new LinkedHashMap<>(invalid.properties());
      invalidProperties.put(
          "chr.currentJar", invalid.currentRoot().resolve("data/master").toString());
      invalidProperties.put("chr.assetRoot", notAssetDirectory.toString());
      invalidProperties.put(
          "chr.javaExecutable", temporaryDirectory.resolve("missing-java").toString());
      invalidProperties.put(
          "chr.caddyExecutable", temporaryDirectory.resolve("missing-caddy").toString());
      invalidProperties.put("chr.pgCtl", temporaryDirectory.resolve("missing-pgctl").toString());
      invalidProperties.put("chr.pgData", notPgDirectory.toString());
      invalidProperties.put("chr.dbUrl", "jdbc:postgresql://external.example:5432/db");
      invalidProperties.put("chr.appPort", "1");
      invalidProperties.put("chr.proxyPort", "1025");
      Path invalidOutput = temporaryDirectory.resolve("preflight-invalid.json");
      withProperties(
          invalidProperties,
          () ->
              assertThrows(
                  IllegalStateException.class,
                  () -> GateCli.main(new String[] {"preflight", invalidOutput.toString()})));
      List<String> failures = strings(JSON.readTree(invalidOutput.toFile()).path("failures"));
      assertTrue(failures.contains("currentJar is not a regular file"));
      assertTrue(failures.contains("assetRoot is not a directory"));
      assertTrue(failures.contains("current source root escapes currentRoot"));
      assertTrue(failures.contains("usersFile permission must be 0600"));
      assertTrue(failures.contains("evidence storage must have at least 20GiB free"));
      assertTrue(failures.contains("dbUrl must target loopback allowlist"));

      assertPortFailure(valid, 1025, 1, "proxy-privileged");
      assertPortFailure(valid, 1025, 1025, "ports-equal");
    } finally {
      deleteTree(highDiskRuntime);
    }
  }

  @Test
  void repeatComparisonRequiresTwentyEightIdenticalArtifacts() throws Exception {
    Path reports = SOURCE_ROOT.resolve("program/characterization/reports/current");
    Path first = reports.resolve("pgpt-gate-20260901-05");
    Path second = reports.resolve("pgpt-gate-20260901-06");
    Path passOutput = temporaryDirectory.resolve("repeat-pass.json");
    GateCli.main(
        new String[] {
          "compare-current", first.toString(), second.toString(), passOutput.toString()
        });
    JsonNode pass = JSON.readTree(passOutput.toFile());
    assertEquals("PASS", pass.path("status").asText());
    assertEquals(28, pass.path("expectedFileCount").asInt());
    assertEquals(28, pass.path("firstFileCount").asInt());

    Path alteredFirst = temporaryDirectory.resolve("altered-first");
    Path alteredSecond = temporaryDirectory.resolve("altered-second");
    write(alteredFirst.resolve("artifacts/common.json"), "first");
    write(alteredFirst.resolve("artifacts/first-only.json"), "first-only");
    write(alteredFirst.resolve("screenshots/first.png"), "png-first");
    write(alteredFirst.resolve("inventory.json"), "inventory-first");
    write(alteredSecond.resolve("artifacts/common.json"), "second");
    write(alteredSecond.resolve("artifacts/second-only.json"), "second-only");
    write(alteredSecond.resolve("screenshots/second.png"), "png-second");
    write(alteredSecond.resolve("supplemental.json"), "supplemental-second");
    Path failOutput = temporaryDirectory.resolve("repeat-fail.json");
    assertThrows(
        IllegalStateException.class,
        () ->
            GateCli.main(
                new String[] {
                  "compare-current",
                  alteredFirst.toString(),
                  alteredSecond.toString(),
                  failOutput.toString()
                }));
    JsonNode fail = JSON.readTree(failOutput.toFile());
    assertEquals("FAIL", fail.path("status").asText());
    assertTrue(strings(fail.path("missing")).contains("first-only.json"));
    assertTrue(strings(fail.path("extra")).contains("second-only.json"));
    assertTrue(strings(fail.path("changed")).contains("common.json"));

    Path emptyOutput = temporaryDirectory.resolve("repeat-empty.json");
    assertThrows(
        IllegalStateException.class,
        () ->
            GateCli.compareCurrent(
                temporaryDirectory.resolve("absent-one"),
                temporaryDirectory.resolve("absent-two"),
                emptyOutput));
    assertEquals("FAIL", JSON.readTree(emptyOutput.toFile()).path("status").asText());
  }

  @Test
  @org.junit.jupiter.api.DisplayName("PT-CHR-PATH-001 parentless log path rejected before IO")
  void preflightRejectsParentlessLogPathWithoutNpe() throws Exception {
    PreflightFixture fixture =
        preflightFixture("parentless-log", temporaryDirectory.resolve("owned-runtime"));
    Map<String, String> properties = new LinkedHashMap<>(fixture.properties());
    Path parentless = Path.of("/");
    assertEquals(null, parentless.getParent());
    properties.put("chr.pgLog", parentless.toString());
    withProperties(
        properties,
        () ->
            assertThrows(
                IllegalArgumentException.class,
                () ->
                    GateCli.preflight(
                        fixture.projectRoot(), temporaryDirectory.resolve("not-written.json"))));
  }

  @Test
  @org.junit.jupiter.api.DisplayName("PT-CHR-PATH-002 parentless output rejected before temporary path")
  void jsonWriterRejectsParentlessOutputWithoutNpe() {
    assertFalse(Files.exists(Path.of("null.part")), "isolated snapshot has no foreign temporary file");
    assertThrows(
        IllegalArgumentException.class, () -> GateCli.writeJson(Path.of("/"), Map.of()));
  }

  @Test
  void reportMapsEveryGateAndRejectsSecretCanaries() throws Exception {
    Path users =
        ownerOnlyFile(
            temporaryDirectory.resolve("report-users.txt"),
            "user=unit-user-not-present\npass=unit-pass-not-present\n");
    Path reports = SOURCE_ROOT.resolve("program/characterization/reports/current");
    Path comparison =
        SOURCE_ROOT.resolve("program/characterization/reports/current-repeat-comparison.json");
    Path passOutput = temporaryDirectory.resolve("gate-pass.json");
    withProperties(
        Map.of("chr.projectRoot", SOURCE_ROOT.toString(), "chr.usersFile", users.toString()),
        () ->
            GateCli.main(
                new String[] {
                  "report",
                  reports.resolve("pgpt-gate-20260901-05").toString(),
                  reports.resolve("pgpt-gate-20260901-06").toString(),
                  comparison.toString(),
                  passOutput.toString()
                }));
    JsonNode pass = JSON.readTree(passOutput.toFile());
    assertEquals("PASS", pass.path("status").asText());
    assertTrue(
        pass.path("gates").properties().stream()
            .allMatch(entry -> "PASS".equals(entry.getValue().asText())));

    Path failureProject = reportFixture("gate-failures");
    mutate(
        failureProject.resolve("program/characterization/tests/resources/cases/gate-contract.json"),
        root -> root.put("version", 0));
    mutate(
        failureProject.resolve("program/characterization/tests/resources/cases/dif-allowlist.json"),
        root -> root.put("version", 0));
    mutate(
        failureProject.resolve("program/characterization/reports/source-verification.json"),
        root -> root.put("status", "FAIL"));
    mutate(
        failureProject.resolve("program/characterization/reports/current-repeat-comparison.json"),
        root -> root.put("status", "FAIL"));
    Path first = run(failureProject, "pgpt-gate-20260901-05");
    Path second = run(failureProject, "pgpt-gate-20260901-06");
    Files.delete(first.resolve("artifacts/CHR-A01.json"));
    Path failUsers =
        ownerOnlyFile(temporaryDirectory.resolve("fail-users.txt"), "pass=not-in-fixture\n");
    Path failOutput = temporaryDirectory.resolve("gate-fail.json");
    withProperties(
        Map.of(
            "chr.projectRoot", failureProject.toString(),
            "chr.usersFile", failUsers.toString()),
        () ->
            assertThrows(
                IllegalStateException.class,
                () ->
                    GateCli.main(
                        new String[] {
                          "report",
                          first.toString(),
                          second.toString(),
                          failureProject
                              .resolve(
                                  "program/characterization/reports/current-repeat-comparison.json")
                              .toString(),
                          failOutput.toString()
                        })));
    JsonNode fail = JSON.readTree(failOutput.toFile());
    assertEquals("FAIL", fail.path("status").asText());
    assertTrue(
        fail.path("gates").properties().stream()
            .allMatch(entry -> "FAIL".equals(entry.getValue().asText())));

    Path secretProject = reportFixture("gate-secret");
    String canary = "unit-secret-canary-7d9a";
    write(
        secretProject.resolve("program/characterization/reports/secret-canary.txt"),
        "prefix-" + canary + "-suffix");
    Path secretUsers =
        ownerOnlyFile(temporaryDirectory.resolve("secret-users.txt"), "pass=" + canary + "\n");
    Path secretOutput = temporaryDirectory.resolve("gate-secret.json");
    withProperties(
        Map.of(
            "chr.projectRoot", secretProject.toString(),
            "chr.usersFile", secretUsers.toString()),
        () ->
            assertThrows(
                IllegalStateException.class,
                () ->
                    GateCli.report(
                        secretProject,
                        run(secretProject, "pgpt-gate-20260901-05"),
                        run(secretProject, "pgpt-gate-20260901-06"),
                        secretProject.resolve(
                            "program/characterization/reports/current-repeat-comparison.json"),
                        secretOutput)));
    JsonNode secretFailure = JSON.readTree(secretOutput.toFile());
    assertEquals(1, secretFailure.path("secretScanHits").asInt());
    assertEquals("FAIL", secretFailure.path("gates").path("CHR-G06").asText());
    assertEquals("PASS", secretFailure.path("gates").path("CHR-G05").asText());
  }

  @Test
  @org.junit.jupiter.api.DisplayName("PT-CHR-PATH-003 unnamed source run rejected before IO")
  void promotionRejectsNullAndUnnamedSourceBeforeAnyIo() throws Exception {
    Path baseline = temporaryDirectory.resolve("not-created-baseline");
    withProperties(
        Map.of("chr.gateCommit", "abcdef1"),
        () -> {
          for (Path invalid : new Path[] {null, Path.of("/")}) {
            IllegalArgumentException error =
                assertThrows(
                    IllegalArgumentException.class,
                    () -> GateCli.promoteCurrent(SOURCE_ROOT, invalid, baseline));
            assertEquals("sourceRun must name a run directory", error.getMessage());
            assertFalse(Files.exists(baseline));
          }
        });
  }

  @Test
  void baselinePromotionIsImmutableCommitBoundAndSymlinkSafe() throws Exception {
    Path sourceRun =
        SOURCE_ROOT
            .resolve("program/characterization/reports/current")
            .resolve("pgpt-gate-20260901-05");
    Path baseline = temporaryDirectory.resolve("promoted-baseline");
    withProperties(
        Map.of("chr.projectRoot", SOURCE_ROOT.toString(), "chr.gateCommit", "abcdef1"),
        () ->
            GateCli.main(
                new String[] {"promote-current", sourceRun.toString(), baseline.toString()}));
    JsonNode manifest = JSON.readTree(baseline.resolve("manifest.json").toFile());
    assertEquals("abcdef1", manifest.path("gateCommit").asText());
    assertEquals(24, manifest.path("caseCount").asInt());
    assertEquals(2, manifest.path("screenshotFileCount").asInt());
    assertTrue(Files.isRegularFile(baseline.resolve("artifacts/CHR-A01.json")));

    withProperties(
        Map.of("chr.gateCommit", "abcdef1"),
        () ->
            assertThrows(
                IllegalStateException.class,
                () -> GateCli.promoteCurrent(SOURCE_ROOT, sourceRun, baseline)));

    Path existingEmpty = temporaryDirectory.resolve("existing-empty-baseline");
    Files.createDirectories(existingEmpty);
    withProperties(
        Map.of("chr.gateCommit", "0123456789abcdef0123456789abcdef01234567"),
        () -> GateCli.promoteCurrent(SOURCE_ROOT, sourceRun, existingEmpty));
    assertEquals(
        "0123456789abcdef0123456789abcdef01234567",
        JSON.readTree(existingEmpty.resolve("manifest.json").toFile()).path("gateCommit").asText());

    withProperties(
        Map.of("chr.gateCommit", "INVALID"),
        () ->
            assertThrows(
                IllegalArgumentException.class,
                () ->
                    GateCli.promoteCurrent(
                        SOURCE_ROOT, sourceRun, temporaryDirectory.resolve("invalid-commit"))));

    Path linkedRun = temporaryDirectory.resolve("linked-run");
    copyTree(sourceRun, linkedRun);
    Files.createSymbolicLink(
        linkedRun.resolve("artifacts/link.json"), linkedRun.resolve("artifacts/CHR-A01.json"));
    withProperties(
        Map.of("chr.gateCommit", "abcdef1"),
        () ->
            assertThrows(
                IOException.class,
                () ->
                    GateCli.promoteCurrent(
                        SOURCE_ROOT, linkedRun, temporaryDirectory.resolve("linked-baseline"))));
  }

  @Test
  void fileInventoryUtilitiesHandleMissingFilteredNestedAndLinkedFiles() throws Exception {
    Path root = temporaryDirectory.resolve("utilities");
    Path first = write(root.resolve("a.txt"), "a");
    Path second = write(root.resolve("nested/b.md"), "bb");
    Files.createSymbolicLink(root.resolve("linked.txt"), first);

    assertTrue(GateCli.regularFiles(temporaryDirectory.resolve("absent"), path -> true).isEmpty());
    assertEquals(
        List.of(second), GateCli.regularFiles(root, path -> path.toString().endsWith(".md")));
    GateCli.TreeStats stats = GateCli.treeStats(root);
    assertEquals(2, stats.fileCount());
    assertEquals(3, stats.bytes());
    assertEquals(List.of("linked.txt"), stats.symlinks());
    assertTrue(GateCli.fileHashes(temporaryDirectory.resolve("absent-hashes")).isEmpty());
    assertEquals(2, GateCli.fileHashes(root).size());

    Path cases = temporaryDirectory.resolve("case-order");
    write(cases.resolve("ignored.json"), "{}");
    write(cases.resolve("CHR-O01.json"), "{}");
    write(cases.resolve("CHR-A02.json"), "{}");
    write(cases.resolve("CHR-A01.json"), "{}");
    assertEquals(List.of("CHR-A01", "CHR-A02", "CHR-O01"), GateCli.caseIds(cases));
    assertTrue(GateCli.caseIds(temporaryDirectory.resolve("absent-cases")).isEmpty());
  }

  @Test
  void secretScanHandlesCredentialSessionMissingLargeAndBinaryInputs() throws Exception {
    Path users =
        ownerOnlyFile(
            temporaryDirectory.resolve("scan-users.txt"),
            "ignored=value\nuser=\npass=scan-pass-canary\nuser=scan-user-canary\n");
    Path emptyProject = temporaryDirectory.resolve("empty-secret-project");
    Files.createDirectories(emptyProject);
    assertTrue(GateCli.secretScan(emptyProject, users).isEmpty());

    Path project = temporaryDirectory.resolve("secret-project");
    write(project.resolve("program/characterization/baseline/clean.txt"), "clean");
    write(
        project.resolve("program/characterization/reports/password.txt"),
        "prefix scan-pass-canary suffix");
    write(
        project.resolve("program/characterization/reports/session.txt"),
        "Cookie: JSESSIONID=redacted-test-value");
    write(project.resolve("program/characterization/reports/other.txt"), "unrelated");
    Path large = project.resolve("program/characterization/reports/large.bin");
    Files.createDirectories(large.getParent());
    try (SeekableByteChannel channel =
        Files.newByteChannel(large, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
      channel.position(10L * 1024 * 1024);
      channel.write(ByteBuffer.wrap(new byte[] {1}));
    }
    List<String> hits = GateCli.secretScan(project, users);
    assertEquals(2, hits.size());
    assertTrue(hits.stream().anyMatch(path -> path.endsWith("password.txt")));
    assertTrue(hits.stream().anyMatch(path -> path.endsWith("session.txt")));

    Path binary = temporaryDirectory.resolve("binary.bin");
    Files.write(binary, new byte[] {0, 1, 2, 3});
    assertFalse(GateCli.containsAny(binary, List.of("", "target-too-long", "zz")));
    Files.write(binary, "x-match-y".getBytes(StandardCharsets.UTF_8));
    assertTrue(GateCli.containsAny(binary, List.of("match")));
  }

  @Test
  void atomicJsonWriterRejectsConcurrentUseOfTheSameOutput() throws Exception {
    Path output = temporaryDirectory.resolve("atomic/concurrent.json");
    CountDownLatch serializationStarted = new CountDownLatch(1);
    CountDownLatch releaseSerialization = new CountDownLatch(1);
    try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      var first =
          executor.submit(
              (Callable<Void>)
                  () -> {
                    GateCli.writeJson(
                        output, new BlockingValue(serializationStarted, releaseSerialization));
                    return null;
                  });
      assertTrue(serializationStarted.await(5, TimeUnit.SECONDS));
      assertThrows(
          IllegalStateException.class, () -> GateCli.writeJson(output, Map.of("value", "second")));
      releaseSerialization.countDown();
      first.get(5, TimeUnit.SECONDS);
    }
    assertEquals("first", JSON.readTree(output.toFile()).path("value").asText());
    assertFalse(Files.exists(output.resolveSibling("concurrent.json.part")));
    assertThrows(IllegalArgumentException.class, () -> GateCli.writeJson(null, Map.of()));
  }

  private void assertPortFailure(PreflightFixture fixture, int appPort, int proxyPort, String name)
      throws Exception {
    Map<String, String> properties = new LinkedHashMap<>(fixture.properties());
    properties.put("chr.appPort", Integer.toString(appPort));
    properties.put("chr.proxyPort", Integer.toString(proxyPort));
    Path output = temporaryDirectory.resolve(name + ".json");
    withProperties(
        properties,
        () ->
            assertThrows(
                IllegalStateException.class,
                () -> GateCli.preflight(fixture.projectRoot(), output)));
    assertTrue(
        strings(JSON.readTree(output.toFile()).path("failures"))
            .contains("app/proxy ports must be distinct non-privileged ports"));
  }

  private PreflightFixture preflightFixture(String name, Path runtimeRoot) throws Exception {
    Path project = temporaryDirectory.resolve("preflight-project-" + name);
    Path current = temporaryDirectory.resolve("preflight-current-" + name);
    Files.createDirectories(current.resolve("program/app/src"));
    Path currentJar = write(current.resolve("app.jar"), "jar");
    Path assetRoot = Files.createDirectories(current.resolve("data/master"));
    Path users = ownerOnlyFile(current.resolve("users.txt"), "user=test\npass=test\n");
    Path java = write(current.resolve("bin/java"), "java");
    Path caddy = write(current.resolve("bin/caddy"), "caddy");
    Path pgCtl = write(current.resolve("bin/pg_ctl"), "pgctl");
    Path pgData = Files.createDirectories(current.resolve("pgdata"));
    Path pgLog = current.resolve("logs/postgresql.log");
    Path pgSocket = current.resolve("pgsocket");
    Map<String, String> properties = new LinkedHashMap<>();
    properties.put("chr.projectRoot", project.toString());
    properties.put("chr.currentRoot", current.toString());
    properties.put("chr.currentJar", currentJar.toString());
    properties.put("chr.assetRoot", assetRoot.toString());
    properties.put("chr.usersFile", users.toString());
    properties.put("chr.javaExecutable", java.toString());
    properties.put("chr.caddyExecutable", caddy.toString());
    properties.put("chr.runtimeRoot", runtimeRoot.toString());
    properties.put("chr.pgCtl", pgCtl.toString());
    properties.put("chr.pgData", pgData.toString());
    properties.put("chr.pgLog", pgLog.toString());
    properties.put("chr.pgSocket", pgSocket.toString());
    properties.put("chr.dbUrl", "jdbc:postgresql://localhost:55432/test_db");
    properties.put("chr.appPort", "1024");
    properties.put("chr.proxyPort", "1025");
    return new PreflightFixture(project, current, users, Map.copyOf(properties));
  }

  private Path reportFixture(String name) throws Exception {
    Path project = temporaryDirectory.resolve(name);
    Path characterization = project.resolve("program/characterization");
    copyTree(
        SOURCE_ROOT.resolve("program/characterization/tests/resources"),
        characterization.resolve("tests/resources"));
    copyTree(
        SOURCE_ROOT.resolve("program/characterization/baseline/current"),
        characterization.resolve("baseline/current"));
    Path sourceReports = SOURCE_ROOT.resolve("program/characterization/reports");
    for (String report :
        List.of(
            "source-verification.json",
            "preflight.json",
            "review-record.json",
            "current-repeat-comparison.json")) {
      Files.createDirectories(characterization.resolve("reports"));
      Files.copy(
          sourceReports.resolve(report),
          characterization.resolve("reports").resolve(report),
          StandardCopyOption.COPY_ATTRIBUTES);
    }
    copyTree(
        sourceReports.resolve("current/pgpt-gate-20260901-05"),
        characterization.resolve("reports/current/pgpt-gate-20260901-05"));
    copyTree(
        sourceReports.resolve("current/pgpt-gate-20260901-06"),
        characterization.resolve("reports/current/pgpt-gate-20260901-06"));
    return project;
  }

  private static Path run(Path project, String runId) {
    return project.resolve("program/characterization/reports/current").resolve(runId);
  }

  private static void mutate(Path file, Consumer<ObjectNode> mutation) throws Exception {
    ObjectNode root = (ObjectNode) JSON.readTree(file.toFile());
    mutation.accept(root);
    writeJson(file, root);
  }

  private static Path ownerOnlyFile(Path path, String content) throws IOException {
    write(path, content);
    Files.setPosixFilePermissions(
        path, Set.of(PosixFilePermission.OWNER_READ, PosixFilePermission.OWNER_WRITE));
    return path;
  }

  private static Path write(Path path, String value) throws IOException {
    Files.createDirectories(path.getParent());
    Files.writeString(path, value, StandardCharsets.UTF_8);
    return path;
  }

  private static void writeJson(Path path, Object value) throws IOException {
    Files.createDirectories(path.getParent());
    JSON.writerWithDefaultPrettyPrinter().writeValue(path.toFile(), value);
  }

  private static List<String> strings(JsonNode values) {
    List<String> result = new ArrayList<>();
    values.forEach(value -> result.add(value.asText()));
    return result;
  }

  private static String aggregateBySpecification(Path root, List<Path> files) throws Exception {
    List<Path> sorted =
        files.stream()
            .sorted(
                Comparator.comparing(
                    path -> root.relativize(path).toString().replace('\\', '/'),
                    (left, right) ->
                        Arrays.compareUnsigned(
                            left.getBytes(StandardCharsets.UTF_8),
                            right.getBytes(StandardCharsets.UTF_8))))
            .toList();
    MessageDigest aggregate = MessageDigest.getInstance("SHA-256");
    for (Path file : sorted) {
      String relative = root.relativize(file).toString().replace('\\', '/');
      aggregate.update((sha256(file) + "  " + relative + "\n").getBytes(StandardCharsets.UTF_8));
    }
    return HEX.formatHex(aggregate.digest());
  }

  private static String sha256(Path file) throws Exception {
    return HEX.formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(file)));
  }

  private static void copyTree(Path source, Path destination) throws IOException {
    try (Stream<Path> paths = Files.walk(source)) {
      for (Path path : paths.sorted().toList()) {
        Path target = destination.resolve(source.relativize(path).toString());
        if (Files.isDirectory(path, LinkOption.NOFOLLOW_LINKS)) {
          Files.createDirectories(target);
        } else {
          Files.copy(path, target, StandardCopyOption.COPY_ATTRIBUTES);
        }
      }
    }
  }

  private static void deleteTree(Path root) throws IOException {
    if (root == null || !Files.exists(root, LinkOption.NOFOLLOW_LINKS)) return;
    try (Stream<Path> paths = Files.walk(root)) {
      for (Path path : paths.sorted(Comparator.reverseOrder()).toList()) {
        Files.deleteIfExists(path);
      }
    }
  }

  private static void withProperties(Map<String, String> properties, ThrowingRunnable action)
      throws Exception {
    Map<String, String> previous = new TreeMap<>();
    properties.forEach((name, value) -> previous.put(name, System.getProperty(name)));
    try {
      properties.forEach(
          (name, value) -> {
            if (value == null) System.clearProperty(name);
            else System.setProperty(name, value);
          });
      action.run();
    } finally {
      previous.forEach(
          (name, value) -> {
            if (value == null) System.clearProperty(name);
            else System.setProperty(name, value);
          });
    }
  }

  @FunctionalInterface
  private interface ThrowingRunnable {
    void run() throws Exception;
  }

  private record PreflightFixture(
      Path projectRoot, Path currentRoot, Path usersFile, Map<String, String> properties) {}

  private record BlockingValue(CountDownLatch started, CountDownLatch release) {
    public String getValue() throws InterruptedException {
      started.countDown();
      if (!release.await(5, TimeUnit.SECONDS)) {
        throw new IllegalStateException("serialization barrier timed out");
      }
      return "first";
    }
  }
}
