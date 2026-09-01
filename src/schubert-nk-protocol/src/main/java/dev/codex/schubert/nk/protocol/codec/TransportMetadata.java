package dev.codex.schubert.nk.protocol.codec;

import dev.codex.schubert.nk.protocol.layout.LayoutId;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/** JMS property snapshot without JMS classes. Trace: NK-PRO-002, UI 231 §5, SS 322 §2. */
public record TransportMetadata(
    TransportBodyType bodyType,
    String transportMessageId,
    UUID correlationId,
    Optional<String> replyToAddress,
    long expirationEpochMillis,
    int deliveryMode,
    int deliveryCount,
    UUID nkMessageId,
    LayoutId nkLayoutId,
    String nkProtocolVersion,
    String destinationAddress) {

  public TransportMetadata {
    Objects.requireNonNull(bodyType, "bodyType");
    Objects.requireNonNull(transportMessageId, "transportMessageId");
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(replyToAddress, "replyToAddress");
    Objects.requireNonNull(nkMessageId, "nkMessageId");
    Objects.requireNonNull(nkLayoutId, "nkLayoutId");
    Objects.requireNonNull(nkProtocolVersion, "nkProtocolVersion");
    Objects.requireNonNull(destinationAddress, "destinationAddress");
    if (transportMessageId.isBlank()
        || nkProtocolVersion.isBlank()
        || destinationAddress.isBlank()
        || replyToAddress.stream().anyMatch(String::isBlank)) {
      throw new IllegalArgumentException("required transport metadata must not be blank");
    }
    if (expirationEpochMillis < 0 || deliveryCount < 1) {
      throw new IllegalArgumentException("transport expiration/count is outside its range");
    }
  }
}
