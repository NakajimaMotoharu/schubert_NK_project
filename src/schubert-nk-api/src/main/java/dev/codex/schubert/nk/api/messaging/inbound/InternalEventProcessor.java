package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;

/**
 * Business port for one validated internal event; it has no access to JMS.
 *
 * <p>Trace: NK-MSG-001; RD MQ-006/MQ-007; UI 213/231; SS 311/312; PT-JMS-005/007.
 */
@FunctionalInterface
public interface InternalEventProcessor {
  /** Processes one event under its application transaction and idempotency policy. */
  void process(WireMessage<FixedPayload> event);
}
