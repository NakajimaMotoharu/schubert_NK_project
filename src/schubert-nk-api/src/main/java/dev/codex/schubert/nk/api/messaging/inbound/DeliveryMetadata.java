package dev.codex.schubert.nk.api.messaging.inbound;

import java.time.Instant;
import java.util.Objects;

/** Actual guarded delivery, not a inferred first attempt. SS312/SSC153; PT-JMS-EVENT-DELIVERY. */
public record DeliveryMetadata(int deliveryCount, String transportMessageId, Instant receivedAt) {
  public DeliveryMetadata {
    Objects.requireNonNull(transportMessageId, "transportMessageId");
    Objects.requireNonNull(receivedAt, "receivedAt");
    if (deliveryCount < 1
        || transportMessageId.isBlank()
        || transportMessageId.length() > 128
        || transportMessageId.chars().anyMatch(c -> c < 0x20 || c > 0x7e)) {
      throw new IllegalArgumentException("delivery metadata is outside its bounded contract");
    }
  }

  @Override
  public String toString() {
    return "DeliveryMetadata[metadata=<redacted>]";
  }
}
