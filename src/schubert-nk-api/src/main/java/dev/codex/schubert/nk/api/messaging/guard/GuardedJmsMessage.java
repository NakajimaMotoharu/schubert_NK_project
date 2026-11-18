package dev.codex.schubert.nk.api.messaging.guard;

import dev.codex.schubert.nk.protocol.codec.TransportMetadata;
import java.util.Objects;

/** Redacted, immutable snapshot after transport checks. NK-MSG-001; SS321/351; SSC-467. */
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
    return "GuardedJmsMessage[<redacted>]";
  }
}
