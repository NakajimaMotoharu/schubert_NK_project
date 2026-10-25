package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.bootstrap.MaintenanceOwnerFrame;
import java.io.IOException;
import java.lang.reflect.Proxy;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.ActiveMQException;
import org.apache.activemq.artemis.api.core.client.ClientMessage;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;

/** SS321/342/343; PG-D453/BUG1523/YKT1283; independent PT-OPS-ENC001..003. */
final class ArtemisManagementEncoderBoundaryTest {
  @Test
  void encoderForwardsExactInputsAndRejectsMissingPort() {
    var message =
        (ClientMessage)
            Proxy.newProxyInstance(
                ClientMessage.class.getClassLoader(),
                new Class<?>[] {ClientMessage.class},
                (proxy, method, arguments) -> {
                  throw new AssertionError(
                      "encoder must receive, not inspect, the borrowed message");
                });
    String resource = "PT_RESOURCE";
    String operation = "PT_OPERATION";
    Object[] arguments = {"PT_SELECTOR", 7L};
    var calls = new AtomicInteger();
    ArtemisManagementReadinessClient.encodeOperation(
        message,
        resource,
        operation,
        (actualMessage, actualResource, actualOperation, actualArguments) -> {
          calls.incrementAndGet();
          assertSame(message, actualMessage);
          assertSame(resource, actualResource);
          assertSame(operation, actualOperation);
          assertSame(arguments, actualArguments);
          assertArrayEquals(new Object[] {"PT_SELECTOR", 7L}, actualArguments);
        },
        arguments);
    assertEquals(1, calls.get());
    assertThrows(
        NullPointerException.class,
        () ->
            ArtemisManagementReadinessClient.encodeOperation(
                message, resource, operation, null, arguments));
    assertEquals(1, calls.get());
  }

  @Test
  void encoderPreservesUnknownAndRedactsDeclaredFailures() {
    var fatal = new AssertionError("PT_PUBLIC_FATAL");
    for (Throwable marker :
        List.of(
            new IllegalStateException("PT_PUBLIC_UNKNOWN"),
            new NullPointerException("PT_PUBLIC_NULL"),
            fatal)) {
      var actual =
          assertThrows(
              marker.getClass(),
              () ->
                  ArtemisManagementReadinessClient.encodeOperation(
                      null,
                      "PT_RESOURCE",
                      "PT_OPERATION",
                      (message, resource, operation, arguments) -> {
                        if (marker instanceof RuntimeException runtime) throw runtime;
                        throw fatal;
                      }));
      assertSame(marker, actual);
    }
    assertFalse(Thread.currentThread().isInterrupted());
    try {
      for (Exception declared :
          List.of(
              new Exception("PT_PUBLIC_PROVIDER"),
              new InterruptedException("PT_PUBLIC_INTERRUPT"))) {
        var failure =
            assertThrows(
                ArtemisManagementReadinessException.class,
                () ->
                    ArtemisManagementReadinessClient.encodeOperation(
                        null,
                        "PT_RESOURCE",
                        "PT_OPERATION",
                        (message, resource, operation, arguments) -> {
                          throw declared;
                        }));
        assertEquals("Artemis effective broker configuration is unavailable", failure.getMessage());
        assertNull(failure.getCause());
        assertEquals(0, failure.getSuppressed().length);
        assertEquals(
            declared instanceof InterruptedException, Thread.currentThread().isInterrupted());
        Thread.interrupted();
      }
    } finally {
      Thread.interrupted();
    }
  }

  @Test
  void parentGuardIsCheckedBeforeBorrowedStartAndRemovedAfterFailure() throws Exception {
    for (boolean expireBeforeStart : List.of(false, true)) {
      var checks = new AtomicInteger();
      var starts = new AtomicInteger();
      MaintenanceOwnerFrame.Guard owner =
          () -> {
            if (checks.incrementAndGet() == 2 && expireBeforeStart)
              throw new IOException("PT_PUBLIC_DEADLINE");
            return 1_000_000_000L;
          };
      var session =
          (ClientSession)
              Proxy.newProxyInstance(
                  ClientSession.class.getClassLoader(),
                  new Class<?>[] {ClientSession.class},
                  (proxy, method, arguments) -> {
                    assertEquals("start", method.getName());
                    starts.incrementAndGet();
                    throw new ActiveMQException("PT_PUBLIC_START");
                  });
      var failure =
          assertThrows(
              ArtemisManagementReadinessException.class,
              () ->
                  ArtemisManagementReadinessClient.withParentDeadline(
                      owner, () -> ArtemisManagementReadinessClient.read(session, "name")));
      assertEquals("Artemis effective broker configuration is unavailable", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
      assertEquals(2, checks.get());
      assertEquals(expireBeforeStart ? 0 : 1, starts.get());
      assertEquals(2000L, ArtemisManagementReadinessClient.requestTimeoutMillis());
      assertFalse(Thread.currentThread().isInterrupted());
    }
  }
}
