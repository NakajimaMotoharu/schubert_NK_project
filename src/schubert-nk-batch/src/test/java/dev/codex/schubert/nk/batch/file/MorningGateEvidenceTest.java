package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.bootstrap.SchemaHistoryAdmission;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * SSC129/ISSPG001/ISSREL001. Literal SS field order and independent UTF8 conversion; no authority.
 */
final class MorningGateEvidenceTest {
  private static final String MORNING = "1".repeat(32);
  private static final String BROKER = "2".repeat(32);
  private static final StartupPermitRecords.Epoch EPOCH =
      new StartupPermitRecords.Epoch(
          StartupPermitRecords.State.INVALID,
          UUID.fromString("11111111-2222-4333-8444-555555555555"),
          UUID.fromString("22222222-2222-4333-8444-555555555555"),
          new MaintenanceActivation(
              new BatchRun(
                  UUID.fromString("33333333-2222-4333-8444-555555555555"),
                  Instant.parse("2026-09-27T15:00:00Z")),
              UUID.fromString("44444444-2222-4333-8444-555555555555")),
          Optional.empty());
  private static final String HEADER =
      """
      boot_id=11111111-2222-4333-8444-555555555555
      epoch_id=22222222-2222-4333-8444-555555555555
      run_id=33333333-2222-4333-8444-555555555555
      cutoff_utc=2026-09-27T15:00:00.000000Z
      activation_id=44444444-2222-4333-8444-555555555555
      morning_invocation_id=11111111111111111111111111111111
      broker_invocation_id=22222222222222222222222222222222
      """;
  private static final List<SchemaHistoryAdmission.Row> ROWS =
      List.of(
          new SchemaHistoryAdmission.Row(0, null, "SCHEMA", "\"schubert_meta\"", null, true),
          new SchemaHistoryAdmission.Row(1, "001", "SQL", "V001__first.sql", -170000001, true));

  private static RootReleaseAdmission.DatabaseInspection facts(
      String version, Map<String, String> artifacts) {
    var build = Map.of("jdkVendor", "公開 Vendor", "jdkVersion", "25.0.4", "mavenVersion", "3.9.12");
    var platform =
        Map.of(
            "osId", "ubuntu", "osVersion", "26.04", "architecture", "x86_64", "javaFeature", "25");
    var runtime = new HashMap<>(platform);
    runtime.put("jdkVendor", "公開 Vendor");
    runtime.put("jdkVersion", "25.0.4");
    return new RootReleaseAdmission.DatabaseInspection(
        new StartupReleaseManifest.Contents(
            version,
            "a".repeat(64),
            ROWS,
            build,
            platform,
            Map.of(
                "app",
                "1",
                "protocol",
                "1",
                "storage",
                "1",
                "bootstrap",
                "1",
                "schema",
                "1",
                "config",
                "1"),
            artifacts),
        ROWS,
        runtime);
  }

  private static Map<String, String> artifacts() {
    return Map.of(
        "VERSION",
        "b".repeat(64),
        "api/api.jar",
        "c".repeat(64),
        "operations/batch.jar",
        "d".repeat(64),
        "web/web.jar",
        "e".repeat(64));
  }

  private static MorningDatabaseSession.DatabaseObservation database() {
    return new MorningDatabaseSession.DatabaseObservation(
        "schubert_batch",
        "schubert_batch",
        "schubert_nk",
        true,
        false,
        2,
        false,
        true,
        facts("PUBLIC", artifacts()));
  }

  @Test
  void issPg001LiteralSixColumnSignedChecksumGolden() throws Exception {
    String expected =
        "NKPG1\n"
            + HEADER
            + """
        login_role=73636875626572745f6261746368
        effective_role=73636875626572745f6261746368
        database=73636875626572745f6e6b
        auto_commit=1
        read_only=0
        isolation=2
        recovery=0
        advisory_lock=1
        schema_rows=2
        SCHEMA|0|-|534348454d41|2273636875626572745f6d65746122|-|1
        SCHEMA|1|001|53514c|563030315f5f66697273742e73716c|-170000001|1
        """;
    byte[] actual = MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, database());
    assertArrayEquals(expected.getBytes(StandardCharsets.US_ASCII), actual);
    actual[0] = 'X';
    assertEquals('N', MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, database())[0]);
  }

  @Test
  void issRel001FixedMapOrderUnicodeWithoutNormalizationAndSortedArtifacts() throws Exception {
    var expected =
        new StringBuilder("NKREL1\n" + HEADER)
            .append("release_version=5055424c4943\nmanifest_sha256=")
            .append("a".repeat(64))
            .append("\napi_config_sha256=")
            .append("f".repeat(64))
            .append("\nweb_config_sha256=")
            .append("9".repeat(64))
            .append('\n');
    // Independently transcribed SS rows; none are read back from Production inputs/getters.
    for (String line :
        List.of(
            "VERSION|app|1",
            "VERSION|protocol|1",
            "VERSION|storage|1",
            "VERSION|bootstrap|1",
            "VERSION|schema|1",
            "VERSION|config|1",
            "BUILD|jdkVendor|公開 Vendor",
            "BUILD|jdkVersion|25.0.4",
            "BUILD|mavenVersion|3.9.12",
            "PLATFORM|osId|ubuntu",
            "PLATFORM|osVersion|26.04",
            "PLATFORM|architecture|x86_64",
            "PLATFORM|javaFeature|25",
            "RUNTIME|osId|ubuntu",
            "RUNTIME|osVersion|26.04",
            "RUNTIME|architecture|x86_64",
            "RUNTIME|javaFeature|25",
            "RUNTIME|jdkVendor|公開 Vendor",
            "RUNTIME|jdkVersion|25.0.4")) {
      String[] field = line.split("\\|", -1);
      expected.append(field[0]).append('|').append(field[1]).append('|');
      for (byte value : field[2].getBytes(StandardCharsets.UTF_8))
        expected.append(String.format(Locale.ROOT, "%02x", value & 255));
      expected.append('\n');
    }
    for (String[] item :
        List.of(
            new String[] {"VERSION", "b"},
            new String[] {"api/api.jar", "c"},
            new String[] {"operations/batch.jar", "d"},
            new String[] {"web/web.jar", "e"})) {
      expected.append("ARTIFACT|");
      for (byte value : item[0].getBytes(StandardCharsets.US_ASCII))
        expected.append(String.format(Locale.ROOT, "%02x", value & 255));
      expected.append('|').append(item[1].repeat(64)).append('\n');
    }
    assertArrayEquals(
        expected.toString().getBytes(StandardCharsets.US_ASCII),
        MorningGateEvidence.release(
            EPOCH, MORNING, BROKER, facts("PUBLIC", artifacts()), "f".repeat(64), "9".repeat(64)));
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.release(
                EPOCH,
                MORNING,
                BROKER,
                facts("\ud800", artifacts()),
                "f".repeat(64),
                "9".repeat(64)));
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.release(
                EPOCH,
                MORNING,
                BROKER,
                facts("X".repeat(32768), artifacts()),
                "f".repeat(64),
                "9".repeat(64)));
  }

  @Test
  void issPg002WrongIdentityReadonlyRecoveryIsolationAndOwnerBindingsNeverEncode() {
    for (int field = 0; field < 8; field++) {
      var wrong =
          new MorningDatabaseSession.DatabaseObservation(
              field == 0 ? "wrong" : "schubert_batch",
              field == 1 ? "wrong" : "schubert_batch",
              field == 2 ? "wrong" : "schubert_nk",
              field != 3,
              field == 4,
              field == 5 ? 8 : 2,
              field == 6,
              field != 7,
              facts("PUBLIC", artifacts()));
      assertThrows(
          IOException.class, () -> MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, wrong));
    }
    for (String wrong : List.of("", "0".repeat(32), "A".repeat(32), "1".repeat(31))) {
      assertThrows(
          IOException.class, () -> MorningGateEvidence.postgres(EPOCH, wrong, BROKER, database()));
      assertThrows(
          IOException.class, () -> MorningGateEvidence.postgres(EPOCH, MORNING, wrong, database()));
    }
    assertThrows(
        IOException.class, () -> MorningGateEvidence.postgres(EPOCH, MORNING, MORNING, database()));
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.postgres(
                EPOCH.issued("a".repeat(64)), MORNING, BROKER, database()));
    assertThrows(
        NullPointerException.class,
        () -> MorningGateEvidence.postgres(null, MORNING, BROKER, database()));
    assertThrows(
        NullPointerException.class,
        () -> MorningGateEvidence.postgres(EPOCH, null, BROKER, database()));
    assertThrows(
        NullPointerException.class,
        () -> MorningGateEvidence.postgres(EPOCH, MORNING, null, database()));
    assertThrows(
        NullPointerException.class,
        () -> MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, null));
    assertThrows(
        NullPointerException.class,
        () ->
            MorningGateEvidence.release(
                EPOCH, MORNING, BROKER, null, "a".repeat(64), "b".repeat(64)));
  }

  @Test
  void issRel002MalformedHashesMapsAndArtifactPathsAreRejected() {
    var good = facts("PUBLIC", artifacts());
    var contents = good.contents();
    for (String wrong : List.of("", "a".repeat(63), "A".repeat(64), "g".repeat(64))) {
      assertThrows(
          IOException.class,
          () -> MorningGateEvidence.release(EPOCH, MORNING, BROKER, good, wrong, "9".repeat(64)));
      assertThrows(
          IOException.class,
          () -> MorningGateEvidence.release(EPOCH, MORNING, BROKER, good, "f".repeat(64), wrong));
      var badHash = new HashMap<>(artifacts());
      badHash.put("api/api.jar", wrong);
      assertThrows(
          IOException.class,
          () ->
              MorningGateEvidence.release(
                  EPOCH,
                  MORNING,
                  BROKER,
                  facts("PUBLIC", badHash),
                  "f".repeat(64),
                  "9".repeat(64)));
    }
    for (String wrong : List.of("", "/absolute", "a\\b", "a//b", "a/./b", "a/../b", "a ", "日本語")) {
      var badPath = new HashMap<>(artifacts());
      badPath.put(wrong, "b".repeat(64));
      assertThrows(
          IOException.class,
          () ->
              MorningGateEvidence.release(
                  EPOCH,
                  MORNING,
                  BROKER,
                  facts("PUBLIC", badPath),
                  "f".repeat(64),
                  "9".repeat(64)));
    }
    var missingArtifact = new HashMap<>(artifacts());
    missingArtifact.remove("VERSION");
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.release(
                EPOCH,
                MORNING,
                BROKER,
                facts("PUBLIC", missingArtifact),
                "f".repeat(64),
                "9".repeat(64)));
    for (int slot = 0; slot < 4; slot++) {
      var build = new HashMap<>(contents.build());
      var platform = new HashMap<>(contents.platform());
      var versions = new HashMap<>(contents.versions());
      var runtime = new HashMap<>(good.runtime());
      var selected = List.of(versions, build, platform, runtime).get(slot);
      selected.remove(List.of("app", "jdkVendor", "osId", "osId").get(slot));
      var wrong =
          new RootReleaseAdmission.DatabaseInspection(
              new StartupReleaseManifest.Contents(
                  "PUBLIC", "a".repeat(64), ROWS, build, platform, versions, artifacts()),
              ROWS,
              runtime);
      assertThrows(
          IOException.class,
          () ->
              MorningGateEvidence.release(
                  EPOCH, MORNING, BROKER, wrong, "f".repeat(64), "9".repeat(64)));
      selected.put("unexpected", "1");
      var extra =
          new RootReleaseAdmission.DatabaseInspection(
              new StartupReleaseManifest.Contents(
                  "PUBLIC", "a".repeat(64), ROWS, build, platform, versions, artifacts()),
              ROWS,
              runtime);
      assertThrows(
          IOException.class,
          () ->
              MorningGateEvidence.release(
                  EPOCH, MORNING, BROKER, extra, "f".repeat(64), "9".repeat(64)));
    }
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.release(
                EPOCH, MORNING, BROKER, facts("", artifacts()), "f".repeat(64), "9".repeat(64)));
  }

  @Test
  void issPg003MissingOrReorderedSchemaAndNilOwnershipNeverEncode() {
    var good = facts("PUBLIC", artifacts());
    for (var rows :
        List.of(
            List.<SchemaHistoryAdmission.Row>of(),
            List.of(ROWS.get(1), ROWS.get(0)),
            List.of(ROWS.get(0)))) {
      var wrong =
          new RootReleaseAdmission.DatabaseInspection(good.contents(), rows, good.runtime());
      var db =
          new MorningDatabaseSession.DatabaseObservation(
              "schubert_batch",
              "schubert_batch",
              "schubert_nk",
              true,
              false,
              2,
              false,
              true,
              wrong);
      assertThrows(
          IOException.class, () -> MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, db));
    }
    for (boolean nilRun : List.of(true, false)) {
      var activation =
          new MaintenanceActivation(
              new BatchRun(
                  nilRun ? new UUID(0, 0) : EPOCH.activation().run().id(),
                  EPOCH.activation().run().cutoff()),
              nilRun ? EPOCH.activation().id() : new UUID(0, 0));
      var wrong =
          new StartupPermitRecords.Epoch(
              StartupPermitRecords.State.INVALID,
              EPOCH.boot(),
              EPOCH.epoch(),
              activation,
              Optional.empty());
      assertThrows(
          IOException.class,
          () -> MorningGateEvidence.postgres(wrong, MORNING, BROKER, database()));
    }
  }
}
