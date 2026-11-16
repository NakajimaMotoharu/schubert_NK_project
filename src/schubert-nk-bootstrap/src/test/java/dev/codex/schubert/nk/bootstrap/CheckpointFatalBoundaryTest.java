package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.Test;

/** SS352/354, BUG2803/YKT2359; public metadata/fake provider only, no native exporter. */
final class CheckpointFatalBoundaryTest {
  private static final String PUBLIC_MARKER = "PUBLIC_FIXED_FAILURE";
  private static final String FIXED_DIAGNOSTIC = "fixed PT native capture unavailable";

  private static FixedNativeCoverageCheckpoint.PublicAgent.Classes fixtureClasses() {
    return name ->
        name.endsWith(".RT")
            ? FixedNativeCoverageCheckpointTest.PublicRtFixture.class
            : FixedNativeCoverageCheckpointTest.PublicFixture.class;
  }

  private static IOException graph(int kind, AssertionError fatal) {
    var root = new IOException(PUBLIC_MARKER);
    switch (kind) {
      case 0 -> root.initCause(fatal);
      case 1 -> root.addSuppressed(fatal);
      default -> {
        var first = new SQLException(PUBLIC_MARKER);
        var second = new SQLException(PUBLIC_MARKER, fatal);
        first.setNextException(second);
        root.initCause(first);
      }
    }
    return root;
  }

  private static IOException nonfatalCycle() {
    var first = new IOException(PUBLIC_MARKER);
    var second = new IOException(PUBLIC_MARKER);
    first.initCause(second);
    second.initCause(first);
    return first;
  }

  private static void fixedFailure(org.junit.jupiter.api.function.Executable operation) {
    var failure = assertThrows(IOException.class, operation);
    assertEquals(FIXED_DIAGNOSTIC, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void ncheckFatal001ConstructorKeepsSameErrorFromSourceAndInvocation() {
    for (int kind = 0; kind < 3; kind++) {
      var fatal = new AssertionError(PUBLIC_MARKER);
      var wrapped = graph(kind, fatal);
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  new FixedNativeCoverageCheckpoint.PublicAgent(
                      fixtureClasses(),
                      type -> {
                        throw wrapped;
                      },
                      (method, target, arguments) -> {
                        throw new AssertionError("invocation must not start after source failure");
                      })));
      assertSame(
          fatal,
          assertThrows(
              AssertionError.class,
              () ->
                  new FixedNativeCoverageCheckpoint.PublicAgent(
                      fixtureClasses(),
                      type -> {},
                      (method, target, arguments) -> {
                        throw new InvocationTargetException(wrapped);
                      })));
    }
    fixedFailure(
        () ->
            new FixedNativeCoverageCheckpoint.PublicAgent(
                fixtureClasses(),
                type -> {
                  throw nonfatalCycle();
                },
                Method::invoke));
  }

  @Test
  void ncheckFatal002BothStringGettersKeepSameGraphErrorAndFixedNonfatal() throws Exception {
    for (String getter : List.of("getVersion", "getSessionId")) {
      for (int kind = 0; kind < 3; kind++) {
        var fatal = new AssertionError(PUBLIC_MARKER);
        var agent = failingGetter(getter, graph(kind, fatal));
        assertSame(
            fatal,
            assertThrows(
                AssertionError.class,
                () -> {
                  if (getter.equals("getVersion")) agent.version();
                  else agent.session();
                }));
      }
      var ordinary = failingGetter(getter, nonfatalCycle());
      fixedFailure(
          () -> {
            if (getter.equals("getVersion")) ordinary.version();
            else ordinary.session();
          });
    }
  }

  @Test
  void ncheckFatal003DataGetterKeepsSameGraphErrorAndNeverRequestsReset() throws Exception {
    for (int kind = 0; kind < 3; kind++) {
      var fatal = new AssertionError(PUBLIC_MARKER);
      var agent = failingGetter("getExecutionData", graph(kind, fatal));
      assertSame(fatal, assertThrows(AssertionError.class, agent::executionDataWithoutReset));
    }
    var ordinary = failingGetter("getExecutionData", nonfatalCycle());
    fixedFailure(ordinary::executionDataWithoutReset);
  }

  private static FixedNativeCoverageCheckpoint.PublicAgent failingGetter(
      String getter, IOException failure) throws IOException {
    return new FixedNativeCoverageCheckpoint.PublicAgent(
        fixtureClasses(),
        type -> {},
        (method, target, arguments) -> {
          if (method.getName().equals(getter)) {
            if (getter.equals("getExecutionData")) {
              assertEquals(1, arguments.length);
              assertEquals(Boolean.FALSE, arguments[0]);
            }
            throw new InvocationTargetException(failure);
          }
          return method.invoke(target, arguments);
        });
  }
}
