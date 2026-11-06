package dev.codex.schubert.nk.api.messaging.inbound;

/**
 * Parent-owned delivery admission, separate from blocking context cleanup. NK-MSG-001; MQ003/008;
 * UI231; SS321/SSC314; BUG2407/YKT2152; PT-JMS-STOP-GROUP001. No new resource is acquired here.
 */
interface InboundConsumerGroup extends AutoCloseable {
  /**
   * Rejects new callbacks; callbacks already admitted keep their existing ACK/rollback contract.
   */
  void stopDelivery();

  @Override
  void close();
}
