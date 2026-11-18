package dev.codex.schubert.nk.api.idempotency;

import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;

/** Typed Inbox result reference. Trace: NK-MSG-002, UI 242, SS 324 §6, SS 331. */
public record InboxResultReference(
    InboxResultReferenceType type, OptionalLong numericId, Optional<UUID> uuid) {
  private static final long MAXIMUM_NUMERIC_ID = 999_999_999_999L;

  public InboxResultReference {
    Objects.requireNonNull(type, "type");
    Objects.requireNonNull(numericId, "numericId");
    Objects.requireNonNull(uuid, "uuid");
    boolean validNumericId =
        numericId.isPresent()
            && numericId.getAsLong() >= 1
            && numericId.getAsLong() <= MAXIMUM_NUMERIC_ID;
    boolean valid;
    if (type == InboxResultReferenceType.NONE) {
      valid = numericId.isEmpty() && uuid.isEmpty();
    } else if (type == InboxResultReferenceType.AUTH_SESSION) {
      valid = numericId.isEmpty() && uuid.isPresent();
    } else {
      valid = validNumericId && uuid.isEmpty();
    }
    if (!valid) {
      throw new IllegalArgumentException("result reference value does not match its type");
    }
  }

  public static InboxResultReference none() {
    return new InboxResultReference(
        InboxResultReferenceType.NONE, OptionalLong.empty(), Optional.empty());
  }

  public static InboxResultReference authSession(UUID id) {
    return new InboxResultReference(
        InboxResultReferenceType.AUTH_SESSION,
        OptionalLong.empty(),
        Optional.of(Objects.requireNonNull(id, "id")));
  }

  public static InboxResultReference numeric(InboxResultReferenceType type, long id) {
    return new InboxResultReference(type, OptionalLong.of(id), Optional.empty());
  }

  @Override
  public String toString() {
    return "InboxResultReference[<redacted>]";
  }
}
