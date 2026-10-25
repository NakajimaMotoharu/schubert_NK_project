package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.LinuxFileLock;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/PG336; PT-OPS-MROOT001-006. */
final class MorningRootScopeTest {
  private static final class Held implements MorningRootScope.Exclusive {
    private final List<String> order;
    private final AtomicBoolean held;
    private boolean available = true;

    Held(List<String> order, AtomicBoolean held) {
      this.order = order;
      this.held = held;
    }

    @Override
    public <T> Optional<T> execute(LinuxFileLock.Operation<T> operation) throws IOException {
      order.add("M-enter");
      if (!available) return Optional.empty();
      held.set(true);
      try {
        return Optional.of(operation.execute());
      } finally {
        held.set(false);
        order.add("M-close");
      }
    }
  }

  @Test
  void mroot001RetainsRealOrderAndMThroughContinuation() throws Exception {
    var order = new ArrayList<String>();
    var held = new AtomicBoolean();
    var lock = new Held(order, held);
    var result =
        MorningRootScope.execute(
            () -> order.add("root"),
            lock,
            () -> {
              assertTrue(held.get());
              order.add("all-eight-policy");
            },
            () -> {
              assertTrue(held.get());
              order.add("trusted-continuation");
              return 7;
            });
    assertEquals(7, result);
    assertFalse(held.get());
    assertEquals(
        List.of(
            "root",
            "M-enter",
            "root",
            "all-eight-policy",
            "root",
            "trusted-continuation",
            "root",
            "M-close",
            "root"),
        order);
  }

  @Test
  void mroot002BusyMNeverInspectsUnitsOrContinues() {
    var order = new ArrayList<String>();
    var held = new AtomicBoolean();
    var lock = new Held(order, held);
    lock.available = false;
    assertThrows(
        IOException.class,
        () ->
            MorningRootScope.execute(
                () -> order.add("root"),
                lock,
                () -> fail("no policy on M contention"),
                () -> fail("no continuation on M contention")));
    assertEquals(List.of("root", "M-enter"), order);
    assertFalse(held.get());
  }

  @Test
  void mroot003PolicyRefusalNeverContinuesAndClosesM() {
    var order = new ArrayList<String>();
    var held = new AtomicBoolean();
    var failure = new IOException("fixed policy unavailable");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningRootScope.execute(
                    () -> order.add("root"),
                    new Held(order, held),
                    () -> {
                      assertTrue(held.get());
                      throw failure;
                    },
                    () -> fail("no continuation after policy failure"))));
    assertEquals(List.of("root", "M-enter", "root", "M-close"), order);
    assertFalse(held.get());
  }

  @Test
  void mroot004ContinuationFailureRetainsIdentityUntilMCloses() {
    var order = new ArrayList<String>();
    var held = new AtomicBoolean();
    var failure = new IOException("downstream failed");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningRootScope.execute(
                    () -> order.add("root"),
                    new Held(order, held),
                    () -> order.add("policy"),
                    () -> {
                      assertTrue(held.get());
                      throw failure;
                    })));
    assertEquals(List.of("root", "M-enter", "root", "policy", "root", "M-close"), order);
    assertFalse(held.get());
  }

  @Test
  void mroot005NullBoundaryAndRootRecheckFailure() {
    var order = new ArrayList<String>();
    var held = new AtomicBoolean();
    var lock = new Held(order, held);
    MorningRootScope.Gate root = () -> order.add("root");
    MorningRootScope.Policy policy = () -> order.add("policy");
    LinuxFileLock.Operation<Boolean> continuation = () -> true;
    assertThrows(
        NullPointerException.class,
        () -> MorningRootScope.execute(null, lock, policy, continuation));
    assertThrows(
        NullPointerException.class,
        () -> MorningRootScope.execute(root, null, policy, continuation));
    assertThrows(
        NullPointerException.class, () -> MorningRootScope.execute(root, lock, null, continuation));
    assertThrows(
        NullPointerException.class, () -> MorningRootScope.execute(root, lock, policy, null));
    assertThrows(
        NullPointerException.class, () -> MorningRootScope.execute(root, lock, policy, () -> null));
    assertFalse(held.get());
    order.clear();
    var failure = new IOException("root changed");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                MorningRootScope.execute(
                    () -> {
                      order.add("root");
                      if (order.size() == 8) throw failure;
                    },
                    lock,
                    policy,
                    continuation)));
    assertEquals(
        List.of("root", "M-enter", "root", "policy", "root", "root", "M-close", "root"), order);
    assertFalse(held.get());
  }

  @Test
  void mroot006EveryRootRecheckStopsAtItsOwnBoundary() {
    for (int failedCheck = 1; failedCheck <= 5; failedCheck++) {
      var order = new ArrayList<String>();
      var held = new AtomicBoolean();
      var failure = new IOException("root changed");
      var checks = new int[1];
      int target = failedCheck;
      assertSame(
          failure,
          assertThrows(
              IOException.class,
              () ->
                  MorningRootScope.execute(
                      () -> {
                        if (++checks[0] == target) throw failure;
                        order.add("root");
                      },
                      new Held(order, held),
                      () -> order.add("policy"),
                      () -> {
                        order.add("continuation");
                        return true;
                      })));
      assertFalse(held.get());
      assertEquals(target, checks[0]);
      assertEquals(target > 2 ? 1 : 0, order.stream().filter("policy"::equals).count());
      assertEquals(target > 3 ? 1 : 0, order.stream().filter("continuation"::equals).count());
      assertEquals(target > 1 ? 1 : 0, order.stream().filter("M-close"::equals).count());
    }
  }
}
