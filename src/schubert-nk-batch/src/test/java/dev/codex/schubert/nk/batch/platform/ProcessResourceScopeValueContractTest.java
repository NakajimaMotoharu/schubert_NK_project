package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** NK-OPS-001/OPS009/UI251/SS343 SSC063/308; PT-OPS-SCOPEVALUE001..004/BUG-3305. */
final class ProcessResourceScopeValueContractTest {
  private static final String CONSTRUCT_REJECTED = "process resource scope is static";
  private static final String FIXED_STOP = "application stop check failed";
  private static final String BODY = "body";
  private static final String RELEASE = "release";

  @Test
  void scopeValue001RejectsAnyInstanceOfTheStaticNamespace() throws Exception {
    assertEquals(0, ProcessResourceScope.class.getDeclaredFields().length);
    var constructor = ProcessResourceScope.class.getDeclaredConstructor();
    assertEquals(Modifier.PRIVATE, constructor.getModifiers());
    boolean wasAccessible = constructor.canAccess(null);
    constructor.setAccessible(true);
    try {
      var failure = assertThrows(InvocationTargetException.class, constructor::newInstance);
      assertEquals(
          CONSTRUCT_REJECTED,
          assertInstanceOf(AssertionError.class, failure.getCause()).getMessage());
    } finally {
      constructor.setAccessible(wasAccessible);
    }
  }

  @Test
  void scopeValue002RejectsMissingInputsWithoutAcquiringOrReleasingThem() {
    var calls = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                null, item -> calls.incrementAndGet(), item -> calls.incrementAndGet()));
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                calls::incrementAndGet, null, item -> calls.incrementAndGet()));
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                calls::incrementAndGet, item -> calls.incrementAndGet(), null));
    assertThrows(
        NullPointerException.class,
        () ->
            ProcessResourceScope.acquire(
                () -> null, item -> calls.incrementAndGet(), item -> calls.incrementAndGet()));
    var failedAcquisition = new IOException("public acquire fault");
    assertSame(
        failedAcquisition,
        assertThrows(
            IOException.class,
            () ->
                ProcessResourceScope.acquire(
                    () -> {
                      throw failedAcquisition;
                    },
                    item -> calls.incrementAndGet(),
                    item -> calls.incrementAndGet())));
    assertEquals(0, calls.get());
  }

  @Test
  void scopeValue003OwnsEachAcquisitionThroughItsOwnRelease() throws Exception {
    var root = new Object();
    var child = new Object();
    var closed = new ArrayList<Object>();
    ProcessResourceScope.acquire(
        () -> root,
        closed::add,
        outer -> {
          assertSame(root, outer);
          ProcessResourceScope.acquire(
              () -> child,
              closed::add,
              inner -> {
                assertSame(child, inner);
                assertEquals(List.of(), closed);
              });
          assertEquals(List.of(child), closed);
        });
    assertEquals(List.of(child, root), closed);
    var failedClose = new IllegalStateException("public close fault");
    assertSame(
        failedClose,
        assertThrows(
            IllegalStateException.class,
            () ->
                ProcessResourceScope.acquire(
                    () -> root,
                    ignored -> {
                      throw failedClose;
                    },
                    ignored -> assertSame(root, ignored))));
    var order = new ArrayList<String>();
    ProcessResourceScope.use(() -> order.add(RELEASE), () -> order.add(BODY));
    assertEquals(List.of(BODY, RELEASE), order);
    assertSame(
        failedClose,
        assertThrows(
            IllegalStateException.class,
            () ->
                ProcessResourceScope.use(
                    () -> {
                      throw failedClose;
                    },
                    () -> assertEquals(List.of(BODY, RELEASE), order))));
  }

  @Test
  void scopeValue004BodyAndReleaseFollowTheIndependentLiteralPriorityTable() {
    // For each body kind the columns are known stop cleanup, unknown runtime cleanup and no fault.
    var table =
        List.of(
            new Priority(BodyFault.IO, List.of(Winner.FIXED_BODY, Winner.CLEANUP, Winner.BODY)),
            new Priority(
                BodyFault.INTERRUPTED,
                List.of(Winner.FIXED_BODY, Winner.CLEANUP_INTERRUPTED, Winner.BODY)),
            new Priority(BodyFault.STOP, List.of(Winner.FIXED_BODY, Winner.CLEANUP, Winner.BODY)),
            new Priority(
                BodyFault.RUNTIME, List.of(Winner.FIXED_BODY, Winner.FIXED_BODY, Winner.BODY)),
            new Priority(
                BodyFault.ERROR, List.of(Winner.FIXED_BODY, Winner.FIXED_BODY, Winner.BODY)));
    for (var row : table) {
      for (int column = 0; column < 3; column++) {
        verifyPriority(true, row.body, column, row.winners.get(column));
        verifyPriority(false, row.body, column, row.winners.get(column));
      }
    }
  }

  private static void verifyPriority(
      boolean acquired, BodyFault source, int column, Winner winner) {
    var events = new ArrayList<String>();
    var body = source.make();
    RuntimeException cleanup =
        switch (column) {
          case 0 -> new StopGateException(StopGateFailure.TIMEOUT);
          case 1 -> new IllegalStateException("public unknown cleanup");
          default -> null;
        };
    Runnable release =
        () -> {
          events.add(RELEASE);
          if (cleanup != null) throw cleanup;
        };
    ProcessResourceScope.QueryWork work =
        () -> {
          events.add(BODY);
          throwBody(body);
        };
    try {
      var actual =
          assertThrows(
              Throwable.class,
              () -> {
                if (acquired)
                  ProcessResourceScope.acquire(
                      Object::new, ignored -> release.run(), ignored -> work.run());
                else ProcessResourceScope.use(release, work);
              });
      assertEquals(List.of(BODY, RELEASE), events);
      assertEquals(winner == Winner.CLEANUP_INTERRUPTED, Thread.currentThread().isInterrupted());
      switch (winner) {
        case CLEANUP, CLEANUP_INTERRUPTED -> {
          assertSame(cleanup, actual);
          assertEquals(0, body.getSuppressed().length);
        }
        case BODY -> {
          assertSame(body, actual);
          assertEquals(0, actual.getSuppressed().length);
        }
        case FIXED_BODY -> {
          assertSame(body, actual);
          assertEquals(1, actual.getSuppressed().length);
          var fixed = assertInstanceOf(StopGateException.class, actual.getSuppressed()[0]);
          assertEquals(StopGateFailure.COMMAND_FAILURE, fixed.reason());
          assertEquals(FIXED_STOP, fixed.getMessage());
          assertNull(fixed.getCause());
        }
      }
    } finally {
      Thread.interrupted();
    }
  }

  private static void throwBody(Throwable body) throws IOException, InterruptedException {
    switch (body) {
      case IOException failure -> throw failure;
      case InterruptedException failure -> throw failure;
      case RuntimeException failure -> throw failure;
      case Error failure -> throw failure;
      default -> throw new AssertionError("invalid body fixture");
    }
  }

  private enum Winner {
    FIXED_BODY,
    CLEANUP,
    CLEANUP_INTERRUPTED,
    BODY
  }

  private record Priority(BodyFault body, List<Winner> winners) {}

  private enum BodyFault {
    IO,
    INTERRUPTED,
    STOP,
    RUNTIME,
    ERROR;

    Throwable make() {
      return switch (this) {
        case IO -> new IOException("public IO");
        case INTERRUPTED -> new InterruptedException("public interrupt");
        case STOP -> new StopGateException(StopGateFailure.NOT_STOPPED);
        case RUNTIME -> new IllegalArgumentException("public invalid");
        case ERROR -> new AssertionError("public fatal");
      };
    }
  }
}
