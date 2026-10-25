package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.MorningParentBudget;
import dev.codex.schubert.nk.batch.platform.RootStartupContext;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.batch.repository.MaintenanceRunState;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.lang.reflect.Proxy;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-2776-001/002; untrusted entry values must never reach publication/provider work. */
final class MorningStartupLaunchOwnerAdmissionTest {
  private static final UUID BOOT = UUID.fromString("27760001-2222-4333-8444-555555555555");
  private static final UUID EPOCH = UUID.fromString("27760002-2222-4333-8444-555555555555");
  private static final MaintenanceActivation ACTIVATION =
      new MaintenanceActivation(
          new BatchRun(
              UUID.fromString("27760003-2222-4333-8444-555555555555"),
              Instant.parse("2051-01-09T15:00:00Z")),
          UUID.fromString("27760004-2222-4333-8444-555555555555"));

  @Test
  void launch2776001UntrustedPublicationValuesRejectBeforeProviders() throws Exception {
    for (String fault : List.of("SERVICE", "EPOCH_STATE", "ACTIVATION")) {
      var originalCalls = new AtomicInteger();
      var databaseCalls = new AtomicInteger();
      MorningNewRunAdmission.OriginalProof original = originalCalls::incrementAndGet;
      var root = RootStartupContext.create();
      var snapshot =
          snapshot(
              fault.equals("SERVICE")
                  ? RootStartupContext.Service.API
                  : RootStartupContext.Service.MORNING);
      var state = new MaintenanceRunState(ACTIVATION, Optional.empty());
      var offered =
          fault.equals("ACTIVATION")
              ? new MaintenanceActivation(ACTIVATION.run(), EPOCH)
              : ACTIVATION;
      var issued =
          new StartupPermitRecords.Epoch(
              fault.equals("EPOCH_STATE")
                  ? StartupPermitRecords.State.INVALID
                  : StartupPermitRecords.State.ISSUED,
              BOOT,
              EPOCH,
              offered,
              fault.equals("EPOCH_STATE") ? Optional.empty() : Optional.of("1".repeat(64)));
      var budget = MorningParentBudget.create();
      var database = database(databaseCalls);
      var rejected =
          assertThrows(
              StorageIoException.class,
              () ->
                  MorningStartupLaunchOwner.publish(
                      root, snapshot, budget, state, database, original, issued));
      assertEquals(StorageIoException.Reason.UNAVAILABLE, rejected.reason());
      assertEquals("transfer storage operation failed", rejected.getMessage());
      assertNull(rejected.getCause());
      assertEquals(0, rejected.getSuppressed().length);
      assertEquals(0, originalCalls.get());
      assertEquals(0, databaseCalls.get());
    }
  }

  @Test
  void launch2776002EveryNullBoundaryRejectsBeforeProviders() throws Exception {
    for (String fault :
        List.of("ROOT", "MORNING", "BUDGET", "STATE", "DATABASE", "ORIGINAL", "ISSUED")) {
      var originalCalls = new AtomicInteger();
      var databaseCalls = new AtomicInteger();
      var root = RootStartupContext.create();
      var snapshot = snapshot(RootStartupContext.Service.MORNING);
      var budget = MorningParentBudget.create();
      var state = new MaintenanceRunState(ACTIVATION, Optional.empty());
      var database = database(databaseCalls);
      MorningNewRunAdmission.OriginalProof original = originalCalls::incrementAndGet;
      var issued =
          new StartupPermitRecords.Epoch(
              StartupPermitRecords.State.ISSUED,
              BOOT,
              EPOCH,
              ACTIVATION,
              Optional.of("1".repeat(64)));
      assertThrows(
          NullPointerException.class,
          () ->
              MorningStartupLaunchOwner.publish(
                  fault.equals("ROOT") ? null : root,
                  fault.equals("MORNING") ? null : snapshot,
                  fault.equals("BUDGET") ? null : budget,
                  fault.equals("STATE") ? null : state,
                  fault.equals("DATABASE") ? null : database,
                  fault.equals("ORIGINAL") ? null : original,
                  fault.equals("ISSUED") ? null : issued));
      assertEquals(0, originalCalls.get());
      assertEquals(0, databaseCalls.get());
    }
  }

  private static RootStartupContext.Snapshot snapshot(RootStartupContext.Service service) {
    return new RootStartupContext.Snapshot(
        service, BOOT.toString(), "2".repeat(32), 42, 100, 1, "/system.slice/" + service.unit());
  }

  private static MorningDatabaseSession.Access database(AtomicInteger calls) {
    return (MorningDatabaseSession.Access)
        Proxy.newProxyInstance(
            MorningDatabaseSession.Access.class.getClassLoader(),
            new Class<?>[] {MorningDatabaseSession.Access.class},
            (unused, method, args) -> {
              calls.incrementAndGet();
              throw new AssertionError("invalid entry must not reach database provider");
            });
  }
}
