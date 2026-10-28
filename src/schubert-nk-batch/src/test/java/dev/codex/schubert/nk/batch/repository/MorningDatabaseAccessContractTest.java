package dev.codex.schubert.nk.batch.repository;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.backup.BackupFileDigest;
import dev.codex.schubert.nk.batch.backup.BackupManifest;
import dev.codex.schubert.nk.batch.backup.BackupVersions;
import dev.codex.schubert.nk.batch.file.BackupBundleCompletion;
import dev.codex.schubert.nk.batch.platform.BackupWorkerRequest;
import dev.codex.schubert.nk.batch.platform.ExpiryReceiptFixture;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.bootstrap.StartupReleaseManifest;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-OPS-MACCESS585001..004 / OPS009,DAT009 / UI251 / SS341343 / SSC129133200. Data claims and a
 * non-native Access never acquire JDBC/Unit/owner authority.
 */
final class MorningDatabaseAccessContractTest {
  private static final String FIXTURE_SCHUBERT_BATCH_F9C88479 = "schubert_batch";
  private static final BatchRun RUN =
      new BatchRun(
          UUID.fromString("58500000-2222-4333-8444-555555555555"),
          Instant.parse("2026-10-08T00:00:00Z"));
  private static final Instant NOW = Instant.parse("2026-10-08T01:00:00Z");

  private static class Unsupported implements MorningDatabaseSession.Access {
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
  void maccess587001OriginalAwareExpiryDefaultForwardsSameArgumentsAndBorrowedData()
      throws Exception {
    MaintenanceOwnerFrame.Guard owner = () -> fail("data dispatch cannot mint native owner");
    var expected =
        new MorningDatabaseSession.ExpiryBegins(
            new BatchStepAttempt(587001, RUN, BatchStep.CLEAN_EXPIRY, 1, NOW, false),
            Optional.empty());
    var calls = new AtomicInteger();
    var access =
        new Unsupported() {
          @Override
          public MorningDatabaseSession.ExpiryBegins beginExpiry(
              BatchRun actualRun, Instant actualTime, MaintenanceOwnerFrame.Guard actualOwner) {
            assertSame(RUN, actualRun);
            assertSame(NOW, actualTime);
            assertSame(owner, actualOwner);
            calls.incrementAndGet();
            return expected;
          }
        };
    assertSame(
        expected,
        access.beginExpiry(RUN, NOW, owner, (id, time) -> fail("default must not consume lookup")));
    assertEquals(1, calls.get());
    assertThrows(NullPointerException.class, () -> access.beginExpiry(RUN, NOW, owner, null));
    assertEquals(1, calls.get());
  }

  @Test
  void maccess587002OriginalAwareCleanupDefaultForwardsSameSnapshotAndBorrowedData()
      throws Exception {
    MaintenanceOwnerFrame.Guard owner = () -> fail("data dispatch cannot mint native owner");
    var steps =
        List.of(
            BatchStep.CLEAN_NOTIFICATION,
            BatchStep.CLEAN_QUESTION,
            BatchStep.CLEAN_SESSION,
            BatchStep.CLEAN_INBOX_OUTBOX,
            BatchStep.CLEAN_LOG,
            BatchStep.CLEAN_BATCH_RUN,
            BatchStep.CLEAN_TRANSFER);
    var entries = new ArrayList<CleanupTerminalRepository.Entry>();
    var success =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 0, 0, 0, 0, BatchStepResult.Reason.NONE);
    for (int i = 0; i < steps.size(); i++)
      entries.add(
          new CleanupTerminalRepository.Entry(
              new BatchStepAttempt(587010 + i, RUN, steps.get(i), 1, NOW, false),
              NOW.plusSeconds(1),
              success));
    var snapshot = new CleanupTerminalRepository.Snapshot(entries);
    List<Optional<CleanupTerminalRepository.Entry>> expected =
        List.of(
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty(),
            Optional.empty());
    var calls = new AtomicInteger();
    var access =
        new Unsupported() {
          @Override
          public List<Optional<CleanupTerminalRepository.Entry>> cleanupReferences(
              CleanupTerminalRepository.Snapshot actual, MaintenanceOwnerFrame.Guard actualOwner) {
            assertSame(snapshot, actual);
            assertSame(owner, actualOwner);
            calls.incrementAndGet();
            return expected;
          }
        };
    assertSame(
        expected,
        access.cleanupReferences(
            snapshot, owner, (id, time) -> fail("default must not consume lookup")));
    assertEquals(1, calls.get());
    assertThrows(NullPointerException.class, () -> access.cleanupReferences(snapshot, owner, null));
    assertEquals(1, calls.get());
  }

  @Test
  void maccess586001ReceiptAndCleanupDataDoNotCreateDatabaseAuthority() throws Exception {
    var access = new Unsupported();
    MaintenanceOwnerFrame.Guard owner = () -> fail("unsupported owner must not run");
    var expiry =
        new MorningDatabaseSession.ExpiryBegins(
            new BatchStepAttempt(586001, RUN, BatchStep.CLEAN_EXPIRY, 1, NOW, false),
            Optional.empty());
    var receipt = ExpiryReceiptFixture.receipt(0);
    denied(() -> access.observeExpiry(expiry, receipt, owner));
    denied(
        () -> access.observeCleanupRejected(RUN, ExpiryReceiptFixture.cleanupReceipt(30), owner));
    assertThrows(NullPointerException.class, () -> access.observeExpiry(expiry, null, owner));
    assertThrows(NullPointerException.class, () -> access.observeExpiry(expiry, receipt, null));
    assertThrows(
        NullPointerException.class, () -> access.observeCleanupRejected(RUN, receipt, null));
    var entries = new ArrayList<CleanupTerminalRepository.Entry>();
    var success =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 0, 0, 0, 0, BatchStepResult.Reason.NONE);
    for (int i = 0; i < CleanupTerminalRepository.STEPS.size(); i++) {
      entries.add(
          new CleanupTerminalRepository.Entry(
              new BatchStepAttempt(
                  586010 + i, RUN, CleanupTerminalRepository.STEPS.get(i), 1, NOW, false),
              NOW.plusSeconds(1),
              success));
    }
    var snapshot = new CleanupTerminalRepository.Snapshot(entries);
    denied(() -> access.cleanupReferences(snapshot, owner));
    denied(
        () ->
            access.cleanupReferences(
                snapshot, owner, (id, observed) -> fail("lookup must not run")));
    assertThrows(NullPointerException.class, () -> access.cleanupReferences(snapshot, null));
  }

  @Test
  void maccess586002BorrowedTemporaryFileCapabilityDoesNotCommitBackup(@TempDir Path directory)
      throws Exception {
    var access = new Unsupported();
    var manifest = claims();
    var pair =
        new MorningDatabaseSession.BackupBegins(
            manifest.databaseStep(), manifest.configurationStep());
    long uid = ((Number) Files.getAttribute(directory, "unix:uid")).longValue();
    long gid = ((Number) Files.getAttribute(directory, "unix:gid")).longValue();
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), directory)) {
      var completion = new BackupBundleCompletion(held, LinuxInodeSecurity.create(), uid, gid);
      denied(
          () ->
              access.completeBackup(
                  pair, completion, "20261008-100001-58500000-2222-4333-8444-555555555555"));
      try (var files = Files.list(directory)) {
        assertEquals(0, files.count());
      }
    }
  }

  @Test
  void maccess586003DefaultReadbackBindsSameDataAndForwardsSameOwner() throws Exception {
    MaintenanceOwnerFrame.Guard owner = () -> fail("data readback is not native owner admission");
    var facts =
        new RootReleaseAdmission.DatabaseInspection(
            new StartupReleaseManifest.Contents(
                "PUBLIC", "a".repeat(64), List.of(), Map.of(), Map.of()),
            List.of(),
            Map.of());
    var expected =
        new MorningDatabaseSession.DatabaseObservation(
            FIXTURE_SCHUBERT_BATCH_F9C88479,
            FIXTURE_SCHUBERT_BATCH_F9C88479,
            "schubert_nk",
            true,
            false,
            2,
            false,
            true,
            facts);
    var changed =
        new MorningDatabaseSession.DatabaseObservation(
            FIXTURE_SCHUBERT_BATCH_F9C88479,
            FIXTURE_SCHUBERT_BATCH_F9C88479,
            "schubert_nk",
            false,
            false,
            2,
            false,
            true,
            facts);
    var observed = new java.util.concurrent.atomic.AtomicReference<>(expected);
    var reads = new AtomicInteger();
    var access =
        new Unsupported() {
          @Override
          public MorningDatabaseSession.DatabaseObservation inspectPermitDatabase(
              MaintenanceOwnerFrame.Guard actual) {
            assertSame(owner, actual);
            reads.incrementAndGet();
            return observed.get();
          }
        };
    assertDoesNotThrow(() -> access.recheckPermitDatabase(expected, owner));
    observed.set(changed);
    denied(() -> access.recheckPermitDatabase(expected, owner));
    assertThrows(NullPointerException.class, () -> access.recheckPermitDatabase(expected, null));
    assertEquals(2, reads.get());
    assertEquals("MorningDatabaseObservation[actual=<redacted>]", expected.toString());

    var begins =
        new MorningDatabaseSession.ExpiryBegins(
            new BatchStepAttempt(586101, RUN, BatchStep.CLEAN_EXPIRY, 1, NOW, false),
            Optional.empty());
    var receipt = ExpiryReceiptFixture.receipt(0);
    var result =
        new BatchStepResult(
            BatchStepResult.Status.SUCCESS, 0, 0, 0, 0, BatchStepResult.Reason.NONE);
    var audit =
        new ExpiryAuditRepository.Snapshot(
            "SUCCESS",
            RUN.cutoff().minusSeconds(604800),
            0L,
            0L,
            0,
            0,
            0,
            0,
            NOW.plusSeconds(1),
            null,
            null);
    var expectedExpiry =
        new MorningDatabaseSession.ExpiryObservation(
            begins, NOW.plusSeconds(1), result, audit, receipt);
    var laterAudit =
        new ExpiryAuditRepository.Snapshot(
            "SUCCESS",
            RUN.cutoff().minusSeconds(604800),
            0L,
            0L,
            0,
            0,
            0,
            0,
            NOW.plusSeconds(2),
            null,
            null);
    var changedExpiry =
        new MorningDatabaseSession.ExpiryObservation(
            begins, NOW.plusSeconds(2), result, laterAudit, receipt);
    var expiryObserved = new java.util.concurrent.atomic.AtomicReference<>(expectedExpiry);
    var expiryAccess =
        new Unsupported() {
          @Override
          public MorningDatabaseSession.ExpiryObservation observeExpiry(
              MorningDatabaseSession.ExpiryBegins actualBegins,
              dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate.TerminalReceipt
                  actualReceipt,
              MaintenanceOwnerFrame.Guard actualOwner) {
            assertSame(begins, actualBegins);
            assertSame(receipt, actualReceipt);
            assertSame(owner, actualOwner);
            return expiryObserved.get();
          }
        };
    assertDoesNotThrow(() -> expiryAccess.recheckExpiry(expectedExpiry, owner));
    expiryObserved.set(changedExpiry);
    denied(() -> expiryAccess.recheckExpiry(expectedExpiry, owner));
    assertThrows(
        NullPointerException.class, () -> expiryAccess.recheckExpiry(expectedExpiry, null));
    assertEquals("ExpiryObservation[actual=<redacted>]", expectedExpiry.toString());
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
