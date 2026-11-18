package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** OPS009/FIL/UI237/251/SS333; SSC063/PG170; PT-OPS-RSCOPE001..008,018027. */
final class ResourceScopeTest {
  private static final int CLOSE_FAILURE_MODE = 1;
  private static final int SUCCESSFUL_BODY_MODE = 1;
  private static final String BODY_EVENT = "body";

  @Test
  void successfulOwnership() throws Exception {
    List<String> order = new ArrayList<>();
    int result =
        ResourceScope.use(
            () -> order.add("close"),
            () -> {
              order.add(BODY_EVENT);
              return 42;
            });
    assertEquals(42, result);
    assertEquals(List.of(BODY_EVENT, "close"), order);
  }

  @Test
  void knownIoFailures() {
    for (StorageIoException.Reason reason : StorageIoException.Reason.values())
      for (boolean cleanup : List.of(false, true)) {
        AtomicInteger closed = new AtomicInteger();
        var primary = new StorageIoException(reason);
        primary.initCause(new IOException("public raw cause"));
        var actual =
            assertThrows(
                StorageIoException.class,
                () ->
                    ResourceScope.use(
                        () -> {
                          closed.incrementAndGet();
                          if (cleanup) throw new IOException("public close");
                        },
                        () -> {
                          throw primary;
                        }));
        fixed(actual, cleanup ? StorageIoException.Reason.UNAVAILABLE : reason);
        assertEquals(1, closed.get());
      }
    for (int mode = 0; mode < 4; mode++) {
      int chosen = mode;
      AtomicInteger closed = new AtomicInteger();
      var actual =
          assertThrows(
              StorageIoException.class,
              () ->
                  ResourceScope.use(
                      () -> {
                        closed.incrementAndGet();
                        if (chosen == CLOSE_FAILURE_MODE) throw new IOException("public close");
                      },
                      () -> {
                        if (chosen == SUCCESSFUL_BODY_MODE) return 42;
                        if (chosen == 0) throw new IOException("public body");
                        var primary = new StorageIoException(StorageIoException.Reason.MISSING);
                        primary.addSuppressed(
                            chosen == 2
                                ? new IOException("public prior")
                                : new AssertionError("public prior"));
                        throw primary;
                      }));
      fixed(actual, StorageIoException.Reason.UNAVAILABLE);
      assertEquals(1, closed.get());
    }
  }

  @Test
  void unknownBodyFailures() {
    for (Throwable primary : unknowns()) {
      AtomicInteger closed = new AtomicInteger();
      assertSame(
          primary,
          assertThrows(
              primary.getClass(),
              () ->
                  ResourceScope.use(
                      closed::incrementAndGet,
                      () -> {
                        raise(primary);
                        return 42;
                      })));
      assertEquals(1, closed.get());
      assertEquals(0, primary.getSuppressed().length);
    }
  }

  @Test
  void knownBodyUnknownCleanup() {
    for (Throwable cleanup : unknowns())
      for (boolean successfulBody : List.of(false, true)) {
        AtomicInteger closed = new AtomicInteger();
        assertSame(
            cleanup,
            assertThrows(
                cleanup.getClass(),
                () ->
                    ResourceScope.use(
                        () -> {
                          closed.incrementAndGet();
                          raise(cleanup);
                        },
                        () -> {
                          if (!successfulBody) throw new IOException("public body");
                          return 42;
                        })));
        assertEquals(1, closed.get());
      }
  }

  @Test
  void unknownCompoundFailures() {
    for (int primaryKind = 0; primaryKind < 3; primaryKind++)
      for (int cleanupKind = 0; cleanupKind < 5; cleanupKind++) {
        Throwable primary = unknowns().get(primaryKind);
        Throwable cleanup =
            cleanupKind == 4
                ? primary
                : cleanupKind == 0
                    ? new IOException("public close")
                    : unknowns().get(cleanupKind - 1);
        AtomicInteger closed = new AtomicInteger();
        assertSame(
            primary,
            assertThrows(
                primary.getClass(),
                () ->
                    ResourceScope.use(
                        () -> {
                          closed.incrementAndGet();
                          raise(cleanup);
                        },
                        () -> {
                          raise(primary);
                          return 42;
                        })));
        assertEquals(1, closed.get());
        assertEquals(1, primary.getSuppressed().length);
        fixed(
            assertInstanceOf(StorageIoException.class, primary.getSuppressed()[0]),
            StorageIoException.Reason.UNAVAILABLE);
      }
  }

  @Test
  void nullAndNullableContracts() throws Exception {
    AtomicInteger closed = new AtomicInteger();
    assertThrows(NullPointerException.class, () -> ResourceScope.use(null, () -> 42));
    assertThrows(
        NullPointerException.class, () -> ResourceScope.use(closed::incrementAndGet, null));
    assertEquals(0, closed.get()); // Not admitted: caller still owns this resource.
    assertNull(ResourceScope.use(closed::incrementAndGet, () -> null));
    assertEquals(1, closed.get());
    var primary = new NullPointerException("public callback invariant");
    assertSame(
        primary,
        assertThrows(
            NullPointerException.class,
            () ->
                ResourceScope.use(
                    closed::incrementAndGet,
                    () -> {
                      throw primary;
                    })));
    assertEquals(2, closed.get());
  }

  @Test
  void nestedScopes() throws Exception {
    List<String> order = new ArrayList<>();
    assertEquals(
        42,
        ResourceScope.use(
            () -> order.add("outer-close"),
            () ->
                ResourceScope.use(
                    () -> order.add("inner-close"),
                    () -> {
                      order.add(BODY_EVENT);
                      return 42;
                    })));
    assertEquals(List.of(BODY_EVENT, "inner-close", "outer-close"), order);
    for (Throwable primary : unknowns()) {
      AtomicInteger closed = new AtomicInteger();
      assertSame(
          primary,
          assertThrows(
              primary.getClass(),
              () ->
                  ResourceScope.use(
                      () -> {
                        closed.incrementAndGet();
                        throw new IOException("public outer");
                      },
                      () ->
                          ResourceScope.use(
                              () -> {
                                closed.incrementAndGet();
                                raise(primary);
                              },
                              () -> {
                                raise(primary);
                                return 42;
                              }))));
      assertEquals(2, closed.get());
      assertEquals(2, primary.getSuppressed().length);
      for (Throwable s : primary.getSuppressed())
        fixed(assertInstanceOf(StorageIoException.class, s), StorageIoException.Reason.UNAVAILABLE);
    }
    var missing =
        assertThrows(
            StorageIoException.class,
            () ->
                ResourceScope.use(
                    () -> {},
                    () ->
                        ResourceScope.use(
                            () -> {},
                            () -> {
                              throw new StorageIoException(StorageIoException.Reason.MISSING);
                            })));
    fixed(missing, StorageIoException.Reason.MISSING);
  }

  @Test
  void concurrentScopes() throws Exception {
    AtomicInteger closed = new AtomicInteger();
    var pool = Executors.newVirtualThreadPerTaskExecutor();
    try {
      List<Future<Integer>> futures = new ArrayList<>();
      for (int i = 0; i < 64; i++) {
        int value = i;
        futures.add(
            pool.submit(() -> ResourceScope.use(closed::incrementAndGet, () -> value + 42)));
      }
      for (int i = 0; i < 64; i++) assertEquals(i + 42, futures.get(i).get(10, TimeUnit.SECONDS));
    } finally {
      pool.shutdownNow();
      assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS));
    }
    assertEquals(64, closed.get());
  }

  static List<Throwable> unknowns() {
    return List.of(
        new IllegalStateException("public runtime"),
        new NullPointerException("public invariant"),
        new AssertionError("public fatal"));
  }

  static void raise(Throwable value) throws IOException {
    if (value instanceof IOException io) throw io;
    if (value instanceof RuntimeException runtime) throw runtime;
    throw (Error) value;
  }

  static void fixed(StorageIoException actual, StorageIoException.Reason expected) {
    assertEquals(expected, actual.reason());
    assertEquals("transfer storage operation failed", actual.getMessage());
    assertNull(actual.getCause());
    assertEquals(0, actual.getSuppressed().length);
  }
}
