package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** OPS009/BAK001/UI251/SS341/342/343/SSC104/PG334; CMAIN001..004 independent exit oracle. */
final class CleanupProcessMainTest {
  @Test
  void nativeExitIsActualWorkOnlyAndCannotUsePreflightObservation() {
    for (int actual : new int[] {0, 10, 30})
      assertEquals(actual, CleanupProcessMain.runNative(new String[0], () -> actual));
    assertEquals(30, CleanupProcessMain.runNative(new String[0], () -> 50));
    assertEquals(
        70,
        CleanupProcessMain.runNative(
            new String[] {"--override"},
            () -> {
              fail("argument");
              return 0;
            }));
    assertEquals(
        30,
        CleanupProcessMain.runNative(
            new String[0],
            () -> {
              throw new IOException("PRIVATE");
            }));
    assertEquals(
        30,
        CleanupProcessMain.runNative(
            new String[0],
            () -> {
              throw new dev.codex.schubert.nk.batch.repository.BatchRepositoryException();
            }));
    assertEquals(
        30,
        CleanupProcessMain.runNative(
            new String[0],
            () -> {
              throw new dev.codex.schubert.nk.batch.cleanup.CleanupStoppedException(
                  dev.codex.schubert.nk.batch.cleanup.CleanupStopReason.TIME_LIMIT);
            }));
    var unknown = new AssertionError("PUBLIC");
    assertSame(
        unknown,
        assertThrows(
            AssertionError.class,
            () ->
                CleanupProcessMain.runNative(
                    new String[0],
                    () -> {
                      throw unknown;
                    })));
    assertThrows(NullPointerException.class, () -> CleanupProcessMain.runNative(null, () -> 0));
    assertThrows(
        NullPointerException.class, () -> CleanupProcessMain.runNative(new String[0], null));
  }

  @Test
  void expiryLiteralEntryAcceptsOnlyRealOutcomeAndUnknownIsNotNormalized() {
    for (int outcome : new int[] {0, 10, 30})
      assertEquals(outcome, CleanupProcessMain.runExpiry(new String[] {"--expiry"}, () -> outcome));
    assertEquals(30, CleanupProcessMain.runExpiry(new String[] {"--expiry"}, () -> 70));
    assertEquals(
        30,
        CleanupProcessMain.runExpiry(
            new String[] {"--expiry"},
            () -> {
              throw new IOException("PRIVATE_CANARY");
            }));
    for (String[] args :
        new String[][] {
          new String[0],
          new String[] {"--EXPIRY"},
          new String[] {"--expiry", "extra"},
          new String[] {null}
        })
      assertEquals(
          70,
          CleanupProcessMain.runExpiry(
              args,
              () -> {
                fail("unexpected work");
                return 0;
              }));
    var unknown = new NullPointerException("PRIVATE_CANARY");
    assertSame(
        unknown,
        assertThrows(
            NullPointerException.class,
            () ->
                CleanupProcessMain.runExpiry(
                    new String[] {"--expiry"},
                    () -> {
                      throw unknown;
                    })));
    var fatal = new AssertionError("PRIVATE_CANARY");
    assertSame(
        fatal,
        assertThrows(
            AssertionError.class,
            () ->
                CleanupProcessMain.runExpiry(
                    new String[] {"--expiry"},
                    () -> {
                      throw fatal;
                    })));
    assertThrows(NullPointerException.class, () -> CleanupProcessMain.runExpiry(null, () -> 0));
    assertThrows(
        NullPointerException.class,
        () -> CleanupProcessMain.runExpiry(new String[] {"--expiry"}, null));
  }

  @Test
  void noArgumentsCannotMintSuccessEvenAfterPreflightObservation() { // CMAIN001
    AtomicInteger checks = new AtomicInteger();
    int status =
        CleanupProcessMain.run(
            new String[0],
            () -> {
              checks.incrementAndGet();
              return BackupArtifactFixture.expected();
            });
    assertEquals(30, status); // SS341: only completed DELETE/skip+transfer may yield 0/10.
    assertEquals(1, checks.get());
  }

  @Test
  void argumentNeverReadsRootOrPrivateMaterial() { // CMAIN002
    AtomicInteger checks = new AtomicInteger();
    assertEquals(
        70,
        CleanupProcessMain.run(
            new String[] {"--run-id", "123"},
            () -> {
              checks.incrementAndGet();
              return BackupArtifactFixture.expected();
            }));
    assertEquals(0, checks.get());
  }

  @Test
  void knownPreflightFailureIsFixedNonSuccessAndUnknownIsNotNormalized() { // CMAIN003
    assertEquals(
        30,
        CleanupProcessMain.run(
            new String[0],
            () -> {
              throw new IOException("PRIVATE_CANARY");
            }));
    var unexpected = new IllegalStateException("PRIVATE_CANARY");
    assertSame(
        unexpected,
        assertThrows(
            IllegalStateException.class,
            () ->
                CleanupProcessMain.run(
                    new String[0],
                    () -> {
                      throw unexpected;
                    })));
  }

  @Test
  void nullContractsAndNativeRootlessRefusal() { // CMAIN004/NCLEAN001
    assertThrows(NullPointerException.class, () -> CleanupProcessMain.run(null, () -> null));
    assertThrows(NullPointerException.class, () -> CleanupProcessMain.run(new String[0], null));
    assertThrows(
        NullPointerException.class, () -> CleanupProcessMain.run(new String[0], () -> null));
    assertThrows(IOException.class, CleanupNativePreflight::verify);
  }
}
