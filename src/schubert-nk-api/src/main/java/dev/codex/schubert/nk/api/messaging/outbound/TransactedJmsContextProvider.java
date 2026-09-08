package dev.codex.schubert.nk.api.messaging.outbound;

import jakarta.jms.JMSContext;

/** Credential boundary that opens one caller-owned transacted JMS context. */
@FunctionalInterface
public interface TransactedJmsContextProvider {
  JMSContext open();
}
