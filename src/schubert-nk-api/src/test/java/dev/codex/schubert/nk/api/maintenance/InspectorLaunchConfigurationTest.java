package dev.codex.schubert.nk.api.maintenance;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.Path;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-DB-INBOX-221..224; literal canonical input and boundary oracles. */
final class InspectorLaunchConfigurationTest {
  private static final String FIXTURE_CREDENTIALS_DIRECTORY_68135E08 = "CREDENTIALS_DIRECTORY";
  private static final String FIXTURE_NK_INSPECTOR_CUTOFF_26CA90AC = "NK_INSPECTOR_CUTOFF";
  private static final String FIXTURE_NK_INSPECTOR_FINGERPRINT_VERSIONS_5584EF87 =
      "NK_INSPECTOR_FINGERPRINT_VERSIONS";
  private static final String FIXTURE_UNTRUSTED_6FC6869D = "UNTRUSTED";
  static final String ID = "00000000-0000-0000-0000-00000000002a";
  static final String CUTOFF = "2026-09-17T00:00:00.123Z";

  static Map<String, String> environment(Path root) {
    var env = new HashMap<String, String>();
    env.put(FIXTURE_CREDENTIALS_DIRECTORY_68135E08, root.toString());
    env.put("NK_INSPECTOR_DB_URL", "jdbc:postgresql://127.0.0.1:5432/schubert_nk");
    env.put("NK_INSPECTOR_RUN_ID", ID);
    env.put(FIXTURE_NK_INSPECTOR_CUTOFF_26CA90AC, CUTOFF);
    env.put(FIXTURE_NK_INSPECTOR_FINGERPRINT_VERSIONS_5584EF87, "fp1,old-v.2");
    return env;
  }

  private static Map<String, String> valid() {
    return environment(Path.of("/run/credentials/inspector"));
  }

  @Test
  void validConfiguration() throws Exception {
    var env = valid();
    env.put("UNRELATED_PRIVATE_VALUE", "UNTRUSTED_DO_NOT_COPY");
    var parsed = InspectorLaunchConfiguration.read(new String[0], env);
    assertEquals(Path.of("/run/credentials/inspector"), parsed.settings().credentialRoot());
    assertEquals("jdbc:postgresql://127.0.0.1:5432/schubert_nk", parsed.settings().databaseUrl());
    assertEquals(UUID.fromString(ID), parsed.run().id());
    assertEquals(Instant.parse(CUTOFF), parsed.run().cutoff());
    assertEquals(Set.of("fp1", "old-v.2"), parsed.settings().fingerprintVersions());
    assertEquals("InspectorLaunchConfiguration[REDACTED]", parsed.toString());
    assertThrows(
        NullPointerException.class, () -> new InspectorLaunchConfiguration(null, parsed.run()));
    assertThrows(
        NullPointerException.class,
        () -> new InspectorLaunchConfiguration(parsed.settings(), null));
    assertThrows(NullPointerException.class, () -> InspectorLaunchConfiguration.read(null, env));
    assertThrows(
        NullPointerException.class, () -> InspectorLaunchConfiguration.read(new String[0], null));
  }

  @Test
  void missingUnknownAndArguments() {
    for (String key : valid().keySet()) {
      var missing = valid();
      missing.remove(key);
      invalid(new String[0], missing);
      var absent = valid();
      absent.put(key, null);
      invalid(new String[0], absent);
      var empty = valid();
      empty.put(key, "");
      invalid(new String[0], empty);
    }
    for (String key :
        List.of(
            "NK_INSPECTOR_BAD",
            "nk_inspector_db_url",
            "NK_INSPECTOR",
            "NK_INSPECTORX",
            "credentials_directory")) {
      var env = valid();
      env.put(key, FIXTURE_UNTRUSTED_6FC6869D);
      invalid(new String[0], env);
    }
    var nullKey = valid();
    nullKey.put(null, FIXTURE_UNTRUSTED_6FC6869D);
    invalid(new String[0], nullKey);
    invalid(new String[] {"--help"}, valid());
    invalid(new String[] {null}, valid());
  }

  @Test
  void scalarBoundaries() throws Exception {
    var maximum =
        Map.of(
            FIXTURE_CREDENTIALS_DIRECTORY_68135E08,
            4096,
            "NK_INSPECTOR_DB_URL",
            256,
            "NK_INSPECTOR_RUN_ID",
            36,
            FIXTURE_NK_INSPECTOR_CUTOFF_26CA90AC,
            32,
            FIXTURE_NK_INSPECTOR_FINGERPRINT_VERSIONS_5584EF87,
            65536);
    for (var entry : maximum.entrySet()) {
      var env = valid();
      env.put(entry.getKey(), "x".repeat(entry.getValue() + 1));
      invalid(new String[0], env);
      for (String extra : List.of("\0", "\r", "\n")) {
        env = valid();
        env.put(entry.getKey(), "x" + extra);
        invalid(new String[0], env);
      }
    }
    for (String root : List.of("/", "relative", "/run/../credential"))
      changed(FIXTURE_CREDENTIALS_DIRECTORY_68135E08, root);
    for (String url :
        List.of(
            "jdbc:postgresql://localhost:5432/db",
            "jdbc:postgresql://127.0.0.1:65536/db",
            "jdbc:postgresql://127.0.0.1:5432/db?x=y")) changed("NK_INSPECTOR_DB_URL", url);
    for (String id :
        List.of("0-0-0-0-1", ID.toUpperCase(Locale.ROOT), FIXTURE_UNTRUSTED_6FC6869D, ID + "x"))
      changed("NK_INSPECTOR_RUN_ID", id);
    for (String date :
        List.of(
            FIXTURE_UNTRUSTED_6FC6869D,
            "2026-09-17T09:00:00.123+09:00",
            "2026-09-17T00:00:00.123000Z",
            "2026-09-17T00:00:00.123456789Z",
            "0000-01-01T00:00:00Z",
            "+10000-01-01T00:00:00Z",
            "2016-12-31T23:59:60Z")) changed(FIXTURE_NK_INSPECTOR_CUTOFF_26CA90AC, date);
    for (String date : List.of("0001-01-01T00:00:00Z", "9999-12-31T23:59:59.999999Z")) {
      var env = valid();
      env.put(FIXTURE_NK_INSPECTOR_CUTOFF_26CA90AC, date);
      assertEquals(
          date, InspectorLaunchConfiguration.read(new String[0], env).run().cutoff().toString());
    }
    var longRoot = valid();
    longRoot.put(FIXTURE_CREDENTIALS_DIRECTORY_68135E08, "/" + "x".repeat(4095));
    assertEquals(
        4096,
        InspectorLaunchConfiguration.read(new String[0], longRoot)
            .settings()
            .credentialRoot()
            .toString()
            .length());
  }

  @Test
  void versionAndSnapshotContracts() throws Exception {
    for (String names :
        List.of(",fp1", "fp1,", "fp1,,fp2", "fp1,fp1", "-v", "a b", "é", "x".repeat(17)))
      changed(FIXTURE_NK_INSPECTOR_FINGERPRINT_VERSIONS_5584EF87, names);
    var env = valid();
    env.put(FIXTURE_NK_INSPECTOR_FINGERPRINT_VERSIONS_5584EF87, "v," + "x".repeat(16));
    var parsed = InspectorLaunchConfiguration.read(new String[0], env);
    env.clear();
    assertEquals(Set.of("v", "x".repeat(16)), parsed.settings().fingerprintVersions());
    assertThrows(
        UnsupportedOperationException.class, () -> parsed.settings().fingerprintVersions().clear());
    assertEquals(ID, parsed.run().id().toString());
  }

  private static void changed(String key, String value) {
    var env = valid();
    env.put(key, value);
    invalid(new String[0], env);
  }

  private static void invalid(String[] args, Map<String, String> env) {
    var failure =
        assertThrows(
            InspectorLaunchConfiguration.Invalid.class,
            () -> InspectorLaunchConfiguration.read(args, env));
    assertEquals("inspector configuration is invalid", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
