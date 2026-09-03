package dev.codex.schubert.nk.api.messaging.inbound;

import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.WireMessage;

/**
 * Business-dispatch port that has no access to JMS and returns one complete encoded reply.
 *
 * <p>Trace: NK-MSG-001; RD MQ-003/MQ-006; UI 212; SS 311/312; PT-JMS-005/007.
 */
@FunctionalInterface
public interface SyncRequestProcessor {
  /** Processes one validated synchronous request under the API application transaction policy. */
  byte[] process(WireMessage<FixedPayload> request);
}
