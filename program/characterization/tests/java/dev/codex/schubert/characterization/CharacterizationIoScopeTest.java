package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

/** PT-CHR-RAW001..007 / SS355 / PG-D-1171. No application or native resource. */
class CharacterizationIoScopeTest {
  private static final String FIXED_RESULT = "fixed";

  @Test
  void successReturnsIndependentValueAfterExactlyOneClose() throws IOException {
    List<String> calls = new ArrayList<>();
    Object resource = new Object();
    String result =
        CharacterizationIoScope.acquire(
            () -> {
              calls.add("open");
              return resource;
            },
            value -> {
              assertSame(resource, value);
              calls.add("close");
            },
            value -> {
              assertSame(resource, value);
              calls.add("work");
              return "fixed-result";
            });
    assertEquals("fixed-result", result);
    assertEquals(List.of("open", "work", "close"), calls);
  }

  @Test
  void eachWorkFailureIsRetainedAndResourceClosedOnce() {
    for (Throwable failure : failures()) {
      AtomicInteger closes = new AtomicInteger();
      Throwable actual =
          assertThrows(
              failure.getClass(),
              () ->
                  CharacterizationIoScope.acquire(
                      Object::new,
                      value -> closes.incrementAndGet(),
                      value -> {
                        raise(failure);
                        return "unused";
                      }));
      assertSame(failure, actual);
      assertEquals(1, closes.get());
      assertEquals(0, actual.getSuppressed().length);
    }
  }

  @Test
  void eachCloseFailurePreventsSuccessfulReturnWithoutSecondClose() {
    for (Throwable failure : failures()) {
      AtomicInteger closes = new AtomicInteger();
      Throwable actual =
          assertThrows(
              failure.getClass(),
              () ->
                  CharacterizationIoScope.acquire(
                      Object::new,
                      value -> {
                        closes.incrementAndGet();
                        raise(failure);
                      },
                      value -> FIXED_RESULT));
      assertSame(failure, actual);
      assertEquals(1, closes.get());
    }
  }

  @Test
  void distinctSecondaryIsSuppressedEvenWhenItIsAnError() {
    for (Throwable secondary : failures()) {
      IOException primary = new IOException("fixed-work");
      IOException actual =
          assertThrows(
              IOException.class,
              () ->
                  CharacterizationIoScope.acquire(
                      Object::new,
                      value -> raise(secondary),
                      value -> {
                        throw primary;
                      }));
      assertSame(primary, actual);
      assertArrayEquals(new Throwable[] {secondary}, actual.getSuppressed());
    }
  }

  @Test
  void identicalSecondaryIsNotSelfSuppressedOrReplaced() {
    IOException same = new IOException("shared-identity");
    IOException actual =
        assertThrows(
            IOException.class,
            () ->
                CharacterizationIoScope.acquire(
                    Object::new,
                    value -> {
                      throw same;
                    },
                    value -> {
                      throw same;
                    }));
    assertSame(same, actual);
    assertEquals(0, same.getSuppressed().length);
  }

  @Test
  void invalidCallbacksAndAcquisitionNeverCreateAnUnownedResource() {
    AtomicInteger opens = new AtomicInteger();
    CharacterizationIoScope.Open<Object> open =
        () -> {
          opens.incrementAndGet();
          return new Object();
        };
    assertThrows(
        NullPointerException.class,
        () -> CharacterizationIoScope.acquire(null, value -> {}, value -> FIXED_RESULT));
    assertThrows(
        NullPointerException.class,
        () -> CharacterizationIoScope.acquire(open, null, value -> FIXED_RESULT));
    assertThrows(
        NullPointerException.class, () -> CharacterizationIoScope.acquire(open, value -> {}, null));
    assertEquals(0, opens.get());
    AtomicInteger closes = new AtomicInteger();
    assertThrows(
        NullPointerException.class,
        () ->
            CharacterizationIoScope.acquire(
                () -> null, value -> closes.incrementAndGet(), value -> FIXED_RESULT));
    IOException failure = new IOException("open-failed");
    assertSame(
        failure,
        assertThrows(
            IOException.class,
            () ->
                CharacterizationIoScope.acquire(
                    () -> {
                      throw failure;
                    },
                    value -> closes.incrementAndGet(),
                    value -> FIXED_RESULT)));
    assertEquals(0, closes.get());
    assertThrows(
        NullPointerException.class,
        () ->
            CharacterizationIoScope.acquire(
                Object::new, value -> closes.incrementAndGet(), value -> null));
    assertEquals(1, closes.get());
  }

  @Test
  void staticToolFactoriesRejectReflectiveConstructionAndRestoreAccess()
      throws ReflectiveOperationException {
    for (Class<?> type :
        List.of(
            ArtifactComparator.class,
            CorrelatedLogEvidenceValidator.class,
            GateCli.class,
            GateContractValidator.class,
            CharacterizationIoScope.class)) {
      var constructor = type.getDeclaredConstructor();
      assertFalse(constructor.canAccess(null));
      constructor.setAccessible(true);
      try {
        InvocationTargetException actual =
            assertThrows(InvocationTargetException.class, constructor::newInstance);
        assertInstanceOf(AssertionError.class, actual.getCause());
        assertEquals(type.getSimpleName() + " is a static tool", actual.getCause().getMessage());
      } finally {
        constructor.setAccessible(false);
      }
      assertFalse(constructor.canAccess(null));
    }
  }

  private static List<Throwable> failures() {
    return List.of(
        new IOException("fixed-io"),
        new IllegalStateException("fixed-state"),
        new AssertionError("fixed-error"));
  }

  private static void raise(Throwable failure) throws IOException {
    if (failure instanceof IOException io) throw io;
    if (failure instanceof RuntimeException runtime) throw runtime;
    throw (Error) failure;
  }
}
