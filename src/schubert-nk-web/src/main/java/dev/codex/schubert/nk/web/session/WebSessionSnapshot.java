package dev.codex.schubert.nk.web.session;

import java.security.NoSuchAlgorithmException;
import java.util.Objects;

/**
 * Immutable request snapshot, never a generic serializable principal or authorization grant.
 * NK-WEB-001; FUN-001/AUT-001..004; UI226; SS314 §7.2.4/331/352; SSC-041/PG-D-098/PT-WEB-036..043.
 * Nonnull values with cookie/hash identity correspondence.
 */
public final class WebSessionSnapshot {
  private final WebSessionId retainedSessionId;
  private final WebSessionRow retainedRow;
  private final SessionAttributes retainedAttributes;

  public WebSessionSnapshot(WebSessionId sessionId, WebSessionRow row, SessionAttributes attributes)
      throws NoSuchAlgorithmException {
    this.retainedSessionId = Objects.requireNonNull(sessionId, "sessionId");
    this.retainedRow = Objects.requireNonNull(row, "row");
    this.retainedAttributes = Objects.requireNonNull(attributes, "attributes");
    if (!sessionId.lookupHash().equals(row.identity().sessionIdHash()))
      throw new IllegalArgumentException("session snapshot identity is inconsistent");
  }

  public WebSessionId sessionId() {
    return retainedSessionId;
  }

  public WebSessionRow row() {
    return retainedRow;
  }

  public SessionAttributes attributes() {
    return retainedAttributes;
  }

  @Override
  public String toString() {
    return "WebSessionSnapshot[REDACTED]";
  }
}
