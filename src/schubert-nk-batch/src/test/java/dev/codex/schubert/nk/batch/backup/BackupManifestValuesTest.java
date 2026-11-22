package dev.codex.schubert.nk.batch.backup;

import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.END;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.RUN;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.START;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.ZERO;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.manifest;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.step;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.versionTokens;
import static dev.codex.schubert.nk.batch.backup.BackupManifestFixture.versions;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeoutException;
import org.junit.jupiter.api.Test;

/** BAK/BKO/UI251/SS341 6.4/343 5.3; SSC058/PG165; BAT178..185 in method order. */
final class BackupManifestValuesTest {
  @Test
  void completeIdentityAndDirectoryName() {
    var value = manifest();
    assertSame(RUN, value.run());
    assertEquals("20260913-000002-12345678-9abc-def0-8123-456789abcdef", value.directoryName());
    assertEquals(712, value.configurationBytes());
    assertEquals(713, value.totalBytes());
    assertEquals(90000, value.databaseStep().id());
    assertEquals(90001, value.configurationStep().id());
    assertEquals(BatchStep.BACKUP_DB, value.databaseStep().step());
    assertEquals(BatchStep.BACKUP_CONFIG, value.configurationStep().step());
    assertEquals(START, value.startedAt());
    assertEquals(END, value.contentFinishedAt());
    assertEquals(ZERO, value.recipientSha256());
    assertEquals(1, value.dump().size());
    assertEquals("a".repeat(64), value.dump().sha256());
    assertEquals(512, value.configuration().size());
    assertEquals("b".repeat(64), value.configuration().sha256());
    assertEquals(200, value.credentials().size());
    assertEquals("c".repeat(64), value.credentials().sha256());
  }

  @Test
  void fileDigestBoundsAndOverflow() {
    for (long size : new long[] {1, Long.MAX_VALUE}) {
      var v = new BackupFileDigest(size, ZERO);
      assertEquals(size, v.size());
      assertEquals(ZERO, v.sha256());
    }
    for (long size : new long[] {Long.MIN_VALUE, -1, 0})
      invalid(() -> new BackupFileDigest(size, ZERO));
    for (String h :
        List.of(
            "",
            "a".repeat(63),
            "a".repeat(65),
            "A".repeat(64),
            "g".repeat(64),
            "0".repeat(63) + "\n",
            "０".repeat(64))) {
      invalid(() -> new BackupFileDigest(1, h));
      invalid(() -> manifest(5, h));
    }
    assertEquals(
        Long.MAX_VALUE, manifest(6, new BackupFileDigest(Long.MAX_VALUE - 712, ZERO)).totalBytes());
    invalid(() -> manifest(6, new BackupFileDigest(Long.MAX_VALUE - 711, ZERO)));
    invalid(() -> manifest(7, new BackupFileDigest(Long.MAX_VALUE, ZERO)));
    invalid(() -> manifest(8, new BackupFileDigest(Long.MAX_VALUE, ZERO)));
    assertEquals(
        Long.MAX_VALUE - 1,
        manifest(7, new BackupFileDigest(Long.MAX_VALUE - 201, ZERO)).configurationBytes());
  }

  @Test
  void versionTokenBoundaries() {
    for (int i = 0; i < 8; i++) {
      final int index = i;
      if (i == 2) {
        for (String s : List.of("001", "999")) assertEquals(s, versions(i, s).schema());
        for (String s : List.of("", "000", "1", "01", "1000", "+01", "a01", "００１"))
          invalid(() -> versions(index, s));
      } else {
        for (String s : List.of("a", "0", "A", "a".repeat(128), "1aZ._+-"))
          assertEquals(s, tokens(versions(i, s)).get(i));
        for (String s :
            List.of(
                "",
                "a".repeat(129),
                ".x",
                "_x",
                "+x",
                "-x",
                "a b",
                "a\nb",
                "a\tb",
                "a/b",
                "a\\b",
                "あ",
                "a\"b",
                "a\u0000b")) invalid(() -> versions(index, s));
      }
    }
  }

  @Test
  void stepAndRunBinding() {
    for (BatchStep k : BatchStep.values()) {
      if (k != BatchStep.BACKUP_DB)
        invalid(() -> manifest(0, step(90000, RUN, k, 1, RUN.cutoff(), false)));
      if (k != BatchStep.BACKUP_CONFIG)
        invalid(() -> manifest(1, step(90001, RUN, k, 1, RUN.cutoff(), false)));
    }
    invalid(() -> manifest(0, step(90000, RUN, BatchStep.BACKUP_DB, 1, RUN.cutoff(), true)));
    invalid(() -> manifest(1, step(90001, RUN, BatchStep.BACKUP_CONFIG, 1, RUN.cutoff(), true)));
    invalid(() -> manifest(1, step(90000, RUN, BatchStep.BACKUP_CONFIG, 1, RUN.cutoff(), false)));
    for (BatchRun r :
        List.of(
            new BatchRun(new UUID(0, 0), RUN.cutoff()),
            new BatchRun(RUN.id(), RUN.cutoff().minusSeconds(1))))
      invalid(() -> manifest(1, step(90001, r, BatchStep.BACKUP_CONFIG, 1, RUN.cutoff(), false)));
    var v =
        manifest(
            0,
            step(1, RUN, BatchStep.BACKUP_DB, 99, START, false),
            1,
            step(999999999999L, RUN, BatchStep.BACKUP_CONFIG, 2, RUN.cutoff(), false));
    assertEquals(99, v.databaseStep().attempt());
    assertEquals(2, v.configurationStep().attempt());
    assertEquals(START, v.databaseStep().startedAt());
    assertEquals(RUN.cutoff(), v.configurationStep().startedAt());
  }

  @Test
  void timeAndPrecisionBoundaries() {
    var d = manifest().databaseStep();
    var c = manifest().configurationStep();
    invalid(() -> manifest(2, RUN.cutoff().minusNanos(1000)));
    invalid(() -> manifest(2, RUN.cutoff())); // DB passes; configuration step has not started.
    invalid(() -> manifest(2, START.plusNanos(1)));
    invalid(() -> manifest(2, Instant.MAX));
    invalid(() -> manifest(3, START.minusNanos(1000)));
    invalid(() -> manifest(3, END.plusNanos(1)));
    invalid(() -> manifest(3, Instant.MAX));
    assertEquals(START, manifest(3, START).contentFinishedAt());
    assertEquals(c.startedAt(), manifest(2, c.startedAt()).startedAt());
    assertEquals(
        d.startedAt(),
        manifest(
                1,
                step(90001, RUN, BatchStep.BACKUP_CONFIG, 1, RUN.cutoff(), false),
                2,
                d.startedAt())
            .startedAt());
    for (String time :
        List.of(
            "0001-01-01T00:00:00Z",
            "1582-10-04T00:00:00Z",
            "1582-10-15T00:00:00Z",
            "9999-12-31T14:59:59.999999Z")) {
      Instant t = Instant.parse(time);
      var r = new BatchRun(new UUID(-1, -1), t);
      var v =
          manifest(
              0,
              step(1, r, BatchStep.BACKUP_DB, 1, t, false),
              1,
              step(2, r, BatchStep.BACKUP_CONFIG, 1, t, false),
              2,
              t,
              3,
              t);
      String name =
          switch (time.substring(0, 10)) {
            case "0001-01-01" -> "00010101-091859";
            case "1582-10-04" -> "15821004-091859";
            case "1582-10-15" -> "15821015-091859";
            default -> "99991231-235959";
          };
      assertEquals(name + "-ffffffff-ffff-ffff-ffff-ffffffffffff", v.directoryName());
    }
    // IANA asia: historical LMT 9:18:59 until 1887-12-31T15:00Z, then Japan rules.
    // Independent literals, not ZoneId or directoryName used to create expected.
    for (var entry :
        Map.of(
                "1887-12-31T14:59:59Z", "18880101-001858",
                "1887-12-31T15:00:00Z", "18880101-000000",
                "1948-06-01T00:00:00Z", "19480601-100000",
                "1952-06-01T00:00:00Z", "19520601-090000")
            .entrySet()) {
      Instant t = Instant.parse(entry.getKey());
      var r = new BatchRun(new UUID(0, 0), t);
      var value =
          manifest(
              0,
              step(1, r, BatchStep.BACKUP_DB, 1, t, false),
              1,
              step(2, r, BatchStep.BACKUP_CONFIG, 1, t, false),
              2,
              t,
              3,
              t);
      assertEquals(
          entry.getValue() + "-00000000-0000-0000-0000-000000000000", value.directoryName());
    }
    var last = Instant.parse("9999-12-31T15:00:00Z");
    invalid(() -> manifest(2, last, 3, last));
    assertEquals(
        Instant.parse("9999-12-31T23:59:59.999999Z"),
        manifest(3, Instant.parse("9999-12-31T23:59:59.999999Z")).contentFinishedAt());
  }

  @Test
  void nullAndRedaction() {
    for (int i = 0; i < 9; i++) {
      final int index = i;
      assertThrows(NullPointerException.class, () -> manifest(index, null));
    }
    for (int i = 0; i < 8; i++) {
      final int index = i;
      assertThrows(NullPointerException.class, () -> versions(index, null));
    }
    assertThrows(NullPointerException.class, () -> new BackupFileDigest(1, null));
    assertEquals("BackupManifest[claims=<redacted>]", manifest().toString());
    assertEquals("BackupVersions[release=<redacted>]", manifest().versions().toString());
    assertEquals("BackupFileDigest[claim=<redacted>]", manifest().dump().toString());
  }

  @Test
  void immutableAccessors() {
    var a = manifest();
    var b = manifest();
    assertEquals(a, b);
    assertEquals(a.hashCode(), b.hashCode());
    assertNotEquals(a, manifest(3, END.plusSeconds(1)));
    assertThrows(UnsupportedOperationException.class, () -> versionTokens().set(0, "changed"));
    assertEquals(versionTokens(), tokens(a.versions()));
    assertSame(a.databaseStep().run(), a.run());
    assertNotSame(a.dump(), b.dump());
    assertEquals(a.dump(), b.dump());
    assertEquals(a.dump().hashCode(), b.dump().hashCode());
    assertEquals(a.versions(), b.versions());
    assertEquals(a.versions().hashCode(), b.versions().hashCode());
  }

  @Test
  void concurrentValueUse() throws InterruptedException, ExecutionException, TimeoutException {
    var value = manifest();
    var pool = Executors.newFixedThreadPool(8);
    try {
      var work = new ArrayList<Future<String>>();
      for (int i = 0; i < 64; i++)
        work.add(
            pool.submit(
                () -> {
                  assertEquals(713, value.totalBytes());
                  assertEquals(712, value.configurationBytes());
                  assertEquals(END, value.contentFinishedAt());
                  return value.directoryName();
                }));
      for (var f : work)
        assertEquals(
            "20260913-000002-12345678-9abc-def0-8123-456789abcdef",
            f.get(5, java.util.concurrent.TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, java.util.concurrent.TimeUnit.SECONDS));
    }
  }

  private static List<String> tokens(BackupVersions v) {
    return List.of(
        v.host(), v.app(), v.schema(), v.os(), v.jdk(), v.postgresql(), v.artemis(), v.age());
  }

  private static void invalid(org.junit.jupiter.api.function.Executable action) {
    var e = assertThrows(IllegalArgumentException.class, action);
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
    assertTrue(e.getMessage().startsWith("invalid backup "));
  }
}
