package dev.codex.schubert.nk.api.messaging.outbound;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.transport.BrokerTopology;
import jakarta.jms.BytesMessage;
import jakarta.jms.DeliveryMode;
import jakarta.jms.JMSContext;
import jakarta.jms.JMSException;
import java.util.ArrayDeque;
import java.util.Arrays;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import org.apache.activemq.artemis.api.core.ActiveMQDuplicateIdException;
import org.apache.activemq.artemis.jms.client.ActiveMQQueue;
import org.jspecify.annotations.Nullable;

/**
 * Validates and commits one persistent outbox message in a local JMS transaction. Trace:
 * NK-MSG-002; RD MQ-006/MQ-008; UI 242; SS 323/324 section 8; PT-IDEM-010/011.
 */
public final class OutboxJmsSender {
  public void send(TransactedJmsContextProvider contextProvider, OutboxEntry entry)
      throws OutboxSendException {
    Objects.requireNonNull(contextProvider, "contextProvider");
    Objects.requireNonNull(entry, "entry");
    validateWireIdentity(entry);
    final JMSContext context;
    try {
      context = Objects.requireNonNull(contextProvider.open(), "JMS context");
    } catch (RuntimeException failure) {
      throw new OutboxSendException("outbox JMS context lifecycle failed", failure);
    }
    @Nullable Throwable primary = null;
    try {
      if (context.getSessionMode() != JMSContext.SESSION_TRANSACTED) {
        throw new OutboxSendException("outbox JMS context is not transacted");
      }
      try {
        stage(context, entry);
      } catch (JMSException | RuntimeException exception) {
        rollback(context, exception);
        throw new OutboxSendException("outbox JMS send was not confirmed", exception);
      }
      try {
        context.commit();
      } catch (RuntimeException exception) {
        rollback(context, exception);
        if (!isDuplicateConfirmation(exception)) {
          throw new OutboxSendException("outbox JMS commit was not confirmed", exception);
        }
      }
    } catch (OutboxSendException exception) {
      primary = exception;
      throw exception;
    } catch (RuntimeException exception) {
      var wrapped = new OutboxSendException("outbox JMS context lifecycle failed", exception);
      primary = wrapped;
      throw wrapped;
    } catch (Error exception) {
      primary = exception;
      throw exception;
    } finally {
      closeAfterFailure(context, primary);
    }
  }

  private static void closeAfterFailure(JMSContext context, @Nullable Throwable primary)
      throws OutboxSendException {
    try {
      context.close();
    } catch (RuntimeException | Error closing) {
      if (primary == null) {
        if (closing instanceof Error fatal) throw fatal;
        throw new OutboxSendException("outbox JMS context lifecycle failed", closing);
      }
      // SSC320/PT-IDEM-FAIL320001: fatal cleanup cannot become ordinary send retry.
      if (closing instanceof Error fatal && !(primary instanceof Error)) {
        fatal.addSuppressed(primary); // Fatal/nonfatal objects cannot be the same Throwable.
        throw fatal;
      }
      if (closing != primary
          && !(primary instanceof OutboxSendException typed && closing == typed.getCause())) {
        primary.addSuppressed(closing);
      }
    }
  }

  private static void stage(JMSContext context, OutboxEntry entry) throws JMSException {
    BytesMessage message = context.createBytesMessage();
    message.writeBytes(entry.body());
    message.setJMSCorrelationID(entry.correlationId().toString());
    message.setStringProperty("NKMessageID", wireMessageId(entry).toString());
    message.setStringProperty("NKLayoutID", entry.layoutId());
    message.setStringProperty("NKProtocolVersion", entry.layoutVersion());
    message.setStringProperty("_AMQ_DUPL_ID", entry.messageId().toString());
    if (entry.dlqMetadata().isPresent()) {
      OutboxDlqMetadata metadata = entry.dlqMetadata().orElseThrow();
      message.setStringProperty("_AMQ_ORIG_ADDRESS", BrokerTopology.ASYNC_WORK.address());
      message.setStringProperty("_AMQ_ORIG_QUEUE", BrokerTopology.ASYNC_WORK.queue());
      message.setStringProperty("NKOriginalTransportID", metadata.originalTransportId());
      message.setStringProperty("NKCorrelationID", entry.correlationId().toString());
      message.setIntProperty("NKDeliveryCount", metadata.deliveryCount());
      message.setStringProperty("NKErrorCode", metadata.errorCode());
      message.setStringProperty("NKDetectedBy", "API_WORK");
      message.setStringProperty("NKDetectedAt", metadata.detectedAt().toString());
    }
    BrokerTopology target = target(entry.destination());
    context
        .createProducer()
        .setDeliveryMode(DeliveryMode.PERSISTENT)
        .setTimeToLive(target.timeToLiveMillis())
        .send(new ActiveMQQueue(target.fullyQualifiedQueue()), message);
  }

  static void validateWireIdentity(OutboxEntry entry) {
    byte[] body = entry.body();
    final CommonHeader header;
    try {
      header = HeaderCodec.standard().peek(body);
    } catch (RuntimeException exception) {
      throw new OutboxIntegrityException(
          "outbox wire body failed fixed-width validation", exception);
    }
    BrokerTopology target = target(entry.destination());
    if (!header.messageId().equals(wireMessageId(entry))
        || !header.correlationId().equals(entry.correlationId())
        || !header.layoutId().value().equals(entry.layoutId())
        || !String.format(Locale.ROOT, "%03d", header.layoutVersion()).equals(entry.layoutVersion())
        || header.totalLength() != body.length
        || body.length > target.maximumBodyLength()
        || !entry.layoutId().equals("QWKREQ01")) {
      throw new OutboxIntegrityException("outbox row and wire identity disagree");
    }
    // BUG-010: QWKREQ01 has one 64-byte data area and no records (SS 323).
    // Header identity alone does not establish required fields, numeric IDs or receipt syntax.
    try {
      // PayloadTypeCatalog also applies the layout's intrinsic semantic constraints.
      PayloadTypeCatalog.decode(
          PayloadCodec.standard()
              .decode(
                  header.layoutId(),
                  Arrays.copyOfRange(body, LayoutDefinition.HEADER_LENGTH, body.length),
                  List.of(),
                  false));
    } catch (RuntimeException exception) {
      throw new OutboxIntegrityException("outbox payload failed fixed-width validation", exception);
    }
  }

  private static java.util.UUID wireMessageId(OutboxEntry entry) {
    return entry.dlqMetadata().map(OutboxDlqMetadata::originalMessageId).orElse(entry.messageId());
  }

  private static BrokerTopology target(OutboxDestination destination) {
    return switch (destination) {
      case ASYNC_WORK -> BrokerTopology.ASYNC_WORK;
      case DLQ -> BrokerTopology.DEAD_LETTER;
    };
  }

  private static void rollback(JMSContext context, Throwable failure) {
    try {
      context.rollback();
    } catch (RuntimeException rollbackFailure) {
      if (rollbackFailure != failure) {
        failure.addSuppressed(rollbackFailure);
      }
    }
  }

  static boolean isDuplicateConfirmation(Throwable failure) {
    Objects.requireNonNull(failure, "failure");
    // BUG1299/YKT1065: provider cause/linked edges form a graph, not a single chain.
    // Suppressed rollback/close failures are not evidence that commit was confirmed.
    ArrayDeque<Throwable> pending = new ArrayDeque<>();
    Set<Throwable> seen = Collections.newSetFromMap(new IdentityHashMap<>());
    pending.add(failure);
    while (!pending.isEmpty()) {
      Throwable candidate = pending.remove();
      if (!seen.add(candidate)) {
        continue;
      }
      if (candidate instanceof ActiveMQDuplicateIdException) {
        return true;
      }
      Throwable cause = candidate.getCause();
      if (cause != null) {
        pending.add(cause);
      }
      if (candidate instanceof JMSException jms && jms.getLinkedException() != null) {
        pending.add(jms.getLinkedException());
      }
    }
    return false;
  }
}
