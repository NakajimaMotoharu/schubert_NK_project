package dev.codex.schubert.nk.batch.file;

import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.platform.CleanupWorkerRequest;
import dev.codex.schubert.nk.batch.repository.BackupStepRepository;
import dev.codex.schubert.nk.batch.repository.BatchRepositoryException;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Objects;
import java.util.function.BooleanSupplier;
import org.jspecify.annotations.NullMarked;

/**
 * Child's bounded backup observation, never a DELETE permit. Caller retains root, M/A, the admitted
 * CleanupDatabaseSession and the borrowed connection; it disposes the connection on any failure.
 * OPS-009/BAK-001/UI251/SS341/343/SSC104/PG332; PT-OPS-CBA001 onward.
 */
@NullMarked
public final class CleanupBackupAdmission {
  private final BackupManifestReader reader;
  private final BackupArtifactVerifier verifier;
  private final BooleanSupplier interrupted;

  public CleanupBackupAdmission(BackupManifestReader reader, BackupArtifactVerifier verifier) {
    this(reader, verifier, () -> Thread.currentThread().isInterrupted());
  }

  CleanupBackupAdmission(
      BackupManifestReader reader, BackupArtifactVerifier verifier, BooleanSupplier interrupted) {
    this.reader = Objects.requireNonNull(reader, "fixed backup reader");
    this.verifier = Objects.requireNonNull(verifier, "fixed artifact verifier");
    this.interrupted = Objects.requireNonNull(interrupted, "interrupt observation");
  }

  /** Requires a schema-admitted, advisory-holding child session, not an arbitrary DB connection. */
  public BackupManifest verify(
      CleanupWorkerRequest request, Instant observedAt, Connection borrowed) throws IOException {
    Objects.requireNonNull(request, "fixed cleanup request");
    Objects.requireNonNull(observedAt, "UTC microsecond observation");
    Objects.requireNonNull(borrowed, "borrowed child connection");
    if (interrupted.getAsBoolean()) throw unavailable();

    BackupManifest claims;
    try {
      claims = reader.findCleanupClaims(request);
      // Reader already bound the canonical claim SHA to request; verifier's successful result
      // requires the on-disk MANIFEST to equal that same canonical claim byte-for-byte.
      verifier.verify(claims);
    } catch (StorageIoException failure) {
      throw unavailable();
    }
    if (interrupted.getAsBoolean()) throw unavailable();

    try {
      if (!borrowed.getAutoCommit()
          || borrowed.isReadOnly()
          || borrowed.getTransactionIsolation() != Connection.TRANSACTION_READ_COMMITTED)
        throw unavailable();
      try {
        borrowed.setAutoCommit(false);
        if (new BackupStepRepository(borrowed).inspect(claims, observedAt).isEmpty())
          throw unavailable();
        if (interrupted.getAsBoolean()) throw unavailable();
        borrowed.rollback(); // Read-only FOR UPDATE observation; never commit a cleanup step.
      } catch (SQLException | IOException | RuntimeException | Error failure) {
        recover(borrowed, failure);
        throw failure;
      }
      borrowed.setAutoCommit(true);
      if (interrupted.getAsBoolean()) throw unavailable();
      return claims;
    } catch (SQLException | BatchRepositoryException failure) {
      throw unavailable();
    }
  }

  private static void recover(Connection borrowed, Throwable primary) throws IOException {
    try {
      borrowed.rollback();
      borrowed.setAutoCommit(true);
    } catch (SQLException cleanup) {
      // Unknown primary keeps identity; every other outcome is fixed and non-success. A failed
      // rollback must never trigger autoCommit restoration (which could commit pending work).
      if (unknown(primary)) {
        primary.addSuppressed(new BatchRepositoryException());
        return;
      }
      throw unavailable();
    } catch (RuntimeException | Error cleanup) {
      if (unknown(primary)) {
        primary.addSuppressed(new BatchRepositoryException());
        return;
      }
      if (cleanup instanceof BatchRepositoryException) throw unavailable();
      throw cleanup;
    }
  }

  private static boolean unknown(Throwable primary) {
    return primary instanceof Error
        || (primary instanceof RuntimeException && !(primary instanceof BatchRepositoryException));
  }

  private static IOException unavailable() {
    return new IOException("root cleanup backup unavailable");
  }
}
