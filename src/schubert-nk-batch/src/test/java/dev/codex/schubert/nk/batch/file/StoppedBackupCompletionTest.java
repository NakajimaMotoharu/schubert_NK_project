package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.platform.BackupUnitReceiptGate;
import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.platform.StoppedBackupFixture;
import dev.codex.schubert.nk.batch.repository.MaintenanceCompletion;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** BUG704/SSC187; independent STOPCOMP001..003 stopped versus KEEP_ACTIVE receipt contract. */
final class StoppedBackupCompletionTest {
  private static MorningCompletionEvidence bound(
      MorningCompletionEvidence f,
      MorningBackupUnitCycle cycle,
      BackupUnitReceiptGate.TerminalReceipt receipt) {
    return new MorningCompletionEvidence(
        f.backupOutcome(),
        f.begins(),
        f.manifest(),
        f.backup(),
        receipt,
        cycle,
        f.cleanup(),
        f.expiry());
  }

  private static void verify(MorningCompletionEvidence f) throws IOException {
    f.verify(
        MorningCompletionEvidenceTest.database(f, new ArrayList<>(), ""),
        MorningCompletionEvidenceTest.CLOCK,
        () -> 10_000_000_000L);
  }

  @Test
  void stopcomp001ExplicitStopKeepsActualOutcomeNotTheActiveReceiptProfile() throws Exception {
    for (String mode : List.of("new", "reused", "failed")) {
      var original = MorningCompletionEvidenceTest.fixture(mode);
      var stopped = new StoppedBackupFixture(mode.equals("failed") ? 30 : 0, true);
      assertEquals(
          List.of(
              "fresh-receipt",
              "explicit-stop",
              "stopped-readback",
              "actual-completion",
              "stopped-readback",
              "original-request",
              "intent-retired"),
          stopped.events);
      assertEquals(mode.equals("failed") ? 30 : 0, stopped.receipt.exitCode());
      if (!mode.equals("failed")) {
        // This is the pre-fix failure: actual stopped bus fields no longer match active/exited.
        assertThrows(IOException.class, stopped.receipt::requireStillPresent);
      }
      var f = bound(original, stopped.cycle, stopped.receipt);
      verify(f);
      assertSame(stopped.cycle, f.backupCycle());
      assertSame(stopped.receipt, f.backupReceipt());
      assertEquals("stopped-readback", stopped.events.getLast());
      stopped.current.set(StoppedBackupFixture.COLD);
      verify(f); // Full GC cold is accepted ONLY with this observed and explicitly stopped cycle.
      assertEquals(
          mode.equals("failed")
              ? MaintenanceCompletion.Outcome.WARNING
              : MaintenanceCompletion.Outcome.SUCCESS,
          f.completion(
                  MorningPrestartEvidenceTest.EPOCH.activation(),
                  MorningCompletionEvidenceTest.CLOCK)
              .outcome());
    }
  }

  @Test
  void stopcomp002ChangedGenerationPartialColdKernelOwnerAndDeadlineReject() throws Exception {
    var base = MorningCompletionEvidenceTest.fixture("new");
    var stopped = new StoppedBackupFixture(0, true);
    var f = bound(base, stopped.cycle, stopped.receipt);
    for (String invalid :
        List.of(
            stopped.stopped.replace(
                "77777777777777777777777777777777", "88888888888888888888888888888888"),
            stopped.stopped.replace("ExecMainStatus=0", "ExecMainStatus=30"),
            stopped.stopped.replace(
                "ExecMainExitTimestampMonotonic=2000000", "ExecMainExitTimestampMonotonic=2000001"),
            StoppedBackupFixture.COLD.replace(
                "ExecMainStartTimestampMonotonic=0", "ExecMainStartTimestampMonotonic=1"))) {
      stopped.current.set(invalid);
      assertThrows(IOException.class, () -> verify(f));
    }
    stopped.current.set(stopped.stopped);
    stopped.kernelEmpty.set(false);
    assertThrows(IOException.class, () -> verify(f));
    stopped.kernelEmpty.set(true);
    stopped.ownerValid.set(false);
    assertThrows(IOException.class, () -> verify(f));
    stopped.ownerValid.set(true);
    stopped.nanos.set(1_799_999_999_999L);
    verify(f);
    stopped.nanos.set(1_800_000_000_000L);
    assertThrows(IOException.class, () -> verify(f));
  }

  @Test
  void stopcomp003CompletedCycleAndExactReceiptCannotBeSubstituted() throws Exception {
    var base = MorningCompletionEvidenceTest.fixture("new");
    var first = new StoppedBackupFixture(0, true);
    var second = new StoppedBackupFixture(0, true);
    assertNotSame(first.receipt, second.receipt);
    assertEquals(first.receipt.invocation(), second.receipt.invocation());
    assertEquals(first.receipt.exitCode(), second.receipt.exitCode());
    assertThrows(IOException.class, () -> verify(bound(base, first.cycle, second.receipt)));
    var unfinished = new StoppedBackupFixture(0, false);
    assertThrows(
        IOException.class, () -> verify(bound(base, unfinished.cycle, unfinished.receipt)));
    assertThrows(NullPointerException.class, () -> bound(base, null, first.receipt));
    assertThrows(NullPointerException.class, () -> bound(base, first.cycle, null));
    verify(bound(base, first.cycle, first.receipt));
    verify(bound(base, second.cycle, second.receipt));
  }

  @Test
  void stopcomp003FullRowAndOriginalReferenceChangesStillReject() throws Exception {
    var f = MorningCompletionEvidenceTest.fixture("new");
    var reused = MorningCompletionEvidenceTest.fixture("reused");
    for (String changed : List.of("observeBackup", "observeCleanup", "cleanupReferences")) {
      var ordinary = MorningCompletionEvidenceTest.database(f, new ArrayList<>(), "");
      var actual =
          (MorningDatabaseSession.Access)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {MorningDatabaseSession.Access.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals(changed))
                      return switch (changed) {
                        case "observeBackup" -> reused.backup();
                        case "observeCleanup" -> reused.cleanup().terminal();
                        case "cleanupReferences" -> reused.cleanup().references();
                        default -> throw new AssertionError("closed DB readback method");
                      };
                    return method.invoke(ordinary, args);
                  });
      assertThrows(
          IOException.class,
          () -> f.verify(actual, MorningCompletionEvidenceTest.CLOCK, () -> 10_000_000_000L));
    }
  }
}
