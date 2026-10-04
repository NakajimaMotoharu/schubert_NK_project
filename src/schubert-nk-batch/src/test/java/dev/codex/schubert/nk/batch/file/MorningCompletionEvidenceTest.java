package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.*;

import dev.codex.schubert.nk.batch.platform.MorningBackupUnitCycle;
import dev.codex.schubert.nk.batch.repository.*;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.time.*;
import java.util.*;
import org.junit.jupiter.api.Test;

/** PARENT455001/002 actual-data envelope, independent literal outcomes and full-row reread. */
final class MorningCompletionEvidenceTest {
  static final Clock CLOCK =
      Clock.fixed(Instant.parse("2026-09-13T02:03:00.123456789Z"), ZoneOffset.UTC);

  static MorningCompletionEvidence fixture(String mode) throws Exception {
    var input = MorningPrestartEvidenceTest.input(mode);
    var rows = input.backup().rows();
    return new MorningCompletionEvidence(
        mode.equals("failed")
            ? MorningBackupUnitCycle.Outcome.FAILED
            : MorningBackupUnitCycle.Outcome.SUCCESS,
        new MorningDatabaseSession.BackupBegins(
            rows.current().get(0).attempt(), rows.current().get(1).attempt()),
        mode.equals("failed")
            ? Optional.empty()
            : Optional.of(MorningPrestartEvidenceTest.MANIFEST),
        rows,
        input.backup().receipt(),
        input.cleanup(),
        input.expiry());
  }

  @Test
  void parent455001BackupFailureIsWarningNotAnAbsoluteGate() throws Exception {
    for (String mode : List.of("new", "reused", "failed")) {
      var f = fixture(mode);
      var result = f.completion(MorningPrestartEvidenceTest.EPOCH.activation(), CLOCK);
      assertEquals(
          mode.equals("failed")
              ? MaintenanceCompletion.Outcome.WARNING
              : MaintenanceCompletion.Outcome.SUCCESS,
          result.outcome());
      assertEquals(Instant.parse("2026-09-13T02:03:00.123456Z"), result.endedAt());
      assertEquals(MorningPrestartEvidenceTest.EPOCH.activation(), result.activation());
      assertEquals("MorningCompletionEvidence[actual=<redacted>]", f.toString());
    }
    var f = fixture("new");
    assertThrows(IOException.class, () -> f.completion(MorningCompletedMainTest.ACTIVATION, CLOCK));
    assertThrows(
        IOException.class,
        () ->
            f.completion(
                MorningPrestartEvidenceTest.EPOCH.activation(),
                Clock.fixed(MorningPrestartEvidenceTest.START.minusSeconds(1), ZoneOffset.UTC)));
  }

  @Test
  void parent455002FreshFullDatabaseAndReceiptsAreRequired() throws Exception {
    for (String mode : List.of("new", "reused", "failed")) {
      var f = fixture(mode);
      var events = new ArrayList<String>();
      MorningDatabaseSession.Access db = database(f, events, "");
      f.verify(
          db,
          CLOCK,
          () -> {
            events.add("owner");
            return 10_000_000_000L;
          });
      assertEquals(
          List.of(
              "owner",
              "recheckConsistent",
              "observeBackup",
              mode.equals("failed") ? "observeCleanupBackupUnavailable" : "observeCleanup",
              "cleanupReferences",
              "recheckExpiry",
              "recheckConsistent",
              "owner"),
          events);
      for (String failed :
          List.of(
              "recheckConsistent",
              "observeBackup",
              "observeCleanup",
              "cleanupReferences",
              "recheckExpiry")) {
        if (mode.equals("failed") && failed.equals("observeCleanup")) continue;
        assertThrows(
            IOException.class,
            () -> f.verify(database(f, new ArrayList<>(), failed), CLOCK, () -> 10_000_000_000L));
      }
    }
  }

  static MorningDatabaseSession.Access database(
      MorningCompletionEvidence f, List<String> events, String fault) {
    return (MorningDatabaseSession.Access)
        Proxy.newProxyInstance(
            MorningCompletionEvidenceTest.class.getClassLoader(),
            new Class<?>[] {MorningDatabaseSession.Access.class},
            (proxy, method, args) -> {
              String name = method.getName();
              events.add(name);
              if (name.equals(fault)) throw new IOException("fixed DB fault");
              return switch (name) {
                case "recheckConsistent" -> {
                  assertEquals(MorningPrestartEvidenceTest.RUN, args[0]);
                  yield null;
                }
                case "observeBackup" -> {
                  assertEquals(f.begins(), args[0]);
                  assertEquals(f.manifest(), args[1]);
                  assertEquals(Instant.parse("2026-09-13T02:03:00.123456Z"), args[2]);
                  yield f.backup();
                }
                case "observeCleanup", "observeCleanupBackupUnavailable" -> {
                  assertEquals(MorningPrestartEvidenceTest.RUN, args[0]);
                  yield f.cleanup().terminal();
                }
                case "cleanupReferences" -> {
                  assertEquals(f.cleanup().terminal(), args[0]);
                  yield f.cleanup().references();
                }
                case "recheckExpiry" -> {
                  assertEquals(f.expiry(), args[0]);
                  yield null;
                }
                default -> throw new AssertionError("unexpected DB operation " + name);
              };
            });
  }

  @Test
  void parent455004MismatchedManifestReceiptAndNullContractReject() throws Exception {
    var f = fixture("new");
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCompletionEvidence(
                MorningBackupUnitCycle.Outcome.FAILED,
                f.begins(),
                f.manifest(),
                f.backup(),
                f.backupReceipt(),
                f.cleanup(),
                f.expiry()));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new MorningCompletionEvidence(
                f.backupOutcome(),
                f.begins(),
                Optional.empty(),
                f.backup(),
                f.backupReceipt(),
                f.cleanup(),
                f.expiry()));
    assertThrows(
        NullPointerException.class,
        () ->
            new MorningCompletionEvidence(
                null,
                f.begins(),
                f.manifest(),
                f.backup(),
                f.backupReceipt(),
                f.cleanup(),
                f.expiry()));
    assertThrows(NullPointerException.class, () -> f.verify(null, CLOCK, () -> 10_000_000_000L));
    assertThrows(
        NullPointerException.class,
        () -> f.verify(database(f, new ArrayList<>(), ""), null, () -> 10_000_000_000L));
    assertThrows(
        NullPointerException.class,
        () -> f.verify(database(f, new ArrayList<>(), ""), CLOCK, null));
    assertThrows(NullPointerException.class, () -> f.completion(null, CLOCK));
    assertThrows(
        NullPointerException.class,
        () -> f.completion(MorningPrestartEvidenceTest.EPOCH.activation(), null));
  }
}
