package dev.codex.schubert.nk.batch.mq;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.batch.repository.BatchRun;
import java.lang.reflect.Proxy;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Consumer;
import org.apache.activemq.artemis.api.core.client.ClientMessage;
import org.apache.activemq.artemis.api.core.client.ClientSession;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** BUG381/YKT301; SS343 unknown identity, not a readiness retry; PT-OPS-MQUNKNOWN001..003. */
final class ArtemisUnknownBoundaryTest {

  @Test
  void mqUnknown004FatalQueryAndEveryEncoderPreserveIdentity() {
    var fatal = new AssertionError("synthetic fatal");
    var session =
        (ClientSession)
            Proxy.newProxyInstance(
                ClientSession.class.getClassLoader(),
                new Class<?>[] {ClientSession.class},
                (proxy, method, args) -> {
                  throw fatal;
                });
    var message =
        (ClientMessage)
            Proxy.newProxyInstance(
                ClientMessage.class.getClassLoader(),
                new Class<?>[] {ClientMessage.class},
                (proxy, method, args) -> {
                  throw fatal;
                });
    for (Executable action :
        List.<Executable>of(
            () -> ArtemisManagementReadinessClient.read(session, "name"),
            () -> ArtemisManagementReadinessClient.putAcceptorsOperation(message),
            () -> ArtemisManagementReadinessClient.putRolesOperation(message, "nk.sync.request"),
            () ->
                ArtemisManagementReadinessClient.putAddressSettingsOperation(
                    message, "nk.sync.request"),
            () ->
                ArtemisManagementReadinessClient.putExpiryOperation(
                    message, "countMessages", "_AMQ_ACTUAL_EXPIRY < 1")))
      assertSame(fatal, assertThrows(AssertionError.class, action));
  }

  private static ClientSession session(RuntimeException failure, AtomicInteger calls) {
    return (ClientSession)
        Proxy.newProxyInstance(
            ClientSession.class.getClassLoader(),
            new Class<?>[] {ClientSession.class},
            (proxy, method, args) -> {
              calls.incrementAndGet();
              throw failure;
            });
  }

  @Test
  void mqUnknown001EveryReaderAndExchangePreservesUnknownIdentity() {
    for (RuntimeException unknown :
        List.of(
            new IllegalStateException("synthetic unknown"),
            new NullPointerException("synthetic unknown"))) {
      var calls = new AtomicInteger();
      var session = session(unknown, calls);
      List<Executable> actions =
          List.of(
              () -> new ArtemisReadinessClient().verifyTopology(session),
              () ->
                  new ArtemisManagementReadinessClient(
                          (s, field) -> {
                            throw unknown;
                          })
                      .verifyBroker(session),
              () ->
                  new ArtemisAddressSettingsReadinessClient(
                          (s, address) -> {
                            throw unknown;
                          })
                      .verify(session),
              () ->
                  new ArtemisAcceptorReadinessClient(
                          s -> {
                            throw unknown;
                          },
                          s -> true)
                      .verify(session),
              () ->
                  new ArtemisRoleReadinessClient(
                          (s, match) -> {
                            throw unknown;
                          })
                      .verify(session),
              () ->
                  new ArtemisQueuePressureClient(
                          (s, queue, field) -> {
                            throw unknown;
                          })
                      .inspect(session),
              () ->
                  ArtemisManagementReadinessClient.read(
                      session,
                      "name",
                      (s, field) -> {
                        throw unknown;
                      }),
              () -> ArtemisManagementReadinessClient.read(session, "name"));
      for (var action : actions) assertSame(unknown, assertThrows(unknown.getClass(), action));
      assertEquals(2, calls.get()); // addressQuery and native management session.start only.
      var message =
          (ClientMessage)
              Proxy.newProxyInstance(
                  ClientMessage.class.getClassLoader(),
                  new Class<?>[] {ClientMessage.class},
                  (proxy, method, args) -> {
                    throw unknown;
                  });
      for (Executable action :
          List.<Executable>of(
              () -> ArtemisManagementReadinessClient.putAcceptorsOperation(message),
              () -> ArtemisManagementReadinessClient.putRolesOperation(message, "nk.sync.request"),
              () ->
                  ArtemisManagementReadinessClient.putAddressSettingsOperation(
                      message, "nk.sync.request"),
              () ->
                  ArtemisManagementReadinessClient.putExpiryOperation(
                      message, "countMessages", "_AMQ_ACTUAL_EXPIRY < 1")))
        assertSame(unknown, assertThrows(unknown.getClass(), action));
    }
  }

  @Test
  void mqUnknown002AllSixAssemblyStagesStopImmediatelyWithoutLaterRead() {
    var unknown = new NullPointerException("synthetic unknown");
    var session = session(unknown, new AtomicInteger());
    for (int selected = 0; selected < 6; selected++) {
      var calls = new AtomicInteger();
      var consumers = new ArrayList<Consumer<ClientSession>>();
      for (int position = 0; position < 5; position++) {
        int stage = position;
        int failing = selected;
        consumers.add(
            s -> {
              calls.incrementAndGet();
              if (stage == failing) throw unknown;
            });
      }
      var observation =
          new ArtemisStartupObservation(
              consumers.get(0),
              consumers.get(1),
              consumers.get(2),
              consumers.get(3),
              consumers.get(4),
              s -> {
                calls.incrementAndGet();
                throw unknown;
              });
      assertSame(
          unknown, assertThrows(NullPointerException.class, () -> observation.inspect(session)));
      assertEquals(selected + 1, calls.get());
    }
    var declared =
        new ArtemisStartupObservation(
            s -> {
              throw new ArtemisReadinessException();
            },
            s -> fail(),
            s -> fail(),
            s -> fail(),
            s -> fail(),
            s -> {
              fail();
              return Map.of();
            });
    assertThrows(ArtemisManagementReadinessException.class, () -> declared.inspect(session));
  }

  @Test
  void mqUnknown003ExpiryUnknownNeverRemovesAndKnownProviderRemainsDeclared() {
    var run =
        new BatchRun(
            UUID.fromString("11111111-2222-4333-8444-555555555555"),
            Instant.parse("2026-09-27T15:00:00Z"));
    var unknown = new NullPointerException("synthetic unknown");
    var session = session(unknown, new AtomicInteger());
    for (boolean known : List.of(false, true)) {
      RuntimeException supplied = known ? new ArtemisManagementReadinessException() : unknown;
      var client =
          new ArtemisExpiryPurgeClient(
              new ArtemisExpiryPurgeClient.Operations() {
                public long count(ClientSession s) {
                  throw supplied;
                }

                public long bytes(ClientSession s) {
                  fail();
                  return 0;
                }

                public long selected(ClientSession s, String selector) {
                  fail();
                  return 0;
                }

                public long remove(ClientSession s, String selector) {
                  fail();
                  return 0;
                }
              });
      var observation = new ArtemisExpiryPurgeClient.Observation(1789916400000L, 0, 0, 0, 0);
      if (known) {
        assertThrows(ArtemisExpiryPurgeException.class, () -> client.observe(session, run));
        assertThrows(
            ArtemisExpiryPurgeException.class,
            () -> client.purgeObserved(session, run, observation));
      } else {
        assertSame(
            unknown, assertThrows(NullPointerException.class, () -> client.observe(session, run)));
        assertSame(
            unknown,
            assertThrows(
                NullPointerException.class, () -> client.purgeObserved(session, run, observation)));
      }
    }
  }
}
