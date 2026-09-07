package dev.codex.schubert.nk.api.messaging.guard;

import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import java.util.Objects;

/** Redacted, immutable snapshot produced after the JMS transport boundary checks. */
public record GuardedJmsMessage(byte[] body, TransportMetadata metadata) {
  public GuardedJmsMessage {
    Objects.requireNonNull(body, "body");
    Objects.requireNonNull(metadata, "metadata");
    body = body.clone();
  }

  @Override
  public byte[] body() {
    return body.clone();
  }

  @Override
  public String toString() {
    return "GuardedJmsMessage[body=<redacted>, metadata=" + metadata + "]";
  }
}
