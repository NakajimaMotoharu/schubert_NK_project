package dev.codex.schubert.nk.protocol.codec;

import dev.codex.schubert.nk.protocol.header.CommonHeader;
import java.util.Objects;

/** Header/JMS/route equality checks. Trace: NK-PRO-002, UI 231 §5, SS 322 §5/§7. */
public final class ProtocolValidator {
  public static final int PERSISTENT_DELIVERY_MODE = 2;
  private static final String PROTOCOL_VERSION = "001";

  private ProtocolValidator() {}

  public static void validateTransport(
      CommonHeader header, TransportMetadata metadata, ExpectedRoute route) {
    Objects.requireNonNull(header, "header");
    Objects.requireNonNull(metadata, "metadata");
    Objects.requireNonNull(route, "route");
    if (metadata.bodyType() != TransportBodyType.BYTES) {
      throw new PermanentProtocolException("transport body is not a BytesMessage");
    }
    if (metadata.deliveryMode() != PERSISTENT_DELIVERY_MODE) {
      throw new PermanentProtocolException("transport delivery mode is not persistent");
    }
    if (!metadata.nkProtocolVersion().equals(PROTOCOL_VERSION)) {
      throw new PermanentProtocolException("transport protocol version differs from wire header");
    }
    if (!metadata.nkMessageId().equals(header.messageId())
        || !metadata.nkLayoutId().equals(header.layoutId())
        || !metadata.correlationId().equals(header.correlationId())) {
      throw new PermanentProtocolException("transport identity differs from wire header");
    }
    if (header.messageKind() != route.messageKind()
        || header.interactionKind() != route.interactionKind()
        || !metadata.destinationAddress().equals(route.destinationAddress())) {
      throw new PermanentProtocolException("message was received on an unexpected route");
    }
    if (!metadata.replyToAddress().equals(route.requiredReplyToAddress())) {
      throw new PermanentProtocolException("reply-to address differs from its allowlisted route");
    }
    if (route.expirationRequired() != (metadata.expirationEpochMillis() > 0)) {
      throw new PermanentProtocolException("transport expiration presence violates the route");
    }
  }
}
