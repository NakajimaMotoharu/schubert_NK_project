package dev.codex.schubert.nk.api.messaging.outbound;

import java.util.Arrays;

/** Closed mapping to the two SS 331 physical outbox addresses. Trace: SSC-006. */
public enum OutboxDestination {
  ASYNC_WORK("nk.async.work"),
  DLQ("nk.dead.letter");

  private final String physicalAddress;

  OutboxDestination(String address) {
    this.physicalAddress = address;
  }

  public String address() {
    return physicalAddress;
  }

  public static OutboxDestination fromAddress(String address) {
    if (address == null) {
      throw new NullPointerException("address");
    }
    return Arrays.stream(values())
        .filter(destination -> destination.physicalAddress.equals(address))
        .findFirst()
        .orElseThrow(() -> new IllegalArgumentException("outbox destination is not allowed"));
  }
}
