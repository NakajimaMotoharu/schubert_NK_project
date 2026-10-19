package dev.codex.schubert.nk.protocol.transport;

import java.util.Objects;

/** Closed SS 321 Artemis address/queue and transport-limit catalog shared without JMS classes. */
public enum BrokerTopology {
  SYNC_REQUEST("nk.sync.request", 1_000_000, 5_000),
  SYNC_REPLY_WEB("nk.sync.reply.web", 1_000_000, 10_000),
  ASYNC_WORK("nk.async.work", 1_000, 0),
  WEB_LOG("nk.web.log", 10_000, 0),
  DEAD_LETTER("nk.dead.letter", 1_000_000, 0),
  EXPIRY("nk.expiry", 1_000_000, 0);

  private final String encodedAddress;
  private final String queueName;
  private final String qualifiedQueueName;
  private final int bodyLengthLimit;
  private final long ttlMillis;

  BrokerTopology(String address, int maximumBodyLength, long timeToLiveMillis) {
    this.encodedAddress = address;
    queueName = address + ".q";
    qualifiedQueueName = address + "::" + queueName;
    this.bodyLengthLimit = maximumBodyLength;
    this.ttlMillis = timeToLiveMillis;
  }

  public String address() {
    return encodedAddress;
  }

  public String queue() {
    return queueName;
  }

  public String fullyQualifiedQueue() {
    return qualifiedQueueName;
  }

  public int maximumBodyLength() {
    return bodyLengthLimit;
  }

  public long timeToLiveMillis() {
    return ttlMillis;
  }

  public boolean expirationRequired() {
    return ttlMillis > 0;
  }

  /** Resolves an exact approved physical address and rejects dynamic destinations. */
  public static BrokerTopology requireAddress(String address) {
    Objects.requireNonNull(address, "address");
    for (BrokerTopology destination : values()) {
      if (destination.encodedAddress.equals(address)) {
        return destination;
      }
    }
    throw new IllegalArgumentException("Artemis address is outside the approved topology");
  }
}
