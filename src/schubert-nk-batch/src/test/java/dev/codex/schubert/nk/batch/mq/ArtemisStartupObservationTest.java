package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.lang.reflect.Proxy;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import java.util.function.Function;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;

/** PT-OPS-MQ-029..031: SS321 six live observations remain borrowed and non-authorizing. */
final class ArtemisStartupObservationTest {
  private static final String[] ADDRESS = {
    "nk.sync.request",
    "nk.sync.reply.web",
    "nk.async.work",
    "nk.web.log",
    "nk.dead.letter",
    "nk.expiry"
  };

  @Test
  void opsMq029OrderedReadOnlyObservation() {
    var calls = new ArrayList<Integer>();
    ClientSession session = unusedSession();
    var values = pressures();
    values.put("nk.dead.letter", ArtemisQueuePressureClient.Pressure.ALERT);
    var observed = assembly(calls, -1, ignored -> values).inspect(session);
    assertEquals(List.of(0, 1, 2, 3, 4, 5), calls);
    assertEquals(values, observed);
    values.clear();
    assertEquals(6, observed.size());
    assertThrows(UnsupportedOperationException.class, () -> observed.clear());
    assertEquals(
        "unexpected borrowed session call: addressQuery",
        assertThrows(AssertionError.class, () -> new ArtemisStartupObservation().inspect(session))
            .getMessage());
  }

  @Test
  void opsMq030FailClosedAndNoLaterChecks() {
    ClientSession session = unusedSession();
    assertThrows(
        NullPointerException.class,
        () -> assembly(new ArrayList<>(), -1, ignored -> pressures()).inspect(null));
    assertThrows(
        ArtemisManagementReadinessException.class,
        () -> assembly(new ArrayList<>(), -1, ignored -> pressures()).inspectEvidence(session));
    assertThrows(
        NullPointerException.class, () -> new ArtemisStartupObservation().inspectEvidence(null));
    for (int failedStep = 0; failedStep < 6; failedStep++) {
      int selectedStep = failedStep;
      var calls = new ArrayList<Integer>();
      var failure =
          assertThrows(
              IllegalArgumentException.class,
              () -> assembly(calls, selectedStep, ignored -> pressures()).inspect(session));
      assertEquals("synthetic private broker reply", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(failedStep + 1, calls.size());
      for (int index = 0; index <= failedStep; index++) assertEquals(index, calls.get(index));
    }
  }

  @Test
  void opsMq031MalformedPressureAndFatalContracts() {
    ClientSession session = unusedSession();
    var calls = new ArrayList<Integer>();
    for (Map<String, ArtemisQueuePressureClient.Pressure> invalid :
        List.of(
            Map.<String, ArtemisQueuePressureClient.Pressure>of(),
            missing(),
            excess(),
            nullElement())) {
      assertThrows(
          ArtemisManagementReadinessException.class,
          () -> assembly(calls, -1, ignored -> invalid).inspect(session));
    }
    assertThrows(
        ArtemisManagementReadinessException.class,
        () -> assembly(calls, -1, ignored -> null).inspect(session));
    AssertionError fatal = new AssertionError("synthetic fatal broker check");
    var fatalCalls = new AtomicInteger();
    Consumer<ClientSession> fatalTopology =
        ignored -> {
          fatalCalls.incrementAndGet();
          throw fatal;
        };
    AssertionError observed =
        assertThrows(
            AssertionError.class,
            () ->
                new ArtemisStartupObservation(
                        fatalTopology,
                        ignored -> fatalCalls.incrementAndGet(),
                        ignored -> fatalCalls.incrementAndGet(),
                        ignored -> fatalCalls.incrementAndGet(),
                        ignored -> fatalCalls.incrementAndGet(),
                        ignored -> pressures())
                    .inspect(session));
    assertSame(fatal, observed);
    assertEquals(1, fatalCalls.get());
    Consumer<ClientSession> valid = ignored -> {};
    Function<ClientSession, Map<String, ArtemisQueuePressureClient.Pressure>> pressure =
        ignored -> pressures();
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisStartupObservation(null, valid, valid, valid, valid, pressure));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisStartupObservation(valid, null, valid, valid, valid, pressure));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisStartupObservation(valid, valid, null, valid, valid, pressure));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisStartupObservation(valid, valid, valid, null, valid, pressure));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisStartupObservation(valid, valid, valid, valid, null, pressure));
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisStartupObservation(valid, valid, valid, valid, valid, null));
  }

  @Test
  void opsMqObsGraph001PreservesFatalFromIsolatedTopologyPort() {
    var fatal = new AssertionError("synthetic topology observation marker");
    var failure = topologyFailure(fatal);
    var calls = new AtomicInteger();
    Consumer<ClientSession> later = ignored -> calls.incrementAndGet();
    var observer =
        new ArtemisStartupObservation(
            ignored -> {
              throw failure;
            },
            later,
            later,
            later,
            later,
            ignored -> {
              calls.incrementAndGet();
              return pressures();
            });

    assertSame(fatal, assertThrows(AssertionError.class, () -> observer.inspect(unusedSession())));
    assertEquals(0, calls.get());
  }

  @Test
  void opsMqObsGraph002PreservesFatalFromBorrowedDetailedObservation() {
    var fatal = new AssertionError("synthetic detailed observation marker");
    var failure = topologyFailure(fatal);
    var calls = new AtomicInteger();
    var local =
        (ClientSession)
            Proxy.newProxyInstance(
                ClientSession.class.getClassLoader(),
                new Class<?>[] {ClientSession.class},
                (ignored, method, arguments) -> {
                  assertEquals("addressQuery", method.getName());
                  calls.incrementAndGet();
                  throw failure;
                });

    var observer = new ArtemisStartupObservation();
    assertSame(fatal, assertThrows(AssertionError.class, () -> observer.inspectEvidence(local)));
    assertEquals(1, calls.get());
  }

  private static ArtemisReadinessException topologyFailure(AssertionError fatal) {
    var first = new SQLException("synthetic first observation failure");
    first.setNextException(new SQLException("synthetic next observation failure", fatal));
    var declared = new ArtemisReadinessException();
    declared.addSuppressed(first);
    return declared;
  }

  private static ArtemisStartupObservation assembly(
      List<Integer> calls,
      int failing,
      Function<ClientSession, Map<String, ArtemisQueuePressureClient.Pressure>> pressure) {
    return new ArtemisStartupObservation(
        step(calls, failing, 0),
        step(calls, failing, 1),
        step(calls, failing, 2),
        step(calls, failing, 3),
        step(calls, failing, 4),
        ignored -> {
          calls.add(5);
          if (failing == 5) throw new IllegalArgumentException("synthetic private broker reply");
          return pressure.apply(ignored);
        });
  }

  private static Consumer<ClientSession> step(List<Integer> calls, int failing, int index) {
    return ignored -> {
      calls.add(index);
      if (failing == index) throw new IllegalArgumentException("synthetic private broker reply");
    };
  }

  private static HashMap<String, ArtemisQueuePressureClient.Pressure> pressures() {
    var values = new HashMap<String, ArtemisQueuePressureClient.Pressure>();
    for (String address : ADDRESS) values.put(address, ArtemisQueuePressureClient.Pressure.NORMAL);
    return values;
  }

  private static Map<String, ArtemisQueuePressureClient.Pressure> missing() {
    var values = pressures();
    values.remove("nk.expiry");
    return values;
  }

  private static Map<String, ArtemisQueuePressureClient.Pressure> excess() {
    var values = pressures();
    values.put("nk.unknown", ArtemisQueuePressureClient.Pressure.NORMAL);
    return values;
  }

  private static Map<String, ArtemisQueuePressureClient.Pressure> nullElement() {
    var values = pressures();
    values.put("nk.expiry", null);
    return values;
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (ignored, method, arguments) -> {
              throw new AssertionError("unexpected borrowed session call: " + method.getName());
            });
  }
}
