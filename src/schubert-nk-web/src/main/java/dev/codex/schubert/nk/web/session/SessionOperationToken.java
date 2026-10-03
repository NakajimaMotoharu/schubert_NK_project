package dev.codex.schubert.nk.web.session;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

/**
 * Purpose/UUID/time only, never the input associated with an update. NK-WEB-001;
 * FUN-001/AUT-004/MQ-021; UI226/236; SS314 §7.2.1/8; SSC-038/PG-D-094/PT-WEB-009..015.
 */
// QA049/PG-D356/TOKV201..208: completion is retention metadata, never an API success proof.
public record SessionOperationToken(
    String purpose, UUID token, Instant issuedAt, Optional<Instant> completedAt) {
  private static final Set<String> PURPOSES =
      Set.of(
          "UCRREQ01",
          "USTREQ01",
          "URLREQ01",
          "UPWREQ01",
          "ULKREQ01",
          "QSBREQ01",
          "NTCREQ01",
          "QDLREQ01");

  /** Legacy constructor creates pending only; purpose/UUID/issuedAt stay immutable. */
  public SessionOperationToken(String purpose, UUID token, Instant issuedAt) {
    this(purpose, token, issuedAt, Optional.empty());
  }

  public SessionOperationToken {
    Objects.requireNonNull(purpose, "purpose");
    Objects.requireNonNull(token, "token");
    Objects.requireNonNull(issuedAt, "issuedAt");
    Objects.requireNonNull(completedAt, "completedAt");
    if (!PURPOSES.contains(purpose))
      throw new IllegalArgumentException("session operation purpose is invalid");
    completedAt.ifPresent(
        value -> {
          if (value.isBefore(issuedAt))
            throw new IllegalArgumentException("session operation completion time is invalid");
        });
  }

  @Override
  public String toString() {
    return "SessionOperationToken[REDACTED]";
  }
}
