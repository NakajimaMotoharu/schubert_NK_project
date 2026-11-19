package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-CHR-PREFLIGHT-FS-001, integrated with the admitted offline tests in one JVM. */
final class GateOwnedFileStoreContract {
  private static final long REQUIRED_BYTES = 21_474_836_480L;
  private static final Set<String> REPORT_FIELDS =
      Set.of(
          "status",
          "failures",
          "freeBytes",
          "credentialPermission",
          "hostAllowlist",
          "projectRoot",
          "runtimeRoot",
          "postgresControl",
          "postgresData");

  @Test
  void admitsOnlyTheOwnedRealFileStoreThroughThePublicCli(@TempDir Path owned) throws Exception {
    Path current = Files.createDirectories(owned.resolve("fixture-current/program/app/src"));
    Path currentRoot = current.getParent().getParent().getParent();
    Path asset = Files.createDirectory(owned.resolve("fixture-assets"));
    Path data = Files.createDirectory(owned.resolve("fixture-database-data"));
    Path runtime = Files.createDirectory(owned.resolve("fixture-runtime"));
    Path users =
        Files.createFile(
            owned.resolve("fixture-users"),
            PosixFilePermissions.asFileAttribute(PosixFilePermissions.fromString("rw-------")));
    Path plainJar = fixtureFile(owned, "fixture-current.jar");
    Path control = fixtureFile(owned, "fixture-postgres-control");
    Path caddy = fixtureFile(owned, "fixture-caddy");
    assertFalse(Files.isExecutable(control));
    assertFalse(Files.isExecutable(caddy));
    assertFalse(Files.isExecutable(plainJar));
    Path report = owned.resolve("preflight.json");
    Map<String, String> options = new LinkedHashMap<>();
    options.put("chr.projectRoot", owned.toString());
    options.put("chr.currentRoot", currentRoot.toString());
    options.put("chr.currentJar", plainJar.toString());
    options.put("chr.assetRoot", asset.toString());
    options.put("chr.usersFile", users.toString());
    options.put(
        "chr.javaExecutable", Path.of(System.getProperty("java.home"), "bin", "java").toString());
    options.put("chr.caddyExecutable", caddy.toString());
    options.put("chr.runtimeRoot", runtime.toString());
    options.put("chr.pgCtl", control.toString());
    options.put("chr.pgData", data.toString());
    options.put("chr.pgLog", owned.resolve("fixture-diagnostics/postgres.log").toString());
    options.put("chr.pgSocket", runtime.resolve("fixture-postgres-socket").toString());
    options.put("chr.dbUrl", "jdbc:postgresql://127.0.0.1:15432/synthetic");
    options.put("chr.appPort", "18081");
    options.put("chr.proxyPort", "18082");

    var saved = new LinkedHashMap<String, String>();
    options.forEach((name, value) -> saved.put(name, System.getProperty(name)));
    long before = Files.getFileStore(runtime).getUsableSpace();
    assertTrue(before >= REQUIRED_BYTES);
    try {
      options.forEach(System::setProperty);
      GateCli.main(new String[] {"preflight", report.toString()});
    } finally {
      saved.forEach(
          (name, value) -> {
            if (value == null) {
              System.clearProperty(name);
            } else {
              System.setProperty(name, value);
            }
          });
    }
    long after = Files.getFileStore(runtime).getUsableSpace();
    assertTrue(after >= REQUIRED_BYTES);
    var json = new ObjectMapper().readTree(report.toFile());
    var fields = new HashSet<String>();
    json.fieldNames().forEachRemaining(fields::add);
    assertEquals(REPORT_FIELDS, fields);
    assertEquals("PASS", json.required("status").textValue());
    assertTrue(json.required("failures").isArray());
    assertTrue(json.required("failures").isEmpty());
    assertTrue(json.required("freeBytes").isIntegralNumber());
    assertTrue(json.required("freeBytes").longValue() >= REQUIRED_BYTES);
    assertEquals("0600", json.required("credentialPermission").textValue());
    assertEquals(
        new ObjectMapper().readTree("[\"localhost\",\"127.0.0.1\"]"),
        json.required("hostAllowlist"));
    assertEquals(owned.toString(), json.required("projectRoot").textValue());
    assertEquals(runtime.toString(), json.required("runtimeRoot").textValue());
    assertEquals(control.toString(), json.required("postgresControl").textValue());
    assertEquals(data.toString(), json.required("postgresData").textValue());
  }

  private static Path fixtureFile(Path root, String name) throws Exception {
    return Files.writeString(root.resolve(name), "OWNED SYNTHETIC FIXTURE ONLY\n");
  }
}
