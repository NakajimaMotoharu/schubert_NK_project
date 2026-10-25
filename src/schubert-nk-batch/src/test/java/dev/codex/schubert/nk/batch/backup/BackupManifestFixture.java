package dev.codex.schubert.nk.batch.backup;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import java.time.Instant;
import java.util.UUID;

/** Public literal fixtures independent of the manifest codec; PG165/BAT178..193. */
public final class BackupManifestFixture {
  public static final String ZERO = "0".repeat(64);
  public static final String[] TOKENS = {
    "nk-pt", "0.1.0-SNAPSHOT", "020", "Ubuntu-26.04.1", "25.0.4", "18.6", "2.56.0", "1.2.1"
  };
  public static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("12345678-9abc-def0-8123-456789abcdef"),
          Instant.parse("2026-09-12T15:00:00Z"));
  public static final Instant START = Instant.parse("2026-09-12T15:00:02.123456Z");
  public static final Instant END = Instant.parse("2026-09-12T15:00:03.654321Z");

  private BackupManifestFixture() {}

  public static BackupVersions versions(String... tokens) {
    return new BackupVersions(
        tokens[0], tokens[1], tokens[2], tokens[3], tokens[4], tokens[5], tokens[6], tokens[7]);
  }

  public static BackupVersions versions(int index, String token) {
    String[] copy = TOKENS.clone();
    copy[index] = token;
    return versions(copy);
  }

  public static BatchStepAttempt step(
      long id, BatchRun run, BatchStep kind, int attempt, Instant start, boolean skipped) {
    return new BatchStepAttempt(id, run, kind, attempt, start, skipped);
  }

  public static BackupManifest manifest(Object... changes) {
    Object[] fields = {
      step(90000, RUN, BatchStep.BACKUP_DB, 1, RUN.cutoff(), false),
      step(90001, RUN, BatchStep.BACKUP_CONFIG, 1, RUN.cutoff().plusSeconds(1), false),
      START,
      END,
      versions(TOKENS),
      ZERO,
      new BackupFileDigest(1, "a".repeat(64)),
      new BackupFileDigest(512, "b".repeat(64)),
      new BackupFileDigest(200, "c".repeat(64))
    };
    for (int i = 0; i < changes.length; i += 2) fields[(Integer) changes[i]] = changes[i + 1];
    return new BackupManifest(
        (BatchStepAttempt) fields[0],
        (BatchStepAttempt) fields[1],
        (Instant) fields[2],
        (Instant) fields[3],
        (BackupVersions) fields[4],
        (String) fields[5],
        (BackupFileDigest) fields[6],
        (BackupFileDigest) fields[7],
        (BackupFileDigest) fields[8]);
  }
}
