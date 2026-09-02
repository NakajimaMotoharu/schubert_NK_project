package dev.codex.schubert.nk.protocol.codec;

import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import java.util.Objects;
import java.util.Optional;

/** Receiver allowlisted route contract. Trace: NK-PRO-002, UI 231 §3～§5, SS 322 §5. */
public record ExpectedRoute(
    MessageKind messageKind,
    InteractionKind interactionKind,
    String destinationAddress,
    Optional<String> requiredReplyToAddress,
    boolean expirationRequired) {

  public ExpectedRoute {
    Objects.requireNonNull(messageKind, "messageKind");
    Objects.requireNonNull(interactionKind, "interactionKind");
    Objects.requireNonNull(destinationAddress, "destinationAddress");
    Objects.requireNonNull(requiredReplyToAddress, "requiredReplyToAddress");
    if (destinationAddress.isBlank()
        || requiredReplyToAddress.stream().anyMatch(String::isBlank)) {
      throw new IllegalArgumentException("expected route addresses must not be blank");
    }
    if ((messageKind == MessageKind.EVENT) != (interactionKind == InteractionKind.INTERNAL)) {
      throw new IllegalArgumentException("event/internal route kinds must be paired");
    }
    if ((messageKind == MessageKind.REQUEST) != requiredReplyToAddress.isPresent()) {
      throw new IllegalArgumentException("only a request route has a required reply address");
    }
    if ((messageKind == MessageKind.EVENT) == expirationRequired) {
      throw new IllegalArgumentException("events have no expiration; request/reply routes require it");
    }
  }
}
