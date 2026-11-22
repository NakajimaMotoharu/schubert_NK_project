package dev.codex.schubert.nk.api.dispatch;

import dev.codex.schubert.nk.protocol.layout.LayoutId;

/**
 * Typed synchronous business handler in the caller's transaction.
 *
 * <p>NK-MSG-001, MQ-003/MQ-006, UI232, SS311 §6.2 and SS312 §3.3, SSC-477, PT-JMS-HCTX005.
 */
public interface LayoutHandler<Q, S> {
  LayoutId requestLayout();

  Class<Q> requestType();

  /** Handles a new request after the applicable authentication and Inbox checks. */
  S handle(RequestContext context, Q request);
}
