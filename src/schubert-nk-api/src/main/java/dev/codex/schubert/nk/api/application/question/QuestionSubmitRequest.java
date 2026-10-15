package dev.codex.schubert.nk.api.application.question;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.question.QuestionSubmitRequestData;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

/**
 * Owned decoded input, not authentication, Inbox NEW or acceptance. NK-QST-001; RD QST001/ASY001;
 * UI224/236; SS312/323 section9.6/324; PG189/SSC070; PT-QST-SUB001..008.
 */
public final class QuestionSubmitRequest implements AutoCloseable {
  private final Object stateLock = new Object();
  private final CommonHeader retainedHeader;
  private final UUID retainedOperationToken;
  private final char[] question;
  private boolean closed;

  private QuestionSubmitRequest(CommonHeader header, QuestionSubmitRequestData data) {
    this.retainedHeader = header;
    retainedOperationToken = data.operationToken();
    question = data.questionText().toCharArray();
  }

  /**
   * Validates exact Q/A wire input before database access; borrowed source remains caller-owned.
   */
  public static QuestionSubmitRequest decode(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    byte[] bytes = request.payload().copyData();
    try {
      CommonHeader header = request.header();
      if (!header.layoutId().value().equals("QSBREQ01")) {
        throw new PermanentProtocolException("unsupported question request");
      }
      header.validateAgainst(LayoutRegistry.standard().require(header.layoutId(), 1));
      var data =
          (QuestionSubmitRequestData)
              PayloadTypeCatalog.decode(
                      PayloadCodec.standard().decode(header.layoutId(), bytes, List.of(), false))
                  .data();
      return new QuestionSubmitRequest(header, data);
    } catch (PermanentProtocolException | IllegalArgumentException invalid) {
      throw new PermanentProtocolException("question submit request is invalid");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  /** Immutable trace only, never proof of current authentication. */
  public CommonHeader header() {
    synchronized (stateLock) {
      ensureOpen();
      return retainedHeader;
    }
  }

  /** Separate Inbox operation key; excluded from canonical fields. */
  public UUID operationToken() {
    synchronized (stateLock) {
      ensureOpen();
      return retainedOperationToken;
    }
  }

  /** Caller owns and clears the returned body copy. */
  public char[] copyQuestion() {
    synchronized (stateLock) {
      ensureOpen();
      return question.clone();
    }
  }

  /** Caller authenticates the actor and separately closes each returned canonical scope. */
  public CanonicalRequest canonical(AuthenticatedActor actor) {
    synchronized (stateLock) {
      ensureOpen();
      Objects.requireNonNull(actor, "actor");
      return new CanonicalRequest(
          Long.toString(actor.userId()),
          "QSBREQ01",
          "001",
          "QUESTION:NEW",
          List.of(CanonicalField.text("question", new String(question))));
    }
  }

  private void ensureOpen() {
    if (closed) throw new IllegalStateException("question submit request is closed");
  }

  /**
   * Idempotent terminal destruction of this scope only; already returned copies have other owners.
   */
  @Override
  public void close() {
    synchronized (stateLock) {
      Arrays.fill(question, '\0');
      closed = true;
    }
  }

  @Override
  public String toString() {
    return "QuestionSubmitRequest[REDACTED]";
  }
}
