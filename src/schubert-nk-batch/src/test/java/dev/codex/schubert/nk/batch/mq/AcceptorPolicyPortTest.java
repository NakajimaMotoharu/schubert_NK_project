package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** OPS-ACC-PORT-001..013; SS321/342 literal JSON only; no real management/session operation. */
final class AcceptorPolicyPortTest {
  private static final String HOST_FIELD = "host";
  private static final String STARTED_FIELD = "started";
  private static final String ACCEPTORS_CALL = "acceptors";
  private static final String NAME_CORE_JSON = "\"name\":\"core\"";
  private static final String JSON_NULL = "null";
  private static final String JSON_TRUE = "true";

  private static final String PUBLIC_FAULT_TEXT = "public fixture";
  private static final String FACTORY =
      "org.apache.activemq.artemis.core.remoting.impl.netty.NettyAcceptorFactory";
  private static final String PARAMS =
      "{\"scheme\":\"tcp\",\"host\":\"127.0.0.1\",\"port\":\"61616\",\"protocols\":\"CORE\"}";
  private static final String GOOD =
      "[{\"name\":\"core\",\"factoryClassName\":\""
          + FACTORY
          + "\",\"params\":"
          + PARAMS
          + ",\"extraProps\":{}}]";
  private static final Map<String, String> EXPECTED =
      Map.of(
          "name",
          "core",
          "factoryClassName",
          FACTORY,
          "scheme",
          "tcp",
          HOST_FIELD,
          "127.0.0.1",
          "port",
          "61616",
          "protocols",
          "CORE",
          STARTED_FIELD,
          "1");

  @Test
  void exactSingletonReturnsSevenLiteralFieldsAndImmutableIndependentResults() {
    var reads = new ArrayList<String>();
    ClientSession session = unusedSession();
    var client =
        new ArtemisAcceptorReadinessClient(
            supplied -> {
              assertSame(session, supplied);
              reads.add(ACCEPTORS_CALL);
              return GOOD;
            },
            supplied -> {
              assertSame(session, supplied);
              reads.add(STARTED_FIELD);
              return true;
            });
    Map<String, String> first = client.inspect(session);
    Map<String, String> second = client.inspect(session);
    assertEquals(EXPECTED, first);
    assertEquals(EXPECTED, second);
    assertEquals(List.of(ACCEPTORS_CALL, STARTED_FIELD, ACCEPTORS_CALL, STARTED_FIELD), reads);
    assertThrows(UnsupportedOperationException.class, () -> first.put(HOST_FIELD, "other"));
    assertDoesNotThrow(() -> client.verify(session));
    assertEquals(
        List.of(
            ACCEPTORS_CALL,
            STARTED_FIELD,
            ACCEPTORS_CALL,
            STARTED_FIELD,
            ACCEPTORS_CALL,
            STARTED_FIELD),
        reads);
  }

  @Test
  void nullBoundariesRejectBeforeAnyReaderAndDefaultWiringHasNoQuery() {
    var reads = new AtomicInteger();
    ArtemisAcceptorReadinessClient.Reader reader =
        supplied -> {
          reads.incrementAndGet();
          return GOOD;
        };
    assertThrows(
        NullPointerException.class, () -> new ArtemisAcceptorReadinessClient(null, reader));
    assertThrows(
        NullPointerException.class, () -> new ArtemisAcceptorReadinessClient(reader, null));
    var client = new ArtemisAcceptorReadinessClient(reader, reader);
    assertThrows(NullPointerException.class, () -> client.inspect(null));
    assertThrows(NullPointerException.class, () -> client.verify(null));
    var defaults = new ArtemisAcceptorReadinessClient();
    assertThrows(NullPointerException.class, () -> defaults.inspect(null));
    assertThrows(NullPointerException.class, () -> defaults.verify(null));
    assertEquals(0, reads.get());
  }

  @Test
  void nonStringManagementValuesRejectBeforeStartedRead() {
    for (Object value : Arrays.asList(null, Boolean.TRUE, 7L, List.of(), Map.of())) {
      var started = new AtomicInteger();
      var client =
          new ArtemisAcceptorReadinessClient(
              ignored -> value,
              ignored -> {
                started.incrementAndGet();
                return true;
              });
      rejected(() -> client.inspect(unusedSession()));
      assertEquals(0, started.get());
    }
  }

  @Test
  void arrayCardinalityAndEveryNonObjectElementReject() {
    for (String json : List.of("[]", "[{},{}]", "[null]", "[[]]", "[7]", "[true]", "[\"data\"]")) {
      rejectsBeforeStarted(json);
    }
  }

  @Test
  void exactAcceptorFieldsNameAndFactoryRejectOneIndependentDifference() {
    for (String json :
        List.of(
            replaced(GOOD, "\"name\":\"core\",", ""),
            replaced(GOOD, NAME_CORE_JSON, "\"name\":\"CORE\""),
            replaced(GOOD, NAME_CORE_JSON, "\"name\":null"),
            replaced(GOOD, NAME_CORE_JSON, "\"name\":7"),
            replaced(GOOD, FACTORY, "public.OtherAcceptor"),
            replaced(GOOD, "\"factoryClassName\":\"" + FACTORY + "\"", "\"factoryClassName\":null"),
            replaced(GOOD, "\"extraProps\":{}", "\"extraProps\":{},\"unexpected\":0"))) {
      rejectsBeforeStarted(json);
    }
  }

  @Test
  void extraPropertiesMustBeAnEmptyObject() {
    for (String extra :
        List.of("{\"publicFlag\":true}", JSON_NULL, "[]", "1", "false", "\"data\"")) {
      rejectsBeforeStarted(replaced(GOOD, "\"extraProps\":{}", "\"extraProps\":" + extra));
    }
  }

  @Test
  void everyParameterKeyValueAndObjectTypeIsCheckedBeforeStarted() {
    for (String params :
        List.of(
            "{}",
            JSON_NULL,
            "[]",
            "7",
            JSON_TRUE,
            "\"data\"",
            replaced(PARAMS, "\"scheme\":\"tcp\",", ""),
            replaced(PARAMS, "\"scheme\":\"tcp\"", "\"scheme\":\"TCP\""),
            replaced(PARAMS, "\"host\":\"127.0.0.1\"", "\"host\":\"0.0.0.0\""),
            replaced(PARAMS, "\"port\":\"61616\"", "\"port\":\"61617\""),
            replaced(PARAMS, "\"protocols\":\"CORE\"", "\"protocols\":\"CORE,AMQP\""),
            replaced(PARAMS, "\"protocols\":\"CORE\"", "\"protocols\":\"CORE\",\"unknown\":1"))) {
      rejectsBeforeStarted(replaced(GOOD, PARAMS, params));
    }
    for (String field : List.of("scheme", HOST_FIELD, "port", "protocols")) {
      String normal =
          switch (field) {
            case "scheme" -> "tcp";
            case HOST_FIELD -> "127.0.0.1";
            case "port" -> "61616";
            default -> "CORE";
          };
      String old = "\"" + field + "\":\"" + normal + "\"";
      for (String value : List.of(JSON_NULL, "7", JSON_TRUE)) {
        rejectsBeforeStarted(replaced(GOOD, old, "\"" + field + "\":" + value));
      }
    }
  }

  @Test
  void startedMustBeTheBooleanTrueAndBothReadersAreCalledOnce() {
    for (Object state : Arrays.asList(null, false, JSON_TRUE, "1", 1L)) {
      var reads = new ArrayList<String>();
      var client =
          new ArtemisAcceptorReadinessClient(
              ignored -> {
                reads.add(ACCEPTORS_CALL);
                return GOOD;
              },
              ignored -> {
                reads.add(STARTED_FIELD);
                return state;
              });
      rejected(() -> client.inspect(unusedSession()));
      assertEquals(List.of(ACCEPTORS_CALL, STARTED_FIELD), reads);
    }
  }

  @Test
  void malformedJsonAndWrongStringTypesHaveFixedDiagnostics() {
    for (String json :
        List.of(
            "",
            "[",
            "[}",
            JSON_NULL,
            "{}",
            "7",
            JSON_TRUE,
            replaced(GOOD, NAME_CORE_JSON, "\"name\":{}"),
            replaced(
                GOOD, "\"factoryClassName\":\"" + FACTORY + "\"", "\"factoryClassName\":[]"))) {
      rejectsBeforeStarted(json);
    }
  }

  @Test
  void readerRuntimeAndErrorsKeepIdentityAndSuccessfulCallsAreNotCached() {
    for (Throwable fault :
        List.of(
            new IllegalStateException(PUBLIC_FAULT_TEXT), new AssertionError(PUBLIC_FAULT_TEXT))) {
      for (boolean first : List.of(true, false)) {
        var calls = new ArrayList<String>();
        var client =
            new ArtemisAcceptorReadinessClient(
                ignored -> {
                  calls.add(ACCEPTORS_CALL);
                  if (first) fail(fault);
                  return GOOD;
                },
                ignored -> {
                  calls.add(STARTED_FIELD);
                  fail(fault);
                  return true;
                });
        assertSame(fault, assertThrows(fault.getClass(), () -> client.inspect(unusedSession())));
        assertEquals(
            first ? List.of(ACCEPTORS_CALL) : List.of(ACCEPTORS_CALL, STARTED_FIELD), calls);
      }
    }
    var reads = new AtomicInteger();
    var client =
        new ArtemisAcceptorReadinessClient(
            ignored -> reads.incrementAndGet() == 2 ? "[]" : GOOD, ignored -> true);
    assertEquals(EXPECTED, client.inspect(unusedSession()));
    rejected(() -> client.inspect(unusedSession()));
    assertEquals(EXPECTED, client.inspect(unusedSession()));
    assertEquals(3, reads.get());
  }

  @Test
  void eachDeclaredParserExceptionIsRedactedBeforeStartedAndNeverRetried() {
    for (RuntimeException fault :
        List.of(
            new org.apache.activemq.artemis.commons.shaded.json.JsonException(PUBLIC_FAULT_TEXT),
            new ClassCastException(PUBLIC_FAULT_TEXT),
            new IllegalStateException(PUBLIC_FAULT_TEXT))) {
      var parses = new AtomicInteger();
      var started = new AtomicInteger();
      var client =
          new ArtemisAcceptorReadinessClient(
              ignored -> GOOD,
              ignored -> {
                started.incrementAndGet();
                return true;
              },
              json -> {
                assertEquals(GOOD, json);
                parses.incrementAndGet();
                throw fault;
              });
      rejected(() -> client.inspect(unusedSession()));
      assertEquals(1, parses.get());
      assertEquals(0, started.get());
    }
  }

  @Test
  void parserNullContractIsCheckedAtConstructorAndResultBoundary() {
    assertThrows(
        NullPointerException.class,
        () -> new ArtemisAcceptorReadinessClient(ignored -> GOOD, ignored -> true, null));
    var started = new AtomicInteger();
    var client =
        new ArtemisAcceptorReadinessClient(
            ignored -> GOOD,
            ignored -> {
              started.incrementAndGet();
              return true;
            },
            ignored -> null);
    var failure = assertThrows(NullPointerException.class, () -> client.inspect(unusedSession()));
    assertEquals("parsed acceptor array", failure.getMessage());
    assertEquals(0, started.get());
  }

  @Test
  void undeclaredParserRuntimeAndFatalKeepIdentityWithoutStartedRead() {
    for (Throwable fault :
        List.of(
            new IllegalArgumentException(PUBLIC_FAULT_TEXT),
            new AssertionError(PUBLIC_FAULT_TEXT))) {
      var started = new AtomicInteger();
      var client =
          new ArtemisAcceptorReadinessClient(
              ignored -> GOOD,
              ignored -> {
                started.incrementAndGet();
                return true;
              },
              json -> {
                fail(fault);
                return null;
              });
      assertSame(fault, assertThrows(fault.getClass(), () -> client.inspect(unusedSession())));
      assertEquals(0, started.get());
    }
  }

  private static String replaced(String original, String old, String replacement) {
    assertTrue(original.contains(old), "fixture replacement must visit the intended field");
    return original.replace(old, replacement);
  }

  private static void rejectsBeforeStarted(String json) {
    var started = new AtomicInteger();
    var client =
        new ArtemisAcceptorReadinessClient(
            ignored -> json,
            ignored -> {
              started.incrementAndGet();
              return true;
            });
    rejected(() -> client.inspect(unusedSession()));
    assertEquals(0, started.get());
  }

  private static void rejected(Executable action) {
    var failure = assertThrows(ArtemisManagementReadinessException.class, action);
    assertEquals("Artemis effective broker configuration is unavailable", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static void fail(Throwable fault) {
    if (fault instanceof RuntimeException runtime) throw runtime;
    throw (Error) fault;
  }

  private static ClientSession unusedSession() {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, args) -> {
              throw new AssertionError("memory readers must not operate the borrowed session");
            });
  }
}
