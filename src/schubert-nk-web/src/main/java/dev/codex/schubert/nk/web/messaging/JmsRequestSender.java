package dev.codex.schubert.nk.web.messaging;

import jakarta.jms.JMSException;
import java.util.UUID;

/** Transacted persistent-send boundary implemented by the JMS adapter. */
@FunctionalInterface
public interface JmsRequestSender {
  void send(UUID correlationId, byte[] encodedBody) throws JMSException;
}
