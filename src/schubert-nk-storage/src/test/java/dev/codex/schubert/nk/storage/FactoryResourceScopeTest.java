package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-IOFACT-001..012 / SS333 SSC308: literal ownership/exception table, no old use oracle. */
final class FactoryResourceScopeTest {
  @Test
  void factory001SuccessAndNullableBodyUseSameResourceOnce() throws Exception {
    for (boolean nullable : List.of(false, true)) {
      var token = new Token();
      var order = new ArrayList<String>();
      Object expected = nullable ? null : new Object();
      Object actual =
          ResourceScope.acquire(
              () -> {
                order.add("open");
                token.live = true;
                return token;
              },
              owned -> {
                assertSame(token, owned);
                order.add("close");
                token.live = false;
              },
              owned -> {
                assertSame(token, owned);
                assertTrue(owned.live);
                order.add("body");
                return expected;
              });
      assertSame(expected, actual);
      assertEquals(List.of("open", "body", "close"), order);
      assertFalse(token.live);
    }
    assertEquals("narrow", narrowStorageType(new Token()));
  }

  @Test
  void factory002EveryNullPortFailsBeforeAcquire() {
    var calls = new AtomicInteger();
    ResourceScope.Acquire<Token, IOException> acquire =
        () -> {
          calls.incrementAndGet();
          return new Token();
        };
    ResourceScope.Release<Token> release = value -> fail("release must not run");
    ResourceScope.OwnedAction<Token, String> body = value -> fail("body must not run");
    for (int i = 0; i < 3; i++) {
      int absent = i;
      assertThrows(
          NullPointerException.class,
          () ->
              ResourceScope.acquire(
                  absent == 0 ? null : acquire,
                  absent == 1 ? null : release,
                  absent == 2 ? null : body));
      assertEquals(0, calls.get());
    }
  }

  @Test
  void factory003NullAcquisitionNeverEntersBodyOrRelease() {
    var order = new ArrayList<String>();
    assertThrows(
        NullPointerException.class,
        () ->
            ResourceScope.acquire(
                () -> {
                  order.add("open");
                  return null;
                },
                value -> order.add("close"),
                value -> {
                  order.add("body");
                  return "bad";
                }));
    assertEquals(List.of("open"), order);
  }

  @Test
  void factory004AllAcquisitionFailuresKeepIdentityWithoutRelease() {
    var failures = new ArrayList<Throwable>();
    failures.add(new IOException("PUBLIC_ACQUIRE_IO"));
    for (var reason : StorageIoException.Reason.values())
      failures.add(new StorageIoException(reason));
    failures.addAll(unknowns());
    for (Throwable failure : failures) {
      var order = new ArrayList<String>();
      assertSame(
          failure,
          assertThrows(
              failure.getClass(),
              () ->
                  ResourceScope.acquire(
                      () -> {
                        order.add("open");
                        raise(failure);
                        return new Token();
                      },
                      value -> order.add("close"),
                      value -> {
                        order.add("body");
                        return "bad";
                      })));
      assertEquals(List.of("open"), order);
    }
  }

  @Test
  void factory005PortConstructionErrorsPrecedeAcquisition() {
    for (int index = 0; index < 3; index++) {
      var opened = new AtomicInteger();
      ResourceScope.Acquire<Token, IOException> acquire =
          () -> {
            opened.incrementAndGet();
            return new Token();
          };
      ResourceScope.Release<Token> release = value -> fail("unexpected release");
      ResourceScope.OwnedAction<Token, String> body = value -> fail("unexpected body");
      var failure = new OutOfMemoryError("PUBLIC_EXPLICIT_INJECTED_PORT_CONSTRUCTION");
      int failedPort = index;
      assertSame(
          failure,
          assertThrows(
              OutOfMemoryError.class,
              () ->
                  ResourceScope.acquire(
                      failedPort == 0 ? constructionFailure(failure) : acquire,
                      failedPort == 1 ? constructionFailure(failure) : release,
                      failedPort == 2 ? constructionFailure(failure) : body)));
      assertEquals(0, opened.get());
    }
  }

  @Test
  void factory006BodyIoReasonsAreRedactedAndExistingSuppressionIsNotExported() {
    for (var reason : StorageIoException.Reason.values()) {
      for (boolean prior : List.of(false, true)) {
        var primary = new StorageIoException(reason);
        primary.initCause(new IOException("PUBLIC_RAW_BODY_CAUSE"));
        if (prior) primary.addSuppressed(new IOException("PUBLIC_PRIOR_SUPPRESSED"));
        var h = new Harness();
        fixed(
            assertThrows(StorageIoException.class, () -> h.run(primary, null)),
            prior ? StorageIoException.Reason.UNAVAILABLE : reason);
        h.closed();
      }
    }
    var h = new Harness();
    fixed(
        assertThrows(
            StorageIoException.class, () -> h.run(new IOException("PUBLIC_BODY_IO"), null)),
        StorageIoException.Reason.UNAVAILABLE);
    h.closed();
  }

  @Test
  void factory007BodyAndCloseIoAlwaysBecomeUnavailableWithoutRawSuppression() {
    for (var reason : StorageIoException.Reason.values()) {
      var h = new Harness();
      fixed(
          assertThrows(
              StorageIoException.class,
              () -> h.run(new StorageIoException(reason), new IOException("PUBLIC_CLOSE_IO"))),
          StorageIoException.Reason.UNAVAILABLE);
      h.closed();
    }
    var h = new Harness();
    fixed(
        assertThrows(
            StorageIoException.class,
            () ->
                h.run(
                    new IOException("PUBLIC_BODY_IO"),
                    new StorageIoException(StorageIoException.Reason.MISSING))),
        StorageIoException.Reason.UNAVAILABLE);
    h.closed();
  }

  @Test
  void factory008UnknownCloseTakesPriorityOverBodyIo() {
    for (Throwable close : unknowns()) {
      var h = new Harness();
      assertSame(
          close,
          assertThrows(close.getClass(), () -> h.run(new IOException("PUBLIC_BODY_IO"), close)));
      assertEquals(0, close.getSuppressed().length);
      h.closed();
    }
  }

  @Test
  void factory009UnknownBodyKeepsIdentityAfterSuccessfulClose() {
    for (Throwable primary : unknowns()) {
      var h = new Harness();
      assertSame(primary, assertThrows(primary.getClass(), () -> h.run(primary, null)));
      assertEquals(0, primary.getSuppressed().length);
      h.closed();
    }
  }

  @Test
  void factory010UnknownCompoundAndSelfFailureHaveSanitizedOrderedSuppression() {
    for (int primaryKind = 0; primaryKind < 4; primaryKind++) {
      for (int closeKind = 0; closeKind < 6; closeKind++) {
        for (boolean prior : List.of(false, true)) {
          Throwable primary = unknowns().get(primaryKind);
          Throwable close =
              closeKind == 5
                  ? primary
                  : closeKind == 4 ? new IOException("PUBLIC_CLOSE_IO") : unknowns().get(closeKind);
          var earlier = new IOException("PUBLIC_EARLIER");
          if (prior) primary.addSuppressed(earlier);
          var h = new Harness();
          assertSame(primary, assertThrows(primary.getClass(), () -> h.run(primary, close)));
          Throwable[] suppressed = primary.getSuppressed();
          assertEquals(prior ? 2 : 1, suppressed.length);
          if (prior) assertSame(earlier, suppressed[0]);
          fixed(
              assertInstanceOf(StorageIoException.class, suppressed[suppressed.length - 1]),
              StorageIoException.Reason.UNAVAILABLE);
          assertNotSame(close, suppressed[suppressed.length - 1]);
          h.closed();
        }
      }
    }
  }

  @Test
  void factory011SuccessfulBodyCannotHideAnyCloseFailure() {
    for (var reason : StorageIoException.Reason.values()) {
      var h = new Harness();
      fixed(
          assertThrows(StorageIoException.class, () -> h.run(null, new StorageIoException(reason))),
          reason);
      h.closed();
    }
    var io = new Harness();
    fixed(
        assertThrows(
            StorageIoException.class, () -> io.run(null, new IOException("PUBLIC_CLOSE_IO"))),
        StorageIoException.Reason.UNAVAILABLE);
    io.closed();
    for (Throwable close : unknowns()) {
      var h = new Harness();
      assertSame(close, assertThrows(close.getClass(), () -> h.run(null, close)));
      assertEquals(0, close.getSuppressed().length);
      h.closed();
    }
  }

  @Test
  void factory012NestedAndParallelScopesKeepIndependentOwnership() throws Exception {
    var order = new ArrayList<String>();
    var outer = new Token();
    var inner = new Token();
    assertEquals(
        "done",
        ResourceScope.acquire(
            () -> {
              order.add("open-outer");
              return outer;
            },
            value -> {
              assertSame(outer, value);
              order.add("close-outer");
            },
            value -> {
              assertSame(outer, value);
              ResourceScope.acquire(
                  () -> {
                    order.add("open-inner");
                    return inner;
                  },
                  held -> {
                    assertSame(inner, held);
                    order.add("close-inner");
                  },
                  held -> {
                    assertSame(inner, held);
                    order.add("body-inner");
                    return "inner";
                  });
              order.add("body-outer");
              return "done";
            }));
    assertEquals(
        List.of(
            "open-outer", "open-inner", "body-inner", "close-inner", "body-outer", "close-outer"),
        order);
    try (var executor = Executors.newFixedThreadPool(2)) {
      var a = new Harness();
      var b = new Harness();
      var first = executor.submit(() -> a.run(null, null));
      var second = executor.submit(() -> b.run(null, null));
      assertEquals("result", first.get());
      assertEquals("result", second.get());
      a.closed();
      b.closed();
      assertNotSame(a.token, b.token);
    }
  }

  private static String narrowStorageType(Token token) throws StorageIoException {
    ResourceScope.Acquire<Token, StorageIoException> acquire = () -> token;
    return ResourceScope.acquire(acquire, owned -> assertSame(token, owned), owned -> "narrow");
  }

  private static <T> T constructionFailure(Error failure) {
    throw failure;
  }

  private static List<Throwable> unknowns() {
    return List.of(
        new IllegalStateException("PUBLIC_RUNTIME"),
        new NullPointerException("PUBLIC_NPE"),
        new AssertionError("PUBLIC_ERROR"),
        new OutOfMemoryError("PUBLIC_EXPLICIT_INJECTED_ERROR"));
  }

  private static void raise(@org.jspecify.annotations.Nullable Throwable failure)
      throws IOException {
    if (failure instanceof IOException io) throw io;
    if (failure instanceof RuntimeException runtime) throw runtime;
    if (failure instanceof Error error) throw error;
    assertNull(failure, "fixture supports declared IO/Runtime/Error only");
  }

  private static void fixed(StorageIoException failure, StorageIoException.Reason reason) {
    assertEquals(reason, failure.reason());
    assertEquals("transfer storage operation failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class Token {
    private boolean live;
  }

  private static final class Harness {
    private final Token token = new Token();
    private final List<String> order = new ArrayList<>();

    String run(
        @org.jspecify.annotations.Nullable Throwable primary,
        @org.jspecify.annotations.Nullable Throwable secondary)
        throws IOException {
      return ResourceScope.acquire(
          () -> {
            order.add("open");
            token.live = true;
            return token;
          },
          owned -> {
            assertSame(token, owned);
            order.add("close");
            assertTrue(token.live);
            token.live = false;
            raise(secondary);
          },
          owned -> {
            assertSame(token, owned);
            assertTrue(token.live);
            order.add("body");
            raise(primary);
            return "result";
          });
    }

    void closed() {
      assertEquals(List.of("open", "body", "close"), order);
      assertFalse(token.live);
    }
  }
}
