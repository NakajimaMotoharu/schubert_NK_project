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

  private final String address;
  private final String queue;
  private final String fullyQualifiedQueue;
  private final int maximumBodyLength;
  private final long timeToLiveMillis;

  BrokerTopology(String address, int maximumBodyLength, long timeToLiveMillis) {
    this.address = address;
    queue = address + ".q";
    fullyQualifiedQueue = address + "::" + queue;
    this.maximumBodyLength = maximumBodyLength;
    this.timeToLiveMillis = timeToLiveMillis;
  }

  public String address() {
    return address;
  }

  public String queue() {
    return queue;
  }

  public String fullyQualifiedQueue() {
    return fullyQualifiedQueue;
  }

  public int maximumBodyLength() {
    return maximumBodyLength;
  }

  public long timeToLiveMillis() {
    return timeToLiveMillis;
  }

  public boolean expirationRequired() {
    return timeToLiveMillis > 0;
  }

  /** Resolves an exact approved physical address and rejects dynamic destinations. */
  public static BrokerTopology requireAddress(String address) {
    Objects.requireNonNull(address, "address");
    for (BrokerTopology destination : values()) {
      if (destination.address.equals(address)) {
        return destination;
      }
    }
    throw new IllegalArgumentException("Artemis address is outside the approved topology");
  }
}
