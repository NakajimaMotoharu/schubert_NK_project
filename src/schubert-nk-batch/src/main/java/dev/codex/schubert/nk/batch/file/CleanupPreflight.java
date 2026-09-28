package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.io.IOException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.function.BooleanSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * Read-only child preflight sequence, not a DELETE capability or complete Cleanup Unit. Only the
 * fixed child composition may supply these package ports; the DB port must own and close the
 * CleanupDatabaseSession, whose callback executes the PG332 backup observation. NK-OPS-001;
 * OPS-009/BAK-001/UI251/SS341/343/SSC104/PG333; PT-OPS-CPR001 onward.
 */
@NullMarked
public final class CleanupPreflight {
  @FunctionalInterface
  interface Gate {
    void recheck() throws IOException;
  }

  @FunctionalInterface
  interface Request {
    CleanupWorkerRequest read() throws IOException;
  }

  @FunctionalInterface
  interface Original {
    MaintenanceActivation observe(CleanupWorkerRequest request) throws IOException;
  }

  @FunctionalInterface
  interface Database {
    BackupManifest verify(CleanupWorkerRequest request, Instant observedAt) throws IOException;
  }

  private final Gate gate;
  private final Request request;
  private final Original original;
  private final Database database;
  private final Clock clock;
  private final BooleanSupplier interrupted;

  CleanupPreflight(Gate gate, Request request, Original original, Database database, Clock clock) {
    this(gate, request, original, database, clock, () -> Thread.currentThread().isInterrupted());
  }

  CleanupPreflight(
      Gate gate,
      Request request,
      Original original,
      Database database,
      Clock clock,
      BooleanSupplier interrupted) {
    this.gate = Objects.requireNonNull(gate, "root child gate");
    this.request = Objects.requireNonNull(request, "fixed private request");
    this.original = Objects.requireNonNull(original, "durable original observation");
    this.database = Objects.requireNonNull(database, "owned child database observation");
    this.clock = Objects.requireNonNull(clock, "UTC observation clock");
    this.interrupted = Objects.requireNonNull(interrupted, "interrupt observation");
  }

  /** Returns an observation only after all owners in the DB port have closed. */
  public BackupManifest verify() throws IOException {
    try {
      check();
      gate.recheck();
      CleanupWorkerRequest fixed = Objects.requireNonNull(request.read(), "private request");
      MaintenanceActivation activation =
          Objects.requireNonNull(original.observe(fixed), "durable activation");
      Instant observedAt =
          Objects.requireNonNull(clock.instant(), "observation instant")
              .truncatedTo(ChronoUnit.MICROS);
      if (observedAt.isBefore(fixed.cutoff())) throw unavailable();
      check();
      BackupManifest manifest =
          Objects.requireNonNull(database.verify(fixed, observedAt), "verified backup");
      check();
      if (!manifest.run().id().equals(fixed.run())
          || !manifest.run().cutoff().equals(fixed.cutoff())) throw unavailable();
      if (!fixed.equals(request.read()) || !activation.equals(original.observe(fixed)))
        throw unavailable();
      gate.recheck();
      check();
      return manifest;
    } catch (IOException failure) {
      throw unavailable();
    }
  }

  private void check() throws IOException {
    if (interrupted.getAsBoolean()) throw unavailable();
  }

  private static IOException unavailable() {
    return new IOException("root cleanup preflight unavailable");
  }
}
