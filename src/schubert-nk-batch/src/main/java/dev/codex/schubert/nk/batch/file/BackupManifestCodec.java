package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupVersions;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import java.nio.charset.StandardCharsets;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.Arrays;
import java.util.Locale;
import java.util.Objects;
import java.util.UUID;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed canonical claims only, not backup authentication. BAK/BKO/UI251/SS341 6.4/343 5.3;
 * PG165/BAT186..193.
 */
@NullMarked
public final class BackupManifestCodec {
  private static final DateTimeFormatter TIME =
      new DateTimeFormatterBuilder().appendInstant(6).toFormatter(Locale.ROOT);
  private static final String FORMAT =
      "{\"format\":\"NKBACKUP1\",\"database\":\"schubert_nk\",\"runId\":\"%s\",\"cutoff\":\"%s\",\"startedAt\":\"%s\",\"contentFinishedAt\":\"%s\",\"databaseStep\":{\"id\":%s,\"attempt\":%s,\"startedAt\":\"%s\"},\"configurationStep\":{\"id\":%s,\"attempt\":%s,\"startedAt\":\"%s\"},\"versions\":{\"host\":\"%s\",\"app\":\"%s\",\"schema\":\"%s\",\"os\":\"%s\",\"jdk\":\"%s\",\"postgresql\":\"%s\",\"artemis\":\"%s\",\"age\":\"%s\"},\"recipientSha256\":\"%s\",\"files\":{\"schubert_nk.dump\":{\"size\":%s,\"sha256\":\"%s\"},\"config.tar\":{\"size\":%s,\"sha256\":\"%s\"},\"credentials.tar.age\":{\"size\":%s,\"sha256\":\"%s\"}}}";
  private static final Pattern STRUCTURE =
      Pattern.compile(
          String.join(
              "([^\"{},\\s]{1,128})",
              Arrays.stream((FORMAT + "\n").split("%s", -1)).map(Pattern::quote).toList()));

  private BackupManifestCodec() {
    throw new AssertionError("static namespace");
  }

  public static byte[] encode(BackupManifest value) {
    Objects.requireNonNull(value, "manifest");
    var d = value.databaseStep();
    var c = value.configurationStep();
    var v = value.versions();
    // Constructor bounds cap canonical output below 4096 bytes (PT-BAT-187).
    return String.format(
            Locale.ROOT,
            FORMAT,
            value.run().id(),
            TIME.format(value.run().cutoff()),
            TIME.format(value.startedAt()),
            TIME.format(value.contentFinishedAt()),
            d.id(),
            d.attempt(),
            TIME.format(d.startedAt()),
            c.id(),
            c.attempt(),
            TIME.format(c.startedAt()),
            v.host(),
            v.app(),
            v.schema(),
            v.os(),
            v.jdk(),
            v.postgresql(),
            v.artemis(),
            v.age(),
            value.recipientSha256(),
            value.dump().size(),
            value.dump().sha256(),
            value.configuration().size(),
            value.configuration().sha256(),
            value.credentials().size(),
            value.credentials().sha256())
        .concat("\n")
        .getBytes(StandardCharsets.US_ASCII);
  }

  public static BackupManifest decode(byte[] bytes) {
    Objects.requireNonNull(bytes, "manifest bytes");
    if (bytes.length == 0 || bytes.length > 4096) throw invalid();
    // Snapshot mutable caller input once; no arrays are retained by the returned immutable model.
    byte[] snapshot = bytes.clone();
    for (byte b : snapshot) if (b < 0) throw invalid();
    Matcher m = STRUCTURE.matcher(new String(snapshot, StandardCharsets.US_ASCII));
    if (!m.matches()) throw invalid();
    try {
      BatchRun run = new BatchRun(UUID.fromString(field(m, 1)), Instant.parse(field(m, 2)));
      var d =
          new BatchStepAttempt(
              Long.parseLong(field(m, 5)),
              run,
              BatchStep.BACKUP_DB,
              Integer.parseInt(field(m, 6)),
              Instant.parse(field(m, 7)),
              false);
      var c =
          new BatchStepAttempt(
              Long.parseLong(field(m, 8)),
              run,
              BatchStep.BACKUP_CONFIG,
              Integer.parseInt(field(m, 9)),
              Instant.parse(field(m, 10)),
              false);
      var v =
          new BackupVersions(
              field(m, 11),
              field(m, 12),
              field(m, 13),
              field(m, 14),
              field(m, 15),
              field(m, 16),
              field(m, 17),
              field(m, 18));
      var value =
          new BackupManifest(
              d,
              c,
              Instant.parse(field(m, 3)),
              Instant.parse(field(m, 4)),
              v,
              field(m, 19),
              digest(m, 20),
              digest(m, 22),
              digest(m, 24));
      if (!Arrays.equals(snapshot, encode(value))) throw invalid();
      return value;
    } catch (IllegalArgumentException | DateTimeException failure) {
      // Deliberately no raw parser cause/suppressed values in public diagnostics.
      throw invalid();
    }
  }

  private static String field(Matcher matcher, int index) {
    return Objects.requireNonNull(matcher.group(index), "required canonical field");
  }

  private static BackupFileDigest digest(Matcher matcher, int sizeIndex) {
    return new BackupFileDigest(
        Long.parseLong(field(matcher, sizeIndex)), field(matcher, sizeIndex + 1));
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("invalid backup manifest");
  }
}
