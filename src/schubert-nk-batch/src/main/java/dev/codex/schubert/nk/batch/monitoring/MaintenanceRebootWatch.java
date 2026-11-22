package dev.codex.schubert.nk.batch.monitoring;

import java.time.DateTimeException;
import java.time.Duration;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/**
 * SS341 §4.2 external reboot-marker decision. Reads observations supplied by the external
 * monitoring process. OPS-003; NK-OPS-001; PT-OPS-MAINT-PREBOOT004-W01..W08.
 */
public final class MaintenanceRebootWatch {
  private static final Duration DEADLINE = Duration.ofMinutes(60);

  private MaintenanceRebootWatch() {}

  enum Decision {
    WAITING,
    COMPLETE,
    CRITICAL,
    INVALID_OBSERVATION
  }

  record Marker(UUID runId, UUID bootId, Instant markedAt) {
    Marker {
      Objects.requireNonNull(runId);
      Objects.requireNonNull(bootId);
      Objects.requireNonNull(markedAt);
    }
  }

  /**
   * Arguments are run ID, original boot ID, maintenance start, observation time, then optionally
   * marker run ID, marker boot ID and marker time. Standard output is one decision.
   */
  public static void main(String[] args) {
    System.out.println(parseObservation(args));
  }

  static Decision parseObservation(String @Nullable [] args) {
    if (args == null
        || (args.length != 4 && args.length != 7)
        || Arrays.stream(args).anyMatch(Objects::isNull)) {
      return Decision.INVALID_OBSERVATION;
    }
    try {
      Optional<Marker> marker = Optional.empty();
      if (args.length == 7) {
        marker =
            Optional.of(
                new Marker(canonicalId(args[4]), canonicalId(args[5]), Instant.parse(args[6])));
      }
      return evaluate(
          canonicalId(args[0]),
          canonicalId(args[1]),
          Instant.parse(args[2]),
          Instant.parse(args[3]),
          marker);
    } catch (IllegalArgumentException | DateTimeException failure) {
      return Decision.INVALID_OBSERVATION;
    }
  }

  static Decision evaluate(
      UUID runId,
      UUID originalBoot,
      Instant startedAt,
      Instant observedAt,
      Optional<Marker> marker) {
    Objects.requireNonNull(runId);
    Objects.requireNonNull(originalBoot);
    Objects.requireNonNull(startedAt);
    Objects.requireNonNull(observedAt);
    Objects.requireNonNull(marker);
    if (observedAt.isBefore(startedAt)) return Decision.INVALID_OBSERVATION;

    if (marker.isPresent()) {
      var proof = marker.orElseThrow();
      if (proof.runId().equals(runId)
          && !proof.bootId().equals(originalBoot)
          && proof.markedAt().isAfter(startedAt)
          && !proof.markedAt().isAfter(observedAt)
          && Duration.between(startedAt, proof.markedAt()).compareTo(DEADLINE) <= 0) {
        return Decision.COMPLETE;
      }
    }
    return Duration.between(startedAt, observedAt).compareTo(DEADLINE) < 0
        ? Decision.WAITING
        : Decision.CRITICAL;
  }

  private static UUID canonicalId(String text) {
    UUID id = UUID.fromString(text);
    if (!id.toString().equals(text))
      throw new IllegalArgumentException("non-canonical observation ID");
    return id;
  }
}
