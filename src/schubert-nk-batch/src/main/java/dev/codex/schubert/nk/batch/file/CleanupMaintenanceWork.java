package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.EnvironmentInodePolicy.require;

import dev.codex.schubert.nk.batch.cleanup.InspectionAttempt;
import dev.codex.schubert.nk.batch.cleanup.InspectorLockHandoff;
import dev.codex.schubert.nk.batch.cleanup.LogCleanupService;
import dev.codex.schubert.nk.batch.cleanup.MaintenanceMutationGuard;
import dev.codex.schubert.nk.batch.cleanup.StepCleanupService;
import dev.codex.schubert.nk.batch.platform.BackupUnitStartClient;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.BatchRunRepository;
import dev.codex.schubert.nk.batch.repository.BatchStep;
import dev.codex.schubert.nk.batch.repository.BatchStepAttempt;
import dev.codex.schubert.nk.batch.repository.BatchStepResult;
import dev.codex.schubert.nk.batch.repository.CleanupCounts;
import dev.codex.schubert.nk.batch.repository.CleanupKind;
import dev.codex.schubert.nk.batch.repository.CleanupTerminalRepository;
import dev.codex.schubert.nk.batch.repository.InspectionSummaryRepository;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.bootstrap.FixedServiceIdentity;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxInodeSecurity;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.ResourceScope;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageIoException;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import edu.umd.cs.findbugs.annotations.SuppressMatchType;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import org.jspecify.annotations.NullMarked;

/**
 * Fixed actual Cleanup ordering under the borrowed, schema/advisory-admitted connection.
 * NK-OPS-001/NK-BAT-001/OPS009/DAT009/FIL006/UI251/SS331/341§7.3/343§6.17/SSC119;
 * PT-OPS-CEXEC001/CINSPECT001..004/TRANSFER001..003. Host ports prove ordering/DB postconditions,
 * NEVER native Unit acceptance. Inspector completion includes Outbox commit/readback BEFORE
 * owner/environment/intent retirement; no keys or JDBC handle cross the Unit boundary.
 */
@NullMarked
final class CleanupMaintenanceWork {
  @FunctionalInterface
  interface AfterInspection {
    void execute(InspectionAttempt actual) throws IOException;
  }

  @FunctionalInterface
  interface Inbox {
    void execute(Connection borrowed, AfterInspection completed) throws IOException;
  }

  @FunctionalInterface
  interface Transfer {
    BatchStepResult execute() throws IOException;
  }

  private final RootStartupContext context;
  private final RootStartupContext.Snapshot expected;
  private final MaintenanceOwnerFrame owner;
  private final MaintenanceOwnerFrame.Guard guard;
  private final MaintenanceMutationGuard mutation;
  private final Inbox retainedInbox;
  private final Transfer retainedTransfer;

  CleanupMaintenanceWork(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MaintenanceOwnerFrame owner,
      MaintenanceOwnerFrame.Guard guard) {
    this.context = Objects.requireNonNull(context, "actual Cleanup root");
    this.expected = Objects.requireNonNull(expected, "actual Cleanup generation");
    this.owner = Objects.requireNonNull(owner, "actual Morning owner");
    this.guard = Objects.requireNonNull(guard, "same owner mutation guard");
    requireProfile();
    mutation = new MaintenanceMutationGuard(guard);
    retainedInbox = this::inspect;
    retainedTransfer = this::transfer;
  }

  CleanupMaintenanceWork(
      RootStartupContext context,
      RootStartupContext.Snapshot expected,
      MaintenanceOwnerFrame owner,
      MaintenanceOwnerFrame.Guard guard,
      Inbox inbox,
      Transfer transfer) {
    this.context = Objects.requireNonNull(context, "actual Cleanup root");
    this.expected = Objects.requireNonNull(expected, "actual Cleanup generation");
    this.owner = Objects.requireNonNull(owner, "actual Morning owner");
    this.guard = Objects.requireNonNull(guard, "same owner mutation guard");
    requireProfile();
    mutation = new MaintenanceMutationGuard(guard);
    this.retainedInbox = Objects.requireNonNull(inbox, "synchronous Inspector operation");
    this.retainedTransfer = Objects.requireNonNull(transfer, "actual Transfer operation");
  }

  private void requireProfile() {
    if (expected.service() != RootStartupContext.Service.CLEANUP
        || owner.cleanup().isPresent()
        || !expected.boot().equals(owner.boot().toString()))
      throw new IllegalArgumentException("Cleanup owner profile unavailable");
  }

  int execute(Connection borrowed) throws IOException {
    Objects.requireNonNull(borrowed, "admitted Cleanup connection");
    guard.check();
    int warnings = 0;
    warnings += ordinary(borrowed, CleanupKind.NOTIFICATIONS) ? 1 : 0;
    warnings += ordinary(borrowed, CleanupKind.QUESTIONS) ? 1 : 0;
    warnings += ordinary(borrowed, CleanupKind.SESSIONS) ? 1 : 0;
    warnings += inbox(borrowed) ? 1 : 0;
    var logs = begin(borrowed, BatchStep.CLEAN_LOG);
    if (!logs.skipped()) {
      var summary = LogCleanupService.withOwner(guard).execute(borrowed, run());
      finish(borrowed, logs, cleanupResult(summary.after().counts(), summary.exitCode() == 10));
      warnings += summary.exitCode() == 10 ? 1 : 0;
    }
    var history = begin(borrowed, BatchStep.CLEAN_BATCH_RUN);
    if (!history.skipped()) {
      var service = StepCleanupService.withOwner(guard);
      // QA048/SSC175/RCPT004: one existing shared step, locators before retained history.
      service.execute(borrowed, history, CleanupKind.WEB_RECEIPTS);
      service.execute(borrowed, history, CleanupKind.BATCH_RUNS);
      service.execute(borrowed, history, CleanupKind.INBOX_PROGRESS);
      var summary = service.execute(borrowed, history, CleanupKind.LOG_PROGRESS);
      finish(borrowed, history, cleanupResult(summary.after(), false));
    }
    warnings += transferStep(borrowed) ? 1 : 0;
    guard.check();
    return warnings == 0 ? 0 : 10;
  }

  /** SSC124: committed actual six SKIPs, zero destructive operations/Inspector, real Transfer. */
  int executeFailed(Connection borrowed) throws IOException {
    Objects.requireNonNull(borrowed, "admitted failed-profile connection");
    for (var step : CleanupTerminalRepository.STEPS.subList(0, 6)) {
      try {
        guard.check();
        require(borrowed.getAutoCommit());
        borrowed.setAutoCommit(false);
        mutation.bind(borrowed);
        var repository = new BatchRunRepository(borrowed);
        var attempt = repository.beginBackupUnavailable(run(), step, now(), true);
        guard.check();
        borrowed.commit();
        guard.check();
        borrowed.setAutoCommit(true);
        borrowed.setAutoCommit(false);
        mutation.bind(borrowed);
        repository.verifyBackupUnavailable(attempt);
        guard.check();
        borrowed.rollback();
        borrowed.setAutoCommit(true);
        guard.check();
      } catch (SQLException known) {
        StorageIoException.preserveFatal(known);
        throw unavailable();
      }
    }
    boolean warning = transferStep(borrowed);
    guard.check();
    return warning ? 10 : 0;
  }

  private boolean transferStep(Connection borrowed) throws IOException {
    var files = begin(borrowed, BatchStep.CLEAN_TRANSFER);
    if (!files.skipped()) {
      guard.check();
      var result = Objects.requireNonNull(retainedTransfer.execute(), "actual Transfer counters");
      require(
          result.status() == BatchStepResult.Status.SUCCESS
              || result.status() == BatchStepResult.Status.WARNING);
      guard.check();
      finish(borrowed, files, result);
      return result.status() == BatchStepResult.Status.WARNING;
    }
    guard.check();
    return false;
  }

  private boolean ordinary(Connection c, CleanupKind kind) throws IOException {
    var attempt = begin(c, kind.step());
    if (attempt.skipped()) return false;
    var summary = StepCleanupService.withOwner(guard).execute(c, attempt, kind);
    finish(c, attempt, cleanupResult(summary.after(), summary.deferred()));
    return summary.deferred();
  }

  private boolean inbox(Connection c) throws IOException {
    var attempt = begin(c, BatchStep.CLEAN_INBOX_OUTBOX);
    if (attempt.skipped()) return false;
    var completed = new AtomicBoolean();
    var warning = new AtomicBoolean();
    retainedInbox.execute(
        c,
        inspected -> {
          Objects.requireNonNull(inspected, "actual same-run inspection");
          require(inspected.run().equals(run()) && !completed.get());
          guard.check();
          var outbox = StepCleanupService.withOwner(guard).execute(c, attempt, CleanupKind.OUTBOX);
          // Current step is a new attempt; durable Inbox progress has a separate run cumulative.
          var delta = inspected.attempt();
          var rows = outbox.after();
          CleanupCounts counts;
          try {
            counts =
                new CleanupCounts(
                    Math.addExact(delta.target(), rows.target()),
                    Math.addExact(delta.deleted(), rows.deleted()),
                    Math.addExact(delta.skipped(), rows.skipped()));
          } catch (ArithmeticException overflow) {
            throw unavailable();
          }
          warning.set(inspected.outcome() == MaintenanceCompletion.Outcome.WARNING);
          finish(c, attempt, cleanupResult(counts, warning.get()));
          completed.set(true);
        });
    require(completed.get()); // A port's return, empty DB or old summary is not execution.
    guard.check();
    return warning.get();
  }

  private BatchRun run() {
    return new BatchRun(owner.run(), owner.cutoff());
  }

  private BatchStepAttempt begin(Connection c, BatchStep step) throws IOException {
    try {
      guard.check();
      require(c.getAutoCommit());
      c.setAutoCommit(false);
      mutation.bind(c);
      var repository = new BatchRunRepository(c);
      var attempt = repository.begin(run(), step, now(), true);
      guard.check();
      c.commit();
      guard.check();
      c.setAutoCommit(true);
      if (attempt.skipped()) {
        c.setAutoCommit(false);
        mutation.bind(c);
        repository.verifyAlreadySuccessful(attempt);
        guard.check();
        c.rollback();
        c.setAutoCommit(true);
      }
      guard.check();
      return attempt;
    } catch (SQLException known) {
      StorageIoException.preserveFatal(known);
      throw unavailable();
    }
    // Ambiguous commit is never repaired here: CleanupDatabaseSession disposes the owner.
  }

  private void finish(Connection c, BatchStepAttempt attempt, BatchStepResult result)
      throws IOException {
    try {
      guard.check();
      require(c.getAutoCommit());
      var ended = now();
      c.setAutoCommit(false);
      mutation.bind(c);
      var repository = new BatchRunRepository(c);
      repository.finish(attempt, ended, result);
      guard.check();
      c.commit();
      guard.check();
      c.setAutoCommit(true);
      c.setAutoCommit(false);
      mutation.bind(c);
      repository.verifyFinished(attempt, ended, result);
      guard.check();
      c.rollback();
      c.setAutoCommit(true);
      guard.check();
    } catch (SQLException known) {
      StorageIoException.preserveFatal(known);
      throw unavailable();
    }
  }

  /** Protected rows are retained skips, never fictitious failures. */
  private static BatchStepResult cleanupResult(CleanupCounts counts, boolean warning) {
    return new BatchStepResult(
        warning ? BatchStepResult.Status.WARNING : BatchStepResult.Status.SUCCESS,
        counts.target(),
        counts.deleted(),
        0,
        0,
        warning ? BatchStepResult.Reason.PROTECTED_RECORDS : BatchStepResult.Reason.NONE);
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification =
          "SS343 fixed new-only Inspector owner source, no arbitrary Unit/path; CINSPECT001")
  private void inspect(Connection c, AfterInspection complete) throws IOException {
    guard.check();
    var before = new InspectionSummaryRepository(c).read(run());
    var frame =
        owner.forInspector(
            new MaintenanceOwnerFrame.Parent(
                expected.invocation(), expected.pid(), expected.startTicks()));
    var requestCalls = LinuxDirectoryCalls.create();
    Path requestPath = Path.of("/run/schubert-nk/cleanup-request");
    ResourceScope.<OwnedTransferDirectory, Boolean, IOException>acquire(
        () -> OwnedTransferDirectory.open(requestCalls, requestPath),
        OwnedTransferDirectory::close,
        root -> {
          var files =
              CleanupWorkerRequestFiles.forOwner(
                  root,
                  LinuxInodeSecurity.create(),
                  CleanupWorkerRequestFiles.OwnerSource.INSPECTOR);
          files.prepareOwner(frame, UUID.randomUUID());
          guard.check();
          return InspectorEnvironmentFiles.create()
              .executeOwned(
                  run(),
                  retirement -> {
                    var budget = MorningParentBudget.borrow(owner.deadlineNanos());
                    var cycle =
                        MorningBackupUnitCycle.create(
                            context, expected, budget, BackupUnitStartClient.Target.INSPECTOR);
                    cycle.executeInspectorHandoff(
                        work -> InspectorLockHandoff.execute(c, work::execute),
                        receipt -> {
                          guard.check();
                          var after =
                              new InspectionSummaryRepository(c)
                                  .read(run())
                                  .orElseThrow(CleanupMaintenanceWork::unavailable);
                          var actual =
                              InspectionAttempt.reconcile(run(), before, after, receipt.exitCode());
                          complete.execute(
                              actual); // Outbox finish/independent DB readback under reacquired
                          // lock.
                          guard.check();
                        },
                        () -> {
                          guard.check();
                          require(files.readOwner().equals(frame));
                          retirement.retire();
                          files.retireOwner(frame);
                          guard.check();
                        });
                    guard.check();
                    return Boolean.TRUE;
                  });
        });
  }

  @SuppressFBWarnings(
      value = "DMI_HARDCODED_ABSOLUTE_FILENAME",
      matchType = SuppressMatchType.EXACT,
      justification = "SS343 fixed API-owned/Web-group Transfer root, private RW only; TRANSFER001")
  private BatchStepResult transfer() throws IOException {
    guard.check();
    var identities = new FixedServiceIdentity();
    var api = identities.resolve(ServiceConfigFiles.Service.API);
    var web = identities.resolve(ServiceConfigFiles.Service.WEB);
    var transferCalls = LinuxDirectoryCalls.create();
    Path transferPath = Path.of("/srv/schubert-nk/data/transfer");
    return ResourceScope.<OwnedTransferDirectory, BatchStepResult, IOException>acquire(
        () -> OwnedTransferDirectory.open(transferCalls, transferPath),
        OwnedTransferDirectory::close,
        root ->
            new TransferCleanup(
                    root, LinuxInodeSecurity.create(), api.uid(), web.gid(), guard::check)
                .execute(owner.cutoff())
                .result());
  }

  private static Instant now() {
    return Instant.now().truncatedTo(ChronoUnit.MICROS);
  }

  private static IOException unavailable() {
    return new IOException("actual Cleanup result unavailable");
  }
}
