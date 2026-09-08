package dev.codex.schubert.nk.web.messaging;

import jakarta.jms.JMSContext;

/** Opens one caller-owned transacted JMS context without exposing its credential. */
@FunctionalInterface
public interface JmsContextFactory {
  JMSContext open();
}
