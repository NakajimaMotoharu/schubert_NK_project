package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupVersions;
import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/**
 * PT-OPS-MACCESS585001..004 / OPS009,DAT009 / UI251 / SS341343 / SSC129133200. Data claims and a
 * non-native Access never acquire JDBC/Unit/owner authority.
 */
final class MorningDatabaseAccessContractTest {
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("58500000-2222-4333-8444-555555555555"),
          Instant.parse("2026-10-08T00:00:00Z"));
  private static final Instant NOW = Instant.parse("2026-10-08T01:00:00Z");

  private static final class Unsupported implements MorningDatabaseSession.Access {
    public void requireUnused(BatchRun run) {
      fail("unsupported default must not forward to DB operation");
    }

    public void requireConsistent(BatchRun run) {
      fail("unsupported default must not forward to DB operation");
    }

    public MorningDatabaseSession.BackupBegins beginBackup(
        BatchRun run, Instant now, boolean recoverAbandoned) {
      return fail("unsupported default must not issue backup");
    }

    public <T> T handoffCleanup(MorningDatabaseSession.CleanupHandoff<T> operation) {
      return fail("unsupported default must not execute child callback");
    }
  }

  private static BackupManifest claims() {
    var database = new BatchStepAttempt(585001, RUN, BatchStep.BACKUP_DB, 1, NOW, false);
    var config = new BatchStepAttempt(585002, RUN, BatchStep.BACKUP_CONFIG, 1, NOW, false);
    return new BackupManifest(
        database,
        config,
        NOW.plusSeconds(1),
        NOW.plusSeconds(2),
        new BackupVersions(
            "public-host", "1.0", "028", "ubuntu-26.04", "25.0.4", "18.6", "2.56.0", "1.2.1"),
        "0".repeat(64),
        new BackupFileDigest(11, "1".repeat(64)),
        new BackupFileDigest(12, "2".repeat(64)),
        new BackupFileDigest(13, "3".repeat(64)));
  }

  private static void denied(Executable operation) {
    var failure = assertThrows(IOException.class, operation);
    assertEquals("root batch database unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void maccess585001PublicBackupClaimsDoNotBecomeParentCapability() {
    var access = new Unsupported();
    var manifest = claims();
    var pair =
        new MorningDatabaseSession.BackupBegins(
            manifest.databaseStep(), manifest.configurationStep());
    denied(() -> access.retainedBackupSuccessful(manifest, NOW.plusSeconds(3)));
    denied(() -> access.successfulBackup(RUN, NOW.plusSeconds(3)));
    denied(() -> access.beginResumeBackup(manifest, NOW.plusSeconds(3)));
    denied(() -> access.completeReusedBackup(pair, manifest, NOW.plusSeconds(4)));
    var failed =
        new BatchStepResult(
            BatchStepResult.Status.FAILED, 0, 0, 0, 0, BatchStepResult.Reason.SAFETY_FAILURE);
    denied(() -> access.failBackup(pair, NOW.plusSeconds(4), failed, failed));
  }

  @Test
  void maccess585002OwnerAndChildCallbacksNeverRunOnUnsupportedAccess() {
    var access = new Unsupported();
    var calls = new AtomicInteger();
    MaintenanceOwnerFrame.Guard owner =
        () -> {
          calls.incrementAndGet();
          return 5_000_000_000L;
        };
    var manifest = claims();
    var pair =
        new MorningDatabaseSession.BackupBegins(
            manifest.databaseStep(), manifest.configurationStep());
    denied(() -> access.inspectPermitDatabase(owner));
    denied(() -> access.observeBackup(pair, Optional.of(manifest), NOW.plusSeconds(3), owner));
    denied(() -> access.failedBackupSnapshot(pair, owner));
    denied(() -> access.observeCleanupBackupUnavailable(RUN, 10, owner));
    denied(() -> access.observeCleanup(RUN, 0, owner));
    denied(() -> access.beginExpiry(RUN, NOW, owner));
    denied(
        () ->
            access.beginExpiry(
                RUN,
                NOW,
                owner,
                (id, observed) -> {
                  calls.incrementAndGet();
                  return RUN;
                }));
    denied(
        () ->
            access.handoffExpiry(
                () -> {
                  calls.incrementAndGet();
                  return Boolean.TRUE;
                }));
    assertEquals(0, calls.get());
  }

  @Test
  void maccess585003OriginalClaimsCannotResumeOrReenterDatabaseOwner() {
    var access = new Unsupported();
    denied(() -> access.recheckConsistent(RUN));
    denied(() -> access.requireAbandonedRequest(new BackupWorkerRequest(RUN.id(), NOW)));
    denied(() -> access.recheckConsistent(RUN)); // Repetition does not create authority.
  }

  @Test
  void maccess585004ExplicitNullContractsFailBeforeCallbacksOrNativeResources() {
    var access = new Unsupported();
    MaintenanceOwnerFrame.Guard owner = () -> fail("owner must not run");
    assertThrows(NullPointerException.class, () -> access.inspectPermitDatabase(null));
    assertThrows(NullPointerException.class, () -> access.recheckPermitDatabase(null, owner));
    assertThrows(NullPointerException.class, () -> access.recheckConsistent(null));
    assertThrows(NullPointerException.class, () -> access.requireAbandonedRequest(null));
    assertThrows(NullPointerException.class, () -> access.handoffExpiry(null));
    assertThrows(NullPointerException.class, () -> access.beginExpiry(null, NOW, owner));
    assertThrows(NullPointerException.class, () -> access.beginExpiry(RUN, null, owner));
    assertThrows(NullPointerException.class, () -> access.beginExpiry(RUN, NOW, null));
    assertThrows(NullPointerException.class, () -> access.beginExpiry(RUN, NOW, owner, null));
    assertThrows(NullPointerException.class, () -> access.failedBackupSnapshot(null, owner));
    assertThrows(
        NullPointerException.class,
        () ->
            access.failedBackupSnapshot(
                new MorningDatabaseSession.BackupBegins(
                    claims().databaseStep(), claims().configurationStep()),
                null));
    assertThrows(NullPointerException.class, () -> access.observeCleanup(null, 0, owner));
    assertThrows(NullPointerException.class, () -> access.observeCleanup(RUN, 0, null));
    assertThrows(
        NullPointerException.class, () -> access.observeCleanupBackupUnavailable(null, 10, owner));
    assertThrows(
        NullPointerException.class, () -> access.observeCleanupBackupUnavailable(RUN, 10, null));
    assertThrows(NullPointerException.class, () -> access.cleanupReferences(null, owner));
    assertThrows(NullPointerException.class, () -> access.cleanupReferences(null, owner, null));
    assertThrows(
        NullPointerException.class, () -> access.observeCleanupRejected(null, null, owner));
    assertThrows(NullPointerException.class, () -> access.observeCleanupRejected(RUN, null, owner));
    assertThrows(NullPointerException.class, () -> access.observeExpiry(null, null, owner));
    assertThrows(NullPointerException.class, () -> access.recheckExpiry(null, owner));
  }
}
