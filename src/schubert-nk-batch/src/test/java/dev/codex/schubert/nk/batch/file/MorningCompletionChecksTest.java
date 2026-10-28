package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.batch.platform.BackupUnitStartClient;
import dev.codex.schubert.nk.batch.repository.MorningDatabaseSession;
import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-OPS-TXOWNER001..004; SS342 SSC185/BUG693. Stateful TX oracle is independent of DB code. */
final class MorningCompletionChecksTest {
  private static final String FIXTURE_PEER_B7216580 = "peer";

  @Test
  void txowner001PeerBracketsDatabaseButTransactionOwnerNeverReadsIt() throws Exception {
    var events = new ArrayList<String>();
    var autoCommit = new AtomicBoolean(true);
    BackupUnitStartClient.RetirementGate db =
        () -> {
          if (!autoCommit.get()) throw new IOException("independent nested DB rejection");
          events.add("DB");
        };
    var checks = new MorningCompletionChecks(() -> events.add(FIXTURE_PEER_B7216580), db);
    checks.verify();
    assertEquals(List.of(FIXTURE_PEER_B7216580, "DB", FIXTURE_PEER_B7216580), events);
    events.clear();
    autoCommit.set(false);
    // Former production callback calls a combined gate from a repository TX: reproduce refusal.
    assertThrows(IOException.class, checks::verify);
    assertEquals(List.of(FIXTURE_PEER_B7216580), events);
    events.clear();
    var owner = checks.ownerGuard(() -> 71L);
    assertEquals(71L, owner.remainingNanos());
    assertEquals(71L, owner.remainingNanos());
    assertEquals(List.of(FIXTURE_PEER_B7216580, FIXTURE_PEER_B7216580), events);
    assertFalse(autoCommit.get());
    autoCommit.set(true);
    checks.verify();
    assertEquals(
        List.of(
            FIXTURE_PEER_B7216580,
            FIXTURE_PEER_B7216580,
            FIXTURE_PEER_B7216580,
            "DB",
            FIXTURE_PEER_B7216580),
        events);
  }

  @Test
  void txowner002EveryEvidenceReadInvokesOwnerInTheSameOpenTransaction() throws Exception {
    for (String mode : List.of("new", "reused", "failed")) {
      var fixture = MorningCompletionEvidenceTest.fixture(mode);
      var autoCommit = new AtomicBoolean(true);
      var txCalls = new AtomicInteger();
      var peers = new AtomicInteger();
      var delegate = MorningCompletionEvidenceTest.database(fixture, new ArrayList<>(), "");
      var db =
          (MorningDatabaseSession.Access)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {MorningDatabaseSession.Access.class},
                  (proxy, method, args) -> {
                    assertTrue(autoCommit.get(), "no nested entry");
                    if (method.getName().equals("recheckConsistent"))
                      return method.invoke(delegate, args);
                    // Independent SSC200 argument catalog: the original lookup follows the guard.
                    int guardIndex =
                        method.getName().equals("cleanupReferences") ? 1 : args.length - 1;
                    assertEquals(
                        MaintenanceOwnerFrame.Guard.class, method.getParameterTypes()[guardIndex]);
                    if (method.getName().equals("cleanupReferences") && args.length == 3) {
                      assertEquals(
                          dev.codex.schubert.nk.batch.repository.SuccessRunLookup.class,
                          method.getParameterTypes()[2]);
                      assertNotNull(args[2]);
                    }
                    var guard = (MaintenanceOwnerFrame.Guard) args[guardIndex];
                    autoCommit.set(false);
                    try {
                      assertEquals(83L, guard.remainingNanos());
                      Object value = method.invoke(delegate, args);
                      assertEquals(83L, guard.remainingNanos());
                      txCalls.incrementAndGet();
                      return value;
                    } finally {
                      assertFalse(autoCommit.get(), "owner must not commit/rollback the TX");
                      autoCommit.set(true);
                    }
                  });
      var checks =
          new MorningCompletionChecks(
              peers::incrementAndGet,
              () -> {
                assertTrue(autoCommit.get(), "DB guard outside TX only");
                db.recheckConsistent(MorningPrestartEvidenceTest.RUN);
              });
      checks.verify();
      fixture.verify(db, MorningCompletionEvidenceTest.CLOCK, checks.ownerGuard(() -> 83L));
      checks.verify();
      assertEquals(4, txCalls.get());
      assertEquals(22, peers.get()); // Four compound read boundaries additionally retain old guard.
      assertTrue(autoCommit.get());
    }
  }

  @Test
  void txowner003PeerDatabaseBudgetFailuresCannotBeAccepted() throws Exception {
    for (int failAt : List.of(1, 2)) {
      var peers = new AtomicInteger();
      var db = new AtomicInteger();
      var failure = new IOException("independent peer changed");
      var checks =
          new MorningCompletionChecks(
              () -> {
                if (peers.incrementAndGet() == failAt) throw failure;
              },
              db::incrementAndGet);
      assertSame(failure, assertThrows(IOException.class, checks::verify));
      assertEquals(failAt, peers.get());
      assertEquals(failAt - 1, db.get());
    }
    var peerCount = new AtomicInteger();
    var failedDb = new IOException("independent DB failure");
    var checks =
        new MorningCompletionChecks(
            peerCount::incrementAndGet,
            () -> {
              throw failedDb;
            });
    assertSame(failedDb, assertThrows(IOException.class, checks::verify));
    assertEquals(1, peerCount.get());
    var expired = new IOException("independent parent expired");
    assertSame(
        expired,
        assertThrows(
            IOException.class,
            () ->
                checks
                    .ownerGuard(
                        () -> {
                          throw expired;
                        })
                    .check()));
    assertEquals(2, peerCount.get());
    var changed =
        new MorningCompletionChecks(
            () -> {
              throw failedDb;
            },
            () -> {});
    assertSame(
        failedDb, assertThrows(IOException.class, () -> changed.ownerGuard(() -> 1L).check()));
  }

  @Test
  void txowner004NullInputsRefuseAtBoundary() {
    assertThrows(NullPointerException.class, () -> new MorningCompletionChecks(null, () -> {}));
    assertThrows(NullPointerException.class, () -> new MorningCompletionChecks(() -> {}, null));
    var checks = new MorningCompletionChecks(() -> {}, () -> {});
    assertThrows(NullPointerException.class, () -> checks.ownerGuard(null));
    assertThrows(NullPointerException.class, () -> checks.ownerGuard(() -> 1L, null));
  }

  /** COMP203001: SQL callbacks retain live ownership, full peers only at compound boundaries. */
  @Test
  void comp203001FullBoundaryAndRetainedOwnerAreIndependentAndFailClosed() throws Exception {
    var full = new AtomicInteger();
    var local = new AtomicInteger();
    var checks = new MorningCompletionChecks(full::incrementAndGet, () -> {});
    var alive = new AtomicBoolean(true);
    var failure = new IOException("independent retained owner expired");
    var owner =
        checks.ownerGuard(
            () -> 71L,
            () -> {
              if (!alive.get()) throw failure;
              local.incrementAndGet();
            });
    checks.verify();
    assertEquals(2, full.get());
    for (int i = 0; i < 52; i++) assertEquals(71L, owner.remainingNanos());
    assertEquals(52, local.get());
    assertEquals(2, full.get());
    alive.set(false);
    assertSame(failure, assertThrows(IOException.class, owner::check));
    assertEquals(52, local.get());
    assertEquals(2, full.get());
    checks.verify();
    assertEquals(4, full.get());
  }
}
