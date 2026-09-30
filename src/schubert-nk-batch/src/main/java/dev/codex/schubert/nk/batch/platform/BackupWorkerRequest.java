package dev.codex.schubert.nk.batch.platform;

import java.nio.charset.StandardCharsets;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed nonsecret output binding, not parent/run/Unit authority. BAK/UI251/SS3416.1/SSC092/BREQ.
 */
@NullMarked
public record BackupWorkerRequest(UUID run, Instant started, Optional<Verification> verification) {
  public static final int MAXIMUM_BYTES = 400;

  /** Fixed public claims only. Parent authenticates manifest/DB; child verifies held dump. */
  public record Verification(String manifestSha256, long dumpSize, String dumpSha256) {
    public Verification {
      Objects.requireNonNull(manifestSha256, "manifest digest");
      Objects.requireNonNull(dumpSha256, "dump digest");
      if (!manifestSha256.matches("[0-9a-f]{64}")
          || dumpSize <= 0
          || !dumpSha256.matches("[0-9a-f]{64}")) throw invalid();
    }
  }

  public BackupWorkerRequest(UUID run, Instant started) {
    this(run, started, Optional.empty());
  }

  private static final DateTimeFormatter NAME =
      DateTimeFormatter.ofPattern("uuuuMMdd-HHmmss", Locale.ROOT).withZone(ZoneId.of("Asia/Tokyo"));

  public BackupWorkerRequest {
    Objects.requireNonNull(run, "run UUID");
    Objects.requireNonNull(started, "content start");
    Objects.requireNonNull(verification, "closed worker profile");
    if (run.equals(new UUID(0, 0))
        || started.isBefore(Instant.parse("0000-12-31T14:41:01Z"))
        || started.isAfter(Instant.parse("9999-12-31T14:59:59.999999Z"))
        || started.getNano() % 1000 != 0) throw invalid();
  }

  public String directoryName() {
    return NAME.format(started) + "-" + run;
  }

  public byte[] encode() {
    if (verification.isPresent()) {
      var v = verification.orElseThrow();
      return ("NKBACKUPVERIFY1\nrun="
              + run
              + "\nstarted="
              + started
              + "\nmanifest_sha256="
              + v.manifestSha256()
              + "\ndump_size="
              + v.dumpSize()
              + "\ndump_sha256="
              + v.dumpSha256()
              + "\n")
          .getBytes(StandardCharsets.US_ASCII);
    }
    return ("NKBACKUP1\nrun=" + run + "\nstarted=" + started + "\n")
        .getBytes(StandardCharsets.US_ASCII);
  }

  /** Consumes and clears caller bytes, including all failure paths. No arbitrary path/command. */
  public static BackupWorkerRequest consume(byte[] owned) {
    Objects.requireNonNull(owned, "owned request");
    byte[] canonical = new byte[0];
    try {
      if (owned.length < 1 || owned.length > MAXIMUM_BYTES) throw invalid();
      for (byte value : owned) if (value != 10 && (value < 32 || value > 126)) throw invalid();
      String[] rows = new String(owned, StandardCharsets.US_ASCII).split("\n", -1);
      boolean verify = rows[0].equals("NKBACKUPVERIFY1");
      if (rows.length != (verify ? 7 : 4)
          || (!verify && !rows[0].equals("NKBACKUP1"))
          || !rows[1].startsWith("run=")
          || !rows[2].startsWith("started=")
          || !rows[rows.length - 1].isEmpty()) throw invalid();
      Optional<Verification> verification = Optional.empty();
      if (verify) {
        if (!rows[3].startsWith("manifest_sha256=")
            || !rows[4].startsWith("dump_size=")
            || !rows[5].startsWith("dump_sha256=")) throw invalid();
        verification =
            Optional.of(
                new Verification(
                    rows[3].substring(16),
                    Long.parseLong(rows[4].substring(10)),
                    rows[5].substring(12)));
      }
      var request =
          new BackupWorkerRequest(
              UUID.fromString(rows[1].substring(4)),
              Instant.parse(rows[2].substring(8)),
              verification);
      canonical = request.encode();
      if (!Arrays.equals(owned, canonical)) throw invalid();
      return request;
    } catch (DateTimeException | IllegalArgumentException failure) {
      throw invalid();
    } finally {
      Arrays.fill(owned, (byte) 0);
      Arrays.fill(canonical, (byte) 0);
    }
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("backup request invalid");
  }
}
