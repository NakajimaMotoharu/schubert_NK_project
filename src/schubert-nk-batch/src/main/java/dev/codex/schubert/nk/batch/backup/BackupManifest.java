package dev.codex.schubert.nk.batch.backup;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Locale;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Consistent claims only; caller must verify files/DB/root ownership. BAK/BKO/UI251/SS341 6.4/343
 * 5.3; PG165/BAT178..185.
 */
@NullMarked
public record BackupManifest(
    BatchStepAttempt databaseStep,
    BatchStepAttempt configurationStep,
    Instant startedAt,
    Instant contentFinishedAt,
    BackupVersions versions,
    String recipientSha256,
    BackupFileDigest dump,
    BackupFileDigest configuration,
    BackupFileDigest credentials) {
  private static final int MAXIMUM_DIRECTORY_YEAR = 9999;

  private static final ZoneId JST = ZoneId.of("Asia/Tokyo");
  private static final DateTimeFormatter NAME =
      DateTimeFormatter.ofPattern("uuuuMMdd-HHmmss", Locale.ROOT).withZone(JST);

  public BackupManifest {
    Objects.requireNonNull(databaseStep, "database step");
    Objects.requireNonNull(configurationStep, "configuration step");
    Objects.requireNonNull(startedAt, "content start");
    Objects.requireNonNull(contentFinishedAt, "content finish");
    Objects.requireNonNull(versions, "versions");
    Objects.requireNonNull(recipientSha256, "recipient fingerprint");
    Objects.requireNonNull(dump, "dump claim");
    Objects.requireNonNull(configuration, "configuration claim");
    Objects.requireNonNull(credentials, "credentials claim");
    if (databaseStep.step() != BatchStep.BACKUP_DB
        || configurationStep.step() != BatchStep.BACKUP_CONFIG
        || databaseStep.skipped()
        || configurationStep.skipped()
        || databaseStep.id() == configurationStep.id()
        || !databaseStep.run().equals(configurationStep.run()))
      throw new IllegalArgumentException("invalid backup step binding");
    time(startedAt, databaseStep.startedAt());
    time(startedAt, configurationStep.startedAt());
    time(contentFinishedAt, startedAt);
    if (startedAt.atZone(JST).getYear() > MAXIMUM_DIRECTORY_YEAR)
      throw new IllegalArgumentException("invalid backup directory year");
    if (!recipientSha256.matches("[0-9a-f]{64}"))
      throw new IllegalArgumentException("invalid backup recipient fingerprint");
    if (configuration.size() > Long.MAX_VALUE - credentials.size()
        || dump.size() > Long.MAX_VALUE - configuration.size() - credentials.size())
      throw new IllegalArgumentException("invalid backup total size");
  }

  private static void time(Instant value, Instant minimum) {
    if (value.isBefore(minimum)
        || value.isAfter(Instant.parse("9999-12-31T23:59:59.999999Z"))
        || value.getNano() % 1000 != 0)
      throw new IllegalArgumentException("invalid backup content time");
  }

  public BatchRun run() {
    return databaseStep.run();
  }

  public String directoryName() {
    return NAME.format(startedAt) + "-" + run().id();
  }

  public long configurationBytes() {
    return configuration.size() + credentials.size();
  }

  public long totalBytes() {
    return dump.size() + configurationBytes();
  }

  @Override
  public String toString() {
    return "BackupManifest[claims=<redacted>]";
  }
}
