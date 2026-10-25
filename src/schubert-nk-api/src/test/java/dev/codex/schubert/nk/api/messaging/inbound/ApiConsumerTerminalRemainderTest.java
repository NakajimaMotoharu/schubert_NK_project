package dev.codex.schubert.nk.api.messaging.inbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.JMSConsumer;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSRuntimeException;
import jakarta.jms.MessageListener;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Clock;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Supplier;
import org.apache.activemq.artemis.jms.client.ActiveMQConnectionFactory;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-OPS-API-REM004: actual broker wire/transactions; deterministic captured provider callbacks.
 */
class ApiConsumerTerminalRemainderTest {
  @Test
  void protocolTerminalAndDirectFatalBothRemainStickyAcrossAllThreeGroups(@TempDir Path root)
      throws Exception {
    // BUG762/YKT542: never replace the normal provider return with only fault injection.
    for (int mode : List.of(0, 1, 2)) {
      boolean protocolFirst = mode == 2;
      boolean uncertain = mode == 1;
      var broker = InternalEventListenerTest.start(root.resolve("mode" + mode));
      try (var factory = new ActiveMQConnectionFactory("vm://0");
          var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
        var slots = new ArrayList<Slot>();
        var commits = new AtomicInteger();
        var rollbacks = new AtomicInteger();
        var protocols = new AtomicInteger();
        var fatals = new AtomicInteger();
        var business = new AtomicInteger();
        var questionCalls = new AtomicInteger();
        Supplier<JMSContext> source =
            () -> {
              var real = factory.createContext(JMSContext.SESSION_TRANSACTED);
              return (JMSContext)
                  Proxy.newProxyInstance(
                      JMSContext.class.getClassLoader(),
                      new Class<?>[] {JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals("commit")) commits.incrementAndGet();
                        if (m.getName().equals("rollback")) {
                          rollbacks.incrementAndGet();
                          real.rollback();
                          if (uncertain) throw new JMSRuntimeException("synthetic uncertainty");
                          return null;
                        }
                        Object value = QuestionWorkConsumersTest.invoke(real, m, a);
                        if (!m.getName().equals("createConsumer")) return value;
                        var consumer = (JMSConsumer) value;
                        var listener = new AtomicReference<MessageListener>();
                        slots.add(new Slot(consumer, listener));
                        return Proxy.newProxyInstance(
                            JMSConsumer.class.getClassLoader(),
                            new Class<?>[] {JMSConsumer.class},
                            (cp, cm, ca) -> {
                              if (cm.getName().equals("setMessageListener")) {
                                listener.set((MessageListener) ca[0]);
                                return null;
                              }
                              return QuestionWorkConsumersTest.invoke(consumer, cm, ca);
                            });
                      });
            };
        SyncRequestProcessor sync =
            ignored -> {
              business.incrementAndGet();
              throw new AssertionError("sync provider");
            };
        InternalEventProcessor log =
            ignored -> {
              business.incrementAndGet();
              throw new AssertionError("log provider");
            };
        InternalEventProcessor question =
            ignored -> {
              if (questionCalls.incrementAndGet() == 1)
                throw new IllegalStateException("retryable provider");
              business.incrementAndGet();
              throw new AssertionError("question provider");
            };
        try (var runtime =
            ApiMessagingRuntime.start(
                source,
                source,
                source,
                sync,
                log,
                question,
                Clock.systemUTC(),
                ignored -> protocols.incrementAndGet(),
                fatals::incrementAndGet)) {
          assertEquals(6, slots.size());
          for (int n : List.of(0, 4, 5)) {
            var slot = slots.get(n);
            var destination =
                n == 0
                    ? BrokerTopology.SYNC_REQUEST
                    : n == 4 ? BrokerTopology.WEB_LOG : BrokerTopology.ASYNC_WORK;
            var callback = slot.listener().get();
            assertNotNull(callback);
            if (protocolFirst) {
              // Provider-created wrong-type object is a deterministic rejection fixture; valid
              // work below is transported by the real broker. Do not infer delivery from this.
              callback.onMessage(producer.createTextMessage("invalid fixture"));
              callback.onMessage(producer.createTextMessage("second invalid fixture"));
              assertEquals(1, protocols.get());
            }
            if (n == 0) sendSync(producer);
            else
              InternalEventListenerTest.sendEvent(
                  producer,
                  destination,
                  InternalEventListenerTest.eventWire(
                      n == 4 ? "WLGEVT01" : "QWKREQ01", n == 4 ? 2080 : 64));
            var message = slot.consumer().receive(5000);
            assertNotNull(message);
            callback.onMessage(message);
            if (n == 5 && !protocolFirst) {
              assertEquals(1, questionCalls.get());
              message =
                  slot.consumer().receive(5000); // real rollback/redelivery, never new work issue.
              assertNotNull(message);
              callback.onMessage(message);
            }
            callback.onMessage(message);
            assertFalse(runtime.ready());
            assertTrue(runtime.terminalFailureObserved());
          }
          // The application cannot observe the fixture's internal real.rollback() success
          // after the provider throws. PG-D441 requires UNKNOWN to stop before the next work.
          // SS322§11 / PG-D444: committed protocol terminal stops this group's later work.
          assertEquals(protocolFirst ? 0 : uncertain ? 2 : 3, business.get());
          assertEquals(protocolFirst ? 0 : uncertain ? 1 : 2, questionCalls.get());
          assertEquals(protocolFirst ? 3 : 0, commits.get());
          assertEquals(protocolFirst ? 0 : uncertain ? 3 : 4, rollbacks.get());
          assertEquals(protocolFirst ? 1 : 0, protocols.get());
          assertEquals(protocolFirst ? 0 : 1, fatals.get());
        }
        if (uncertain || protocolFirst) {
          // Closing the stopped owner must return the uncommitted work, never ACK it.
          try (var observer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE);
              var pending =
                  observer.createConsumer(
                      new ActiveMQQueue(BrokerTopology.ASYNC_WORK.fullyQualifiedQueue()))) {
            // Second redelivery is 5s (SS321); fixture deadline includes scheduler margin.
            var returned = pending.receive(10000);
            assertNotNull(returned);
            assertArrayEquals(
                InternalEventListenerTest.eventWire("QWKREQ01", 64),
                returned.getBody(byte[].class));
          }
        }
      } finally {
        broker.stop();
      }
    }
  }

  @Test
  void ordinaryQuestionWorkCommitsExactlyOnceAndRemainsReady(@TempDir Path root) throws Exception {
    var broker = InternalEventListenerTest.start(root);
    try (var factory = new ActiveMQConnectionFactory("vm://0");
        var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
      var completed = new java.util.concurrent.CountDownLatch(1);
      var commits = new AtomicInteger();
      var business = new AtomicInteger();
      Supplier<JMSContext> source =
          () -> {
            var real = factory.createContext(JMSContext.SESSION_TRANSACTED);
            return (JMSContext)
                Proxy.newProxyInstance(
                    JMSContext.class.getClassLoader(),
                    new Class<?>[] {JMSContext.class},
                    (p, m, a) -> {
                      Object value = QuestionWorkConsumersTest.invoke(real, m, a);
                      if (m.getName().equals("commit")) {
                        commits.incrementAndGet();
                        completed.countDown();
                      }
                      if (m.getName().equals("rollback")) fail("ordinary work must not roll back");
                      return value;
                    });
          };
      try (var owner =
          QuestionWorkConsumers.start(
              source,
              new QuestionWorkListener(
                  event -> {
                    assertEquals("QWKREQ01", event.header().layoutId().value());
                    assertEquals(64, event.payload().dataLength());
                    business.incrementAndGet();
                  },
                  Clock.systemUTC()),
              ignored -> fail("no protocol failure"),
              () -> fail("no fatal"))) {
        InternalEventListenerTest.sendEvent(
            producer,
            BrokerTopology.ASYNC_WORK,
            InternalEventListenerTest.eventWire("QWKREQ01", 64));
        assertTrue(completed.await(5, java.util.concurrent.TimeUnit.SECONDS));
        assertEquals(1, commits.get());
        assertEquals(1, business.get());
        assertTrue(owner.ready());
        assertEquals(
            0,
            broker
                .getActiveMQServer()
                .locateQueue(
                    org.apache.activemq.artemis.api.core.SimpleString.of("nk.async.work.q"))
                .getMessageCount());
      }
    } finally {
      broker.stop();
    }
  }

  @Test
  void twoIndependentFatalGroupsStopOuterOwnerOnceAndNeverAckOrResume(@TempDir Path root)
      throws Exception {
    for (boolean uncertain : List.of(false, true)) {
      var broker =
          InternalEventListenerTest.start(root.resolve(uncertain ? "uncertain" : "normal"));
      try (var factory = new ActiveMQConnectionFactory("vm://0");
          var producer = factory.createContext(JMSContext.AUTO_ACKNOWLEDGE)) {
        var slots = new ArrayList<Slot>();
        var rollbacks = new AtomicInteger();
        var commits = new AtomicInteger();
        var stops = new AtomicInteger();
        var business = new AtomicInteger();
        Supplier<JMSContext> source =
            () -> {
              var real = factory.createContext(JMSContext.SESSION_TRANSACTED);
              return (JMSContext)
                  Proxy.newProxyInstance(
                      JMSContext.class.getClassLoader(),
                      new Class<?>[] {JMSContext.class},
                      (p, m, a) -> {
                        if (m.getName().equals("rollback")) {
                          rollbacks.incrementAndGet();
                          real.rollback();
                          if (uncertain)
                            throw new JMSRuntimeException("synthetic rollback uncertainty");
                          return null;
                        }
                        if (m.getName().equals("commit")) commits.incrementAndGet();
                        Object value = QuestionWorkConsumersTest.invoke(real, m, a);
                        if (!m.getName().equals("createConsumer")) return value;
                        var consumer = (JMSConsumer) value;
                        var listener = new AtomicReference<MessageListener>();
                        slots.add(new Slot(consumer, listener));
                        return Proxy.newProxyInstance(
                            JMSConsumer.class.getClassLoader(),
                            new Class<?>[] {JMSConsumer.class},
                            (cp, cm, ca) -> {
                              if (cm.getName().equals("setMessageListener")) {
                                listener.set((MessageListener) ca[0]);
                                return null;
                              }
                              return QuestionWorkConsumersTest.invoke(consumer, cm, ca);
                            });
                      });
            };
        InternalEventProcessor fatal =
            ignored -> {
              business.incrementAndGet();
              throw new AssertionError("synthetic provider fatal");
            };
        try (var runtime =
            ApiMessagingRuntime.start(
                source,
                source,
                source,
                ignored -> new byte[0],
                fatal,
                fatal,
                Clock.systemUTC(),
                ignored -> fail("no protocol failure"),
                stops::incrementAndGet)) {
          assertEquals(6, slots.size());
          assertTrue(runtime.ready());
          for (int n : List.of(4, 5)) {
            var destination = n == 4 ? BrokerTopology.WEB_LOG : BrokerTopology.ASYNC_WORK;
            InternalEventListenerTest.sendEvent(
                producer,
                destination,
                InternalEventListenerTest.eventWire(
                    n == 4 ? "WLGEVT01" : "QWKREQ01", n == 4 ? 2080 : 64));
            var slot = slots.get(n);
            var message = slot.consumer().receive(5000);
            assertNotNull(message);
            var listener = slot.listener().get();
            assertNotNull(listener);
            listener.onMessage(message);
            listener.onMessage(
                message); // halted callbacks must not enter the business/guard again.
            assertFalse(runtime.ready());
            assertTrue(runtime.terminalFailureObserved());
            assertEquals(1, stops.get());
          }
          assertEquals(2, business.get());
          assertEquals(2, rollbacks.get());
          assertEquals(0, commits.get());
        }
        for (String queue : List.of("nk.sync.request.q", "nk.web.log.q", "nk.async.work.q"))
          assertEquals(
              0,
              broker
                  .getActiveMQServer()
                  .locateQueue(org.apache.activemq.artemis.api.core.SimpleString.of(queue))
                  .getConsumerCount());
      } finally {
        broker.stop();
      }
    }
  }

  private static void sendSync(JMSContext producer) throws Exception {
    byte[] wire = new byte[256];
    Arrays.fill(wire, (byte) ' ');
    String id = "00000000-0000-0000-0000-000000000001";
    ascii(wire, 0, "SCHBNK01");
    ascii(wire, 8, "001");
    ascii(wire, 11, "LOGREQ01");
    ascii(wire, 19, "001");
    ascii(wire, 22, "QS");
    ascii(wire, 24, id);
    ascii(wire, 60, id);
    ascii(wire, 96, "20260903120000000");
    ascii(wire, 113, "a".repeat(64));
    ascii(wire, 177, "0256");
    ascii(wire, 181, "000000000000000000000000256");
    var message = producer.createBytesMessage();
    message.writeBytes(wire);
    message.setJMSCorrelationID(id);
    message.setJMSReplyTo(new ActiveMQQueue("nk.sync.reply.web"));
    message.setStringProperty("NKMessageID", id);
    message.setStringProperty("NKLayoutID", "LOGREQ01");
    message.setStringProperty("NKProtocolVersion", "001");
    producer
        .createProducer()
        .setDeliveryMode(jakarta.jms.DeliveryMode.PERSISTENT)
        .setTimeToLive(5000)
        .send(new ActiveMQQueue("nk.sync.request::nk.sync.request.q"), message);
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }

  private record Slot(JMSConsumer consumer, AtomicReference<MessageListener> listener) {}
}
