package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.api.io.TempDir;

/** NK-OPS-001/PT-OPS-INBOX-001..008; SS341/342/343 6.8. No host service is started. */
final class InspectorDeploymentTest {
  private static final String FIXTURE_BIN_SH_EA0135D2 = "/bin/sh";
  private static final Path REPO = Path.of(System.getProperty("nk.pt.repository"));
  private static final Path DEPLOYMENT = REPO.resolve("src/deployment");
  private static final Path SHELLCHECK = shellCheck();
  private static final String UNIT = "schubert-nk-inbox-inspector.service";
  @TempDir Path root;
  private String method;
  private int sequence;

  private static Path shellCheck() {
    String configured = System.getenv("SCHUBERT_SHELLCHECK");
    return configured == null || configured.isBlank()
        ? Path.of(
            "/home/mini/codex/project1/work/toolchain/shellcheck-0.11.0/root/usr/bin/shellcheck")
        : Path.of(configured);
  }

  @BeforeEach
  void evidenceMethod(TestInfo info) {
    method = info.getTestMethod().orElseThrow().getName();
  }

  @Test
  void renderedShellCheck() throws Exception {
    var wrapper = fake("NKINSPECTOR1 0\n", 0);
    assertEquals(0, execute(List.of(FIXTURE_BIN_SH_EA0135D2, "-n", wrapper.toString())).code());
    var version = execute(List.of(SHELLCHECK.toString(), "--version"));
    assertEquals(0, version.code());
    assertTrue(version.out().contains("version: 0.11.0"));
    var result =
        execute(
            List.of(SHELLCHECK.toString(), "--shell=sh", "--severity=style", wrapper.toString()));
    assertEquals(new Result(0, "", ""), result);
  }

  @Test
  void statusMapping() throws Exception {
    for (int status : List.of(0, 10, 50, 70)) {
      var result = shell(fake("NKINSPECTOR1 " + status + "\n", 0));
      assertEquals(status, result.code());
      assertEquals("", result.out());
      assertTrue(result.err().contains("exit " + status));
      assertReceipt(result, "NKINSPECTOR1 " + status + "\n.");
    }
    for (int status : List.of(1, 70, 143)) {
      var result = shell(fake("NKINSPECTOR1 0\n", status));
      assertEquals(50, result.code());
      assertEquals("", result.out());
      assertReceipt(result, "NKINSPECTOR1 0\n!");
    }
    Path brokenOd = Files.createTempFile(root, "failed-od-", ".sh");
    Files.writeString(brokenOd, "#!/bin/sh\nexit 1\n");
    Files.setPosixFilePermissions(brokenOd, PosixFilePermissions.fromString("rwx------"));
    Path injected = fake("NKINSPECTOR1 0\n", 0);
    // Test-only executable-boundary fault. Production has no configurable od path.
    Files.writeString(
        injected, Files.readString(injected).replace("/usr/bin/od", "'" + brokenOd + "'"));
    var failedOd = shell(injected);
    assertEquals(50, failedOd.code());
    assertEquals("", failedOd.out());
    var missingJava =
        shell(render(root.resolve("missing-java").toString(), "/fixed/api.jar", "/fixed/lib"));
    assertEquals(50, missingJava.code());
    assertEquals("", missingJava.out());
    assertReceipt(missingJava, "!");
    // BUG217/YKT173: pipeline xtrace may interleave; the parent's post-pipeline hex is stable.
    assertReceipt(
        new Result(
            50,
            "",
            "+ + printf/usr/bin/od ! -An\n -v -tx1 -w64\n+ inspector_receipt= 21\n+ exit 50\n"),
        "!");
    for (String wrong :
        List.of(
            "",
            "+ inspector_receipt= 2e\n",
            "+ inspector_receipt= 21\n+ inspector_receipt= 21\n",
            "+ inspector_receipt= 21\n+ inspector_receipt= 2e\n")) {
      assertThrows(AssertionError.class, () -> assertReceipt(new Result(50, "", wrong), "!"));
    }
  }

  @Test
  void malformedReceipts() throws Exception {
    var receipts =
        new ArrayList<>(
            List.of(
                "",
                "NKINSPECTOR1 1\n",
                "NKINSPECTOR2 0\n",
                "NKINSPECTOR1 0",
                "NKINSPECTOR1 0\n\n",
                "NKINSPECTOR1 0\r\n",
                " NKINSPECTOR1 0\n",
                "NKINSPECTOR1 0 \n",
                "NKINSPECTOR1 00\n",
                "NKINSPECTOR1 0\nEXTRA\n",
                "NKINSPECTOR1 0\nNKINSPECTOR1 0\n"));
    String exact = "NKINSPECTOR1 0\n";
    for (int i = 0; i <= exact.length(); i++)
      receipts.add(exact.substring(0, i) + '\0' + exact.substring(i));
    receipts.add("\u0080" + exact);
    receipts.add(exact + "\u00ff");
    assertEquals(29, receipts.size());
    for (String receipt : receipts) {
      var result = shell(fake(receipt, 0));
      assertEquals(50, result.code(), receipt);
      assertEquals("", result.out());
      assertReceipt(result, receipt + ".");
      assertTrue(result.err().contains("exit 50"));
    }
  }

  @Test
  void argumentsAndPlaceholders() throws Exception {
    var wrapper = fake("NKINSPECTOR1 0\n", 0);
    for (List<String> arguments : List.of(List.of("unknown"), List.of("one", "two"))) {
      var command = new ArrayList<>(List.of(FIXTURE_BIN_SH_EA0135D2, "-x", wrapper.toString()));
      command.addAll(arguments);
      var result = execute(command);
      assertEquals(70, result.code());
      assertEquals("", result.out());
      assertFalse(result.err().contains("--enable-native-access"));
    }
    var unrendered = shell(DEPLOYMENT.resolve("operations/inbox-inspector.sh.template"));
    assertEquals(70, unrendered.code());
    assertEquals("", unrendered.out());
    assertFalse(unrendered.err().contains("--enable-native-access"));
  }

  @Test
  void realMainBridge() throws Exception {
    Path wrapper =
        render(
            Path.of(System.getProperty("java.home"), "bin/java").toString(),
            System.getProperty("java.class.path"),
            root.toString());
    var result = execute(List.of(FIXTURE_BIN_SH_EA0135D2, wrapper.toString()));
    assertEquals(new Result(70, "", ""), result);
  }

  @Test
  void baseUnitAndSyntax() throws Exception {
    var actual = directives(Files.readString(DEPLOYMENT.resolve("systemd/" + UNIT)));
    var expected = new LinkedHashMap<String, List<String>>();
    String literals =
        """
        Unit.Description=Schubert NK private Inbox maintenance inspector
        Unit.After=postgresql.service
        Unit.Requires=postgresql.service
        Unit.Before=artemis.service schubert-nk-api.service schubert-nk-web.service caddy.service
        Service.Type=oneshot
        Service.User=schubert-inbox-inspector
        Service.Group=schubert-inbox-inspector
        Service.SupplementaryGroups=schubert schubert-read
        Service.CapabilityBoundingSet=
        Service.AmbientCapabilities=
        Service.RemainAfterExit=yes
        Service.WorkingDirectory=/opt/schubert-nk/current/api
        Service.ExecStart=/opt/schubert-nk/current/operations/bin/schubert-nk-inbox-inspector
        Service.EnvironmentFile=/etc/schubert-nk/inbox-inspector.env
        Service.EnvironmentFile=/run/schubert-nk/maintenance/inbox-inspector.env
        Service.UnsetEnvironment=JAVA_TOOL_OPTIONS JDK_JAVA_OPTIONS _JAVA_OPTIONS CLASSPATH LD_PRELOAD LD_LIBRARY_PATH
        Service.LoadCredential=db-inbox-inspector:/etc/schubert-nk/credentials/db-inbox-inspector
        Service.LoadCredential=maintenance-owner:/run/schubert-nk/cleanup-request/inspector-owner
        Service.LoadCredential=api-context-aes-current:/etc/schubert-nk/credentials/api-context-aes-current
        Service.LoadCredential=api-inbox-response-aes-current:/etc/schubert-nk/credentials/api-inbox-response-aes-current
        Service.Restart=no
        Service.SuccessExitStatus=10
        Service.TimeoutStartSec=30min
        Service.TimeoutStopSec=60s
        Service.KillMode=control-group
        Service.SendSIGKILL=no
        Service.MemoryMax=1024M
        Service.LimitNOFILE=65536
        Service.UMask=0077
        Service.NoNewPrivileges=true
        Service.PrivateTmp=true
        Service.PrivateDevices=true
        Service.ProtectSystem=strict
        Service.ProtectHome=true
        Service.ProtectKernelTunables=true
        Service.ProtectKernelModules=true
        Service.ProtectControlGroups=true
        Service.ProtectKernelLogs=true
        Service.ProtectClock=true
        Service.ProtectHostname=true
        Service.RestrictSUIDSGID=true
        Service.LockPersonality=true
        Service.RestrictNamespaces=true
        Service.RestrictRealtime=true
        Service.RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
        Service.StandardOutput=journal
        Service.StandardError=journal
        """;
    for (String line : literals.lines().toList()) {
      String[] pair = line.split("=", 2);
      expected.computeIfAbsent(pair[0], ignored -> new ArrayList<>()).add(pair[1]);
    }
    assertEquals(expected, actual);
    verifyUnit(List.of());
  }

  @Test
  void previousProfiles() throws Exception {
    String context = "api-context-aes-previous";
    String response = "api-inbox-response-aes-previous";
    for (var selection :
        List.of(
            List.<String>of(), List.of(context), List.of(response), List.of(context, response))) {
      var ids =
          new HashSet<>(
              List.of(
                  "db-inbox-inspector",
                  "maintenance-owner",
                  "api-context-aes-current",
                  "api-inbox-response-aes-current"));
      var paths = new ArrayList<Path>();
      for (String id : selection) {
        Path path =
            DEPLOYMENT.resolve(
                "systemd/optional/inbox-inspector-"
                    + (id.equals(context) ? "context" : "response")
                    + "-previous.conf");
        assertEquals(
            Map.of("Service.LoadCredential", List.of(id + ":/etc/schubert-nk/credentials/" + id)),
            directives(Files.readString(path)));
        assertTrue(ids.add(id));
        paths.add(path);
      }
      assertEquals(4 + selection.size(), ids.size());
      verifyUnit(paths);
    }
  }

  @Test
  void releaseClasspathAndIsolation() throws Exception {
    String script = Files.readString(DEPLOYMENT.resolve("operations/inbox-inspector.sh.template"));
    for (String flag :
        List.of(
            "--enable-native-access=ALL-UNNAMED",
            "-Dfile.encoding=UTF-8",
            "-Duser.timezone=UTC",
            "-XX:+ExitOnOutOfMemoryError",
            "-Xms128m",
            "-Xmx512m",
            "-XX:MaxDirectMemorySize=64m",
            "-XX:MaxMetaspaceSize=192m",
            "-XX:ReservedCodeCacheSize=128m",
            "-cp '@API_JAR@:@LIB_DIR@/*'",
            "dev.codex.schubert.nk.api.maintenance.InspectorLauncher"))
      assertTrue(script.contains(flag), flag);
    for (String forbidden :
        List.of(
            "eval ", "sudo ", "systemd-run", "$JAVA", "$CLASSPATH", "HeapDump", "exec $", "sh -c"))
      assertFalse(script.contains(forbidden));
    var factory = javax.xml.parsers.DocumentBuilderFactory.newInstance();
    factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
    var pom =
        factory.newDocumentBuilder().parse(REPO.resolve("src/schubert-nk-api/pom.xml").toFile());
    var xpath = javax.xml.xpath.XPathFactory.newInstance().newXPath();
    assertEquals("25", xpath.evaluate("/project/properties/maven.compiler.release", pom));
    assertEquals("42.7.13", xpath.evaluate("/project/properties/postgresql.jdbc.version", pom));
    assertEquals(
        "compile",
        xpath.evaluate("/project/dependencies/dependency[artifactId='postgresql']/scope", pom));
    assertEquals(
        "${postgresql.jdbc.version}",
        xpath.evaluate("/project/dependencies/dependency[artifactId='postgresql']/version", pom));
  }

  private static void assertReceipt(Result result, String bytes) {
    String expected =
        "+ inspector_receipt= "
            + HexFormat.ofDelimiter(" ").formatHex(bytes.getBytes(StandardCharsets.UTF_8));
    assertEquals(
        List.of(expected),
        result.err().lines().filter(line -> line.startsWith("+ inspector_receipt=")).toList());
  }

  private Path fake(String receipt, int exit) throws Exception {
    var directory = Files.createTempDirectory(root, "fake-");
    Path output = directory.resolve("public-receipt.txt");
    Path executable = directory.resolve("java");
    Files.writeString(output, receipt);
    Files.writeString(executable, "#!/bin/sh\n/bin/cat '" + output + "'\nexit " + exit + "\n");
    Files.setPosixFilePermissions(executable, PosixFilePermissions.fromString("rwx------"));
    return render(
        executable.toString(), directory.resolve("api.jar").toString(), directory.toString());
  }

  private Path render(String java, String jar, String library) throws Exception {
    for (String value : List.of(java, jar, library)) assertFalse(value.contains("'"));
    String template =
        Files.readString(DEPLOYMENT.resolve("operations/inbox-inspector.sh.template"));
    Path script = Files.createTempFile(root, "wrapper-", ".sh");
    Files.writeString(
        script,
        template
            .replace("@JAVA_BIN@", java)
            .replace("@API_JAR@", jar)
            .replace("@LIB_DIR@", library));
    return script;
  }

  private Result shell(Path script) throws Exception {
    return execute(List.of(FIXTURE_BIN_SH_EA0135D2, "-x", script.toString()));
  }

  private Result execute(List<String> command) throws Exception {
    return execute(command, Map.of());
  }

  private Result execute(List<String> command, Map<String, String> environment) throws Exception {
    Path output = Files.createTempFile(root, "out-", ".txt");
    Path error = Files.createTempFile(root, "err-", ".txt");
    var builder = new ProcessBuilder(command);
    builder.environment().clear();
    builder.environment().putAll(environment);
    builder.redirectOutput(output.toFile()).redirectError(error.toFile());
    var process = builder.start();
    try {
      assertTrue(process.waitFor(20, TimeUnit.SECONDS), "bounded tool execution");
      var result =
          new Result(process.exitValue(), Files.readString(output), Files.readString(error));
      Path evidence =
          Files.createDirectories(
              REPO.resolve("src/schubert-nk-api/target/inspector-deployment/" + method));
      var json =
          new com.google.gson.GsonBuilder()
              .setPrettyPrinting()
              .create()
              .toJson(
                  Map.of(
                      "method",
                      method,
                      "command",
                      command,
                      "exitCode",
                      result.code(),
                      "stdout",
                      result.out(),
                      "stderr",
                      result.err()));
      json =
          json.replace(root.toString(), "<PT_ROOT>")
              .replace(REPO.toString(), "<REPOSITORY>")
              .replace(System.getProperty("java.home"), "<JDK>");
      Files.writeString(
          evidence.resolve(String.format(Locale.ROOT, "%03d.json", ++sequence)), json + "\n");
      return result;
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw interrupted;
    } finally {
      finishOwnedChild(process);
    }
  }

  // BUG2632: TERM is a request; only a finite successful wait confirms this test's child ended.
  static void finishOwnedChild(Process process) throws InterruptedException {
    if (!process.isAlive()) return;
    boolean interruptedOnEntry = Thread.interrupted();
    try {
      process.destroy();
      assertTrue(process.waitFor(10, TimeUnit.SECONDS), "owned tool termination unconfirmed");
    } catch (InterruptedException interrupted) {
      Thread.currentThread().interrupt();
      throw interrupted;
    } finally {
      if (interruptedOnEntry) Thread.currentThread().interrupt();
    }
  }

  private void verifyUnit(List<Path> profiles) throws Exception {
    var directory = Files.createTempDirectory(root, "unit-");
    String original = Files.readString(DEPLOYMENT.resolve("systemd/" + UNIT));
    Files.writeString(
        directory.resolve(UNIT),
        original
            .replace(
                "ExecStart=/opt/schubert-nk/current/operations/bin/schubert-nk-inbox-inspector",
                "ExecStart=/bin/true")
            .replace("WorkingDirectory=/opt/schubert-nk/current/api", "WorkingDirectory=" + root));
    Files.writeString(
        directory.resolve("postgresql.service"), "[Service]\nType=oneshot\nExecStart=/bin/true\n");
    Path dropins = Files.createDirectory(directory.resolve(UNIT + ".d"));
    for (Path profile : profiles) Files.copy(profile, dropins.resolve(profile.getFileName()));
    var result =
        execute(
            List.of(
                "/usr/bin/systemd-analyze",
                "verify",
                "--man=no",
                directory.resolve(UNIT).toString()),
            UnitSyntaxFixture.environment(directory));
    assertEquals(new Result(0, "", ""), result);
  }

  private static Map<String, List<String>> directives(String source) {
    var values = new LinkedHashMap<String, List<String>>();
    String section = "";
    for (String line : source.lines().toList()) {
      if (line.isBlank() || line.startsWith("#")) continue;
      if (line.startsWith("[")) {
        section = line.substring(1, line.length() - 1);
        continue;
      }
      String[] pair = line.split("=", 2);
      assertEquals(2, pair.length);
      values.computeIfAbsent(section + "." + pair[0], ignored -> new ArrayList<>()).add(pair[1]);
    }
    return values;
  }

  private record Result(int code, String out, String err) {}
}
