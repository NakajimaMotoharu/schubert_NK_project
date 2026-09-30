package dev.codex.schubert.nk.batch.platform;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.nio.charset.StandardCharsets;
import java.time.DateTimeException;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.UUID;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed nonsecret correlation between parent Morning and Cleanup oneshot. Not authority for M/A,
 * backup success, DB lock, file deletion or downstream Artemis. NK-BAT-001/NK-OPS-001;
 * OPS-009/BAK-001; UI251; SS341§2/3/7,342§4,343§6; SSC104; PT-OPS-CREQ001..007.
 */
@NullMarked
public record CleanupWorkerRequest(
    UUID run, UUID activation, Instant cutoff, String manifestSha256) {
  public static final int MAXIMUM_BYTES = 256;
  private static final UUID NIL = new UUID(0, 0);

  public CleanupWorkerRequest {
    Objects.requireNonNull(run, "run");
    Objects.requireNonNull(activation, "activation");
    Objects.requireNonNull(cutoff, "cutoff");
    Objects.requireNonNull(manifestSha256, "manifest digest");
    if (run.equals(NIL) || activation.equals(NIL) || run.equals(activation)) throw invalid();
    new BatchRun(run, cutoff); // Fixed UTC microsecond range; never widen on resume.
    if (!manifestSha256.matches("[0-9a-f]{64}")) throw invalid();
  }

  /** Caller owns and clears the returned bytes after root-only private publication. */
  public byte[] encode() {
    return ("NKCLEAN1\nrun="
            + run
            + "\nactivation="
            + activation
            + "\ncutoff="
            + cutoff
            + "\nmanifest="
            + manifestSha256
            + "\n")
        .getBytes(StandardCharsets.US_ASCII);
  }

  /** Consumes and clears caller bytes on success and every parse failure. */
  public static CleanupWorkerRequest consume(byte[] owned) {
    Objects.requireNonNull(owned, "owned request");
    byte[] canonical = new byte[0];
    try {
      if (owned.length < 1 || owned.length > MAXIMUM_BYTES) throw invalid();
      for (byte value : owned) if (value != 10 && (value < 32 || value > 126)) throw invalid();
      String[] rows = new String(owned, StandardCharsets.US_ASCII).split("\n", -1);
      if (rows.length != 6
          || !rows[0].equals("NKCLEAN1")
          || !rows[1].startsWith("run=")
          || !rows[2].startsWith("activation=")
          || !rows[3].startsWith("cutoff=")
          || !rows[4].startsWith("manifest=")
          || !rows[5].isEmpty()) throw invalid();
      var request =
          new CleanupWorkerRequest(
              UUID.fromString(rows[1].substring(4)),
              UUID.fromString(rows[2].substring(11)),
              Instant.parse(rows[3].substring(7)),
              rows[4].substring(9));
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

  @Override
  public String toString() {
    return "CleanupWorkerRequest[identity/cutoff/manifest=<redacted>]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("cleanup request invalid");
  }

  /**
   * Same shared transport, separate fixed profile. Claims only, not permission to purge. SSC111.
   */
  public record Expiry(
      UUID run,
      UUID activation,
      Instant cutoff,
      UUID boot,
      UUID epoch,
      String brokerInvocation,
      long stepId,
      int attempt,
      Instant started,
      boolean skipped) {
    public static final int MAXIMUM_BYTES = 1024;

    public Expiry {
      Objects.requireNonNull(run);
      Objects.requireNonNull(activation);
      Objects.requireNonNull(cutoff);
      Objects.requireNonNull(boot);
      Objects.requireNonNull(epoch);
      Objects.requireNonNull(brokerInvocation);
      Objects.requireNonNull(started);
      if (run.equals(NIL)
          || activation.equals(NIL)
          || run.equals(activation)
          || boot.equals(NIL)
          || epoch.equals(NIL)
          || !brokerInvocation.matches("[0-9a-f]{32}")
          || brokerInvocation.equals("0".repeat(32))) throw invalid();
      new BatchStepAttempt(
          stepId, new BatchRun(run, cutoff), BatchStep.CLEAN_EXPIRY, attempt, started, skipped);
    }

    public BatchStepAttempt handle() {
      return new BatchStepAttempt(
          stepId, new BatchRun(run, cutoff), BatchStep.CLEAN_EXPIRY, attempt, started, skipped);
    }

    public MaintenanceActivation original() {
      return new MaintenanceActivation(new BatchRun(run, cutoff), activation);
    }

    public byte[] encode() {
      return ("NKEXPIRY1\nrun="
              + run
              + "\nactivation="
              + activation
              + "\ncutoff="
              + cutoff
              + "\nboot="
              + boot
              + "\nepoch="
              + epoch
              + "\nbroker="
              + brokerInvocation
              + "\nstep_id="
              + stepId
              + "\nattempt="
              + attempt
              + "\nstarted="
              + started
              + "\nskipped="
              + skipped
              + "\n")
          .getBytes(StandardCharsets.US_ASCII);
    }

    public static Expiry consume(byte[] owned) {
      Objects.requireNonNull(owned, "owned Expiry request");
      byte[] canonical = new byte[0];
      try {
        if (owned.length < 1 || owned.length > MAXIMUM_BYTES) throw invalid();
        for (byte b : owned) if (b != 10 && (b < 32 || b > 126)) throw invalid();
        String[] rows = new String(owned, StandardCharsets.US_ASCII).split("\n", -1);
        var keys =
            java.util.List.of(
                "run=",
                "activation=",
                "cutoff=",
                "boot=",
                "epoch=",
                "broker=",
                "step_id=",
                "attempt=",
                "started=",
                "skipped=");
        if (rows.length != 12 || !rows[0].equals("NKEXPIRY1") || !rows[11].isEmpty())
          throw invalid();
        String[] values = new String[10];
        for (int i = 0; i < 10; i++) {
          if (!rows[i + 1].startsWith(keys.get(i))) throw invalid();
          values[i] = rows[i + 1].substring(keys.get(i).length());
        }
        if (!values[9].equals("true") && !values[9].equals("false")) throw invalid();
        var request =
            new Expiry(
                UUID.fromString(values[0]),
                UUID.fromString(values[1]),
                Instant.parse(values[2]),
                UUID.fromString(values[3]),
                UUID.fromString(values[4]),
                values[5],
                Long.parseLong(values[6]),
                Integer.parseInt(values[7]),
                Instant.parse(values[8]),
                Boolean.parseBoolean(values[9]));
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

    @Override
    public String toString() {
      return "ExpiryWorkerRequest[claims=<redacted>]";
    }
  }
}
