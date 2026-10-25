package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS341/343/PG338; PT-OPS-MPASS001-009. */
final class MorningStopPassTest {
  private static final List<MaintenanceUnit> ORDER =
      List.of(
          MaintenanceUnit.CADDY,
          MaintenanceUnit.WEB,
          MaintenanceUnit.API,
          MaintenanceUnit.CLEANUP,
          MaintenanceUnit.INSPECTOR,
          MaintenanceUnit.EXPIRY,
          MaintenanceUnit.BACKUP,
          MaintenanceUnit.ARTEMIS);

  private static MorningStopPass.Attempt finished(MaintenanceUnitStopClient.Status status) {
    return new MorningStopPass.Attempt() {
      public MaintenanceUnitStopClient.Status status() {
        return status;
      }

      public MaintenanceUnitStopClient.Status awaitClient() {
        fail("already terminal");
        return MaintenanceUnitStopClient.Status.UNKNOWN;
      }
    };
  }

  @Test
  void mpass001AllStopsBeforeFreshWholeSet() throws Exception {
    var stopped = new ArrayList<MaintenanceUnit>();
    var observed = new ArrayList<MaintenanceUnit>();
    var order = new ArrayList<String>();
    var gates = new AtomicInteger();
    new MorningStopPass(
            () -> gates.incrementAndGet(),
            new MorningStopPass.Stop() {
              public void preflight() {
                order.add("preflight");
              }

              public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                stopped.add(unit);
                order.add("stop-" + unit);
                return finished(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO);
              }
            },
            new MorningStopPass.Terminals() {
              public void require(MaintenanceUnit unit) {
                observed.add(unit);
                order.add("terminal-" + unit);
              }

              public void requireAll() {
                assertEquals(ORDER, observed);
                order.add("all-eight-fresh");
              }
            })
        .execute();
    assertEquals(ORDER, stopped);
    assertEquals(ORDER, observed);
    assertEquals("preflight", order.getFirst());
    assertEquals("all-eight-fresh", order.getLast());
    for (int i = 0; i < ORDER.size(); i++) {
      assertEquals("stop-" + ORDER.get(i), order.get(i * 2 + 1));
      assertEquals("terminal-" + ORDER.get(i), order.get(i * 2 + 2));
    }
    assertEquals(18, gates.get()); // before preflight, twice per Unit, after complete set.
  }

  @Test
  void mpass002PreflightRefusalStartsNothing() {
    var failure = new IOException("policy unavailable");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                new MorningStopPass(
                        () -> {},
                        new MorningStopPass.Stop() {
                          public void preflight() throws IOException {
                            throw failure;
                          }

                          public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                            return fail("no stop on failed preflight");
                          }
                        },
                        new NoTerminals())
                    .execute()));
  }

  @Test
  void mpass003NonzeroClientCannotCountAsUnitStop() {
    for (MaintenanceUnit failed : List.of(MaintenanceUnit.CADDY, MaintenanceUnit.ARTEMIS)) {
      var stopped = new ArrayList<MaintenanceUnit>();
      var observed = new ArrayList<MaintenanceUnit>();
      IOException refusal =
          assertThrows(
              IOException.class,
              () ->
                  new MorningStopPass(
                          () -> {},
                          new MorningStopPass.Stop() {
                            public void preflight() {}

                            public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                              stopped.add(unit);
                              return finished(
                                  unit == failed
                                      ? MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO
                                      : MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO);
                            }
                          },
                          new MorningStopPass.Terminals() {
                            public void require(MaintenanceUnit unit) {
                              observed.add(unit);
                            }

                            public void requireAll() {
                              fail("no full success");
                            }
                          })
                      .execute());
      assertEquals("Morning stop pass unavailable", refusal.getMessage());
      assertEquals(failed.ordinal() + 1, stopped.size());
      assertEquals(failed.ordinal(), observed.size());
    }
  }

  @Test
  void mpass004UnitNotQuiescentStopsNextClient() {
    var stopped = new ArrayList<MaintenanceUnit>();
    IOException refusal =
        assertThrows(
            IOException.class,
            () ->
                new MorningStopPass(
                        () -> {},
                        new MorningStopPass.Stop() {
                          public void preflight() {}

                          public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                            stopped.add(unit);
                            return finished(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO);
                          }
                        },
                        new MorningStopPass.Terminals() {
                          public void require(MaintenanceUnit unit) throws IOException {
                            if (unit == MaintenanceUnit.WEB) throw new IOException("not terminal");
                          }

                          public void requireAll() {
                            fail("no full success");
                          }
                        })
                    .execute());
    assertEquals("not terminal", refusal.getMessage());
    assertEquals(List.of(MaintenanceUnit.CADDY, MaintenanceUnit.WEB), stopped);
  }

  @Test
  void mpass005UnknownIsReapedBeforeUnitObservation() throws Exception {
    var awaited = new AtomicInteger();
    var observed = new AtomicInteger();
    var pass =
        new MorningStopPass(
            () -> {},
            new MorningStopPass.Stop() {
              public void preflight() {}

              public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                if (unit != MaintenanceUnit.CADDY)
                  return finished(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO);
                return new MorningStopPass.Attempt() {
                  public MaintenanceUnitStopClient.Status status() {
                    return MaintenanceUnitStopClient.Status.UNKNOWN;
                  }

                  public MaintenanceUnitStopClient.Status awaitClient() {
                    assertEquals(0, observed.get());
                    return awaited.incrementAndGet() == 1
                        ? MaintenanceUnitStopClient.Status.UNKNOWN
                        : MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
                  }
                };
              }
            },
            new MorningStopPass.Terminals() {
              public void require(MaintenanceUnit unit) {
                observed.incrementAndGet();
              }

              public void requireAll() {
                assertEquals(8, observed.get());
              }
            });
    pass.execute();
    assertEquals(2, awaited.get());
    assertEquals(8, observed.get());
  }

  @Test
  void mpass006UnknownKeepsCallerScopeUntilRealTerminal() throws Exception {
    var release = new CountDownLatch(1);
    var firstAwait = new CountDownLatch(1);
    try (var workers = Executors.newSingleThreadExecutor()) {
      var result =
          workers.submit(
              () -> {
                new MorningStopPass(
                        () -> {},
                        new MorningStopPass.Stop() {
                          public void preflight() {}

                          public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                            if (unit != MaintenanceUnit.CADDY)
                              return finished(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO);
                            return new MorningStopPass.Attempt() {
                              public MaintenanceUnitStopClient.Status status() {
                                return MaintenanceUnitStopClient.Status.UNKNOWN;
                              }

                              public MaintenanceUnitStopClient.Status awaitClient() {
                                firstAwait.countDown();
                                return release.getCount() == 0
                                    ? MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO
                                    : MaintenanceUnitStopClient.Status.UNKNOWN;
                              }
                            };
                          }
                        },
                        new NoTerminals())
                    .execute();
                return true;
              });
      try {
        assertTrue(firstAwait.await(2, TimeUnit.SECONDS));
        assertFalse(result.isDone(), "UNKNOWN must not return to an M-owning caller");
      } finally {
        release.countDown();
      }
      assertTrue(result.get(2, TimeUnit.SECONDS));
    }
  }

  @Test
  void mpass007InterruptedReapPreservesFlagUntilTerminal() throws Exception {
    var awaited = new AtomicInteger();
    try {
      Thread.currentThread().interrupt();
      new MorningStopPass(
              () -> {},
              new MorningStopPass.Stop() {
                public void preflight() {}

                public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                  if (unit != MaintenanceUnit.CADDY)
                    return finished(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO);
                  return new MorningStopPass.Attempt() {
                    public MaintenanceUnitStopClient.Status status() {
                      return MaintenanceUnitStopClient.Status.UNKNOWN;
                    }

                    public MaintenanceUnitStopClient.Status awaitClient() {
                      assertFalse(Thread.currentThread().isInterrupted());
                      awaited.incrementAndGet();
                      return MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO;
                    }
                  };
                }
              },
              new NoTerminals())
          .execute();
      assertEquals(1, awaited.get());
      assertTrue(Thread.currentThread().isInterrupted());
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void mpass008NullContractsAndWrongActor() throws Exception {
    assertThrows(NullPointerException.class, () -> new MorningStopPass(null, null, null));
    assertThrows(
        NullPointerException.class, () -> new MorningStopPass(() -> {}, null, new NoTerminals()));
    assertThrows(
        NullPointerException.class, () -> new MorningStopPass(() -> {}, new NeverStop(), null));
    assertThrows(NullPointerException.class, () -> MorningStopPass.create(null, null));
    var fixture = new RootStartupContextTest.Fixture();
    var context = fixture.context();
    var api = context.capture(RootStartupContext.Service.API);
    IOException refusal =
        assertThrows(IOException.class, () -> MorningStopPass.create(context, api));
    assertEquals("Morning stop pass unavailable", refusal.getMessage());
    assertNull(refusal.getCause());
  }

  /** PT-OPS-MPASS010: new interrupt during UNKNOWN never releases the caller's stop pass. */
  @Test
  void mpass010NewInterruptDuringUnknownPreservesFlagAndAllTerminalObservations() throws Exception {
    var entered = new CountDownLatch(1);
    var release = new CountDownLatch(1);
    var thread = new AtomicReference<Thread>();
    var awaited = new AtomicInteger();
    var stopped = new ArrayList<MaintenanceUnit>();
    var observed = new ArrayList<MaintenanceUnit>();
    try (var worker = Executors.newSingleThreadExecutor()) {
      var result =
          worker.submit(
              () -> {
                thread.set(Thread.currentThread());
                new MorningStopPass(
                        () -> {},
                        new MorningStopPass.Stop() {
                          public void preflight() {}

                          public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                            stopped.add(unit);
                            if (unit != MaintenanceUnit.CADDY)
                              return finished(MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO);
                            return new MorningStopPass.Attempt() {
                              public MaintenanceUnitStopClient.Status status() {
                                entered.countDown();
                                return MaintenanceUnitStopClient.Status.UNKNOWN;
                              }

                              public MaintenanceUnitStopClient.Status awaitClient() {
                                awaited.incrementAndGet();
                                return release.getCount() == 0
                                    ? MaintenanceUnitStopClient.Status.CLIENT_EXITED_ZERO
                                    : MaintenanceUnitStopClient.Status.UNKNOWN;
                              }
                            };
                          }
                        },
                        new MorningStopPass.Terminals() {
                          public void require(MaintenanceUnit unit) {
                            observed.add(unit);
                          }

                          public void requireAll() {
                            assertEquals(ORDER, observed);
                          }
                        })
                    .execute();
                return Thread.currentThread().isInterrupted();
              });
      try {
        assertTrue(entered.await(5, TimeUnit.SECONDS));
        long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(5);
        Thread.State state;
        do {
          state = thread.get().getState();
          if (state == Thread.State.TIMED_WAITING) break;
          Thread.onSpinWait();
        } while (System.nanoTime() < deadline);
        assertEquals(Thread.State.TIMED_WAITING, state);
        assertFalse(result.isDone());
        thread.get().interrupt();
      } finally {
        release.countDown();
      }
      assertTrue(result.get(5, TimeUnit.SECONDS));
      assertEquals(ORDER, stopped);
      assertEquals(ORDER, observed);
      assertTrue(awaited.get() >= 1);
    }
  }

  @Test
  void mpass009ReapedNonzeroNeverObservesUnitOrStartsNext() {
    var awaited = new AtomicInteger();
    IOException refusal =
        assertThrows(
            IOException.class,
            () ->
                new MorningStopPass(
                        () -> {},
                        new MorningStopPass.Stop() {
                          public void preflight() {}

                          public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
                            assertEquals(MaintenanceUnit.CADDY, unit);
                            return new MorningStopPass.Attempt() {
                              public MaintenanceUnitStopClient.Status status() {
                                return MaintenanceUnitStopClient.Status.UNKNOWN;
                              }

                              public MaintenanceUnitStopClient.Status awaitClient() {
                                awaited.incrementAndGet();
                                return MaintenanceUnitStopClient.Status.CLIENT_EXITED_NONZERO;
                              }
                            };
                          }
                        },
                        new MorningStopPass.Terminals() {
                          public void require(MaintenanceUnit unit) {
                            fail("nonzero is not a Unit stop");
                          }

                          public void requireAll() {
                            fail("nonzero is not full success");
                          }
                        })
                    .execute());
    assertEquals(1, awaited.get());
    assertEquals("Morning stop pass unavailable", refusal.getMessage());
    assertNull(refusal.getCause());
  }

  private static final class NeverStop implements MorningStopPass.Stop {
    public void preflight() {}

    public MorningStopPass.Attempt stop(MaintenanceUnit unit) {
      return fail("not called");
    }
  }

  private static final class NoTerminals implements MorningStopPass.Terminals {
    public void require(MaintenanceUnit unit) {}

    public void requireAll() {}
  }
}
