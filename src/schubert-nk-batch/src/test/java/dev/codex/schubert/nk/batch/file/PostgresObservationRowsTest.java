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
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS343SSC129; PG-D508; PT-OPS-PG-ROWS-001. Serialization only, never DB/admission/issuer IO. */
final class PostgresObservationRowsTest {
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

  private static SchemaHistoryAdmission.Row schema() {
    return new SchemaHistoryAdmission.Row(0, null, "SCHEMA", "\"schubert_meta\"", null, true);
  }

  private static SchemaHistoryAdmission.Row sql(int rank) {
    String version = String.format(Locale.ROOT, "%03d", rank);
    return new SchemaHistoryAdmission.Row(
        rank, version, "SQL", "V" + version + "__row.sql", -rank, true);
  }

  private static MorningDatabaseSession.DatabaseObservation observation(
      List<SchemaHistoryAdmission.Row> rows) {
    var build =
        Map.of("jdkVendor", "PublicVendor", "jdkVersion", "25.0.4", "mavenVersion", "3.9.12");
    var platform =
        Map.of(
            "osId", "ubuntu", "osVersion", "26.04", "architecture", "x86_64", "javaFeature", "25");
    var versions =
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
            "1");
    var artifacts =
        Map.of(
            "VERSION",
            "b".repeat(64),
            "api/api.jar",
            "c".repeat(64),
            "operations/batch.jar",
            "d".repeat(64),
            "web/web.jar",
            "e".repeat(64));
    var contents =
        new StartupReleaseManifest.Contents(
            "PUBLIC", "a".repeat(64), rows, build, platform, versions, artifacts);
    var runtime = new HashMap<>(platform);
    runtime.put("jdkVendor", "PublicVendor");
    runtime.put("jdkVersion", "25.0.4");
    var release = new RootReleaseAdmission.DatabaseInspection(contents, rows, runtime);
    return new MorningDatabaseSession.DatabaseObservation(
        "schubert_batch", "schubert_batch", "schubert_nk", true, false, 2, false, true, release);
  }

  @Test
  void pgRows001MaximumFullGoldenAndOversizeOrSameBomRankGapRejected() throws Exception {
    var rows = new ArrayList<SchemaHistoryAdmission.Row>();
    rows.add(schema());
    for (int rank = 1; rank <= 999; rank++) rows.add(sql(rank));
    var normal = observation(rows);
    var expected =
        new StringBuilder(
            """
        NKPG1
        boot_id=11111111-2222-4333-8444-555555555555
        epoch_id=22222222-2222-4333-8444-555555555555
        run_id=33333333-2222-4333-8444-555555555555
        cutoff_utc=2026-09-27T15:00:00.000000Z
        activation_id=44444444-2222-4333-8444-555555555555
        morning_invocation_id=11111111111111111111111111111111
        broker_invocation_id=22222222222222222222222222222222
        login_role=73636875626572745f6261746368
        effective_role=73636875626572745f6261746368
        database=73636875626572745f6e6b
        auto_commit=1
        read_only=0
        isolation=2
        recovery=0
        advisory_lock=1
        schema_rows=1000
        SCHEMA|0|-|534348454d41|2273636875626572745f6d65746122|-|1
        """);
    // Independent SS field ordering and ASCII/UTF8 conversion; no production encoder/Row reads.
    for (int rank = 1; rank <= 999; rank++) {
      String version = String.format(Locale.ROOT, "%03d", rank);
      String script = "V" + version + "__row.sql";
      expected
          .append("SCHEMA|")
          .append(rank)
          .append('|')
          .append(version)
          .append("|53514c|")
          .append(HexFormat.of().formatHex(script.getBytes(StandardCharsets.UTF_8)))
          .append('|')
          .append(-rank)
          .append("|1\n");
    }
    assertArrayEquals(
        expected.toString().getBytes(StandardCharsets.US_ASCII),
        MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, normal));
    assertEquals(1000, rows.size());
    assertEquals(rows, normal.release().schemaRows());
    assertEquals(rows, normal.release().contents().migrations());

    rows.add(sql(999));
    var tooMany = observation(rows);
    assertEquals(1001, tooMany.release().schemaRows().size());
    assertEquals(tooMany.release().contents().migrations(), tooMany.release().schemaRows());
    assertThrows(
        IOException.class, () -> MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, tooMany));
    assertEquals(1000, normal.release().schemaRows().size());

    var gap = observation(List.of(schema(), sql(2)));
    assertEquals(gap.release().contents().migrations(), gap.release().schemaRows());
    assertEquals(2, gap.release().schemaRows().get(1).installedRank());
    assertThrows(
        IOException.class, () -> MorningGateEvidence.postgres(EPOCH, MORNING, BROKER, gap));
  }
}
