package dev.codex.schubert.nk.api.security;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.idempotency.InboxCompletion;
import dev.codex.schubert.nk.api.idempotency.InboxCompletionState;
import dev.codex.schubert.nk.api.idempotency.InboxResultReference;
import dev.codex.schubert.nk.api.idempotency.InboxResultReferenceType;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodec;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotException;
import dev.codex.schubert.nk.api.idempotency.ResponseSnapshotIdentity;
import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.auth.LoginResponseData;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

/**
 * Immutable Login result storage/reconstruction, never an authenticated principal or session touch.
 * NK-AUT-001; AUT-001/MQ-006..010; UI232/234/241; SS324 §6.1/331/314; SSC-013;
 * PT-AUT-REPLAY-001..005. The caller owns Inbox/HMAC validation and the entire DB transaction.
 */
public final class LoginReplayService {
  private static final LayoutId LOGIN = new LayoutId("LGNRSP01");
  private static final String READ_SESSION =
      "select user_id,created_message_id,context_hash,context_ciphertext,key_version,issued_at"
          + " from schubert.auth_sessions where id=?";
  private final ResponseSnapshotCodec snapshots;
  private final AuthContextCodec contexts;
  private final ContextHash hashes;

  public LoginReplayService(
      ResponseSnapshotCodec snapshots, AuthContextCodec contexts, ContextHash hashes) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
    this.contexts = Objects.requireNonNull(contexts, "contexts");
    this.hashes = Objects.requireNonNull(hashes, "hashes");
  }

  /** Non-persisted PROCESSING/temporary response; UI222/234, PT-AUT-INBOX-003/006. */
  public byte[] temporaryFailure(UUID requestId, UUID responseId, Instant sentAt) {
    Objects.requireNonNull(requestId, "requestId");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(sentAt, "sentAt");
    return wire(
        new AuthenticationResponseMapper().temporaryLoginFailure(),
        ResultCode.TEMPORARY_FAILURE,
        requestId,
        responseId,
        sentAt);
  }

  /** Captures only deterministic Login results. Caller stores this with session/counters/audit. */
  public InboxCompletion capture(
      LoginResult result, UUID requestId, UUID responseId, Instant completedAt) {
    Objects.requireNonNull(result, "result");
    Objects.requireNonNull(requestId, "requestId");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(completedAt, "completedAt");
    byte[] body =
        wire(
            new AuthenticationResponseMapper().login(result),
            result.resultCode(),
            requestId,
            responseId,
            completedAt);
    try {
      InboxResultReference reference;
      InboxCompletionState state;
      if (result instanceof LoginResult.Success success) {
        reference = InboxResultReference.authSession(success.issued().identity().sessionId());
        state = InboxCompletionState.COMPLETED;
      } else {
        reference = InboxResultReference.none();
        state = InboxCompletionState.ERROR;
      }
      return new InboxCompletion(
          state,
          reference,
          "LGNRSP01",
          "001",
          Optional.of(snapshots.encrypt(identity(requestId), body)),
          completedAt.truncatedTo(ChronoUnit.MICROS));
    } catch (ResponseSnapshotException | IllegalStateException failure) {
      throw new AuthenticationInfrastructureException();
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  /**
   * Validates the saved result and emits a fresh header. No database mutations; caller must
   * rollback on failure. Even a subsequently revoked context is not resurrected by presenting its
   * old result.
   */
  public byte[] restore(
      Connection connection,
      InboxCompletion completion,
      UUID requestId,
      UUID responseId,
      Instant sentAt,
      boolean replay) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(completion, "completion");
    Objects.requireNonNull(requestId, "requestId");
    Objects.requireNonNull(responseId, "responseId");
    Objects.requireNonNull(sentAt, "sentAt");
    try {
      require(!connection.getAutoCommit());
      require(completion.responseLayoutId().equals("LGNRSP01"));
      require(completion.responseVersion().equals("001"));
      var snapshot = completion.responseSnapshot().orElseThrow(SQLException::new);
      byte[] body = snapshots.decrypt(identity(requestId), snapshot);
      try {
        require(body.length == 688);
        CommonHeader original = HeaderCodec.standard().peek(body);
        require(original.layoutId().equals(LOGIN));
        require(original.correlationId().equals(requestId));
        ResultCode code = original.resultCode().orElseThrow(SQLException::new);
        byte[] data = Arrays.copyOfRange(body, 256, 688);
        try {
          var values = PayloadCodec.standard().decode(LOGIN, data, List.of(), code);
          if (code == ResultCode.SUCCESS) {
            require(completion.state() == InboxCompletionState.COMPLETED);
            require(completion.resultReference().type() == InboxResultReferenceType.AUTH_SESSION);
            var typed = (LoginResponseData) PayloadTypeCatalog.decode(values).data();
            validateSession(
                connection, completion.resultReference().uuid().orElseThrow(), requestId, typed);
            if (replay) code = ResultCode.IDEMPOTENT_SUCCESS;
          } else {
            require(code == ResultCode.AUTHENTICATION_FAILED || code == ResultCode.LOCKED);
            require(completion.state() == InboxCompletionState.ERROR);
            require(completion.resultReference().type() == InboxResultReferenceType.NONE);
          }
          return wire(
              PayloadCodec.standard().encode(values, code), code, requestId, responseId, sentAt);
        } finally {
          Arrays.fill(data, (byte) 0);
        }
      } finally {
        Arrays.fill(body, (byte) 0);
      }
    } catch (SQLException
        | ResponseSnapshotException
        | AuthContextCryptoException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      // No provider text, parameter, ciphertext, context, cause or suppressed close error escapes.
      throw new AuthenticationInfrastructureException();
    }
  }

  private void validateSession(
      Connection connection, UUID sessionId, UUID requestId, LoginResponseData data)
      throws SQLException {
    try (var statement = connection.prepareStatement(READ_SESSION)) {
      statement.setObject(1, sessionId);
      try (var row = statement.executeQuery()) {
        require(row.next());
        long owner = requireValue(row.getObject("user_id", Long.class));
        require(requestId.equals(requireValue(row.getObject("created_message_id", UUID.class))));
        byte[] cipher = requireValue(row.getBytes("context_ciphertext"));
        try {
          var raw =
              contexts.decrypt(
                  new AuthContextIdentity(sessionId, owner),
                  new EncryptedAuthContext(requireValue(row.getString("key_version")), cipher));
          require(
              secretEquals(
                  raw.wireValue(), data.authenticationContextId().orElseThrow().wireValue()));
          require(secretEquals(hashes.calculate(raw), requireValue(row.getString("context_hash"))));
        } finally {
          Arrays.fill(cipher, (byte) 0);
        }
        Instant issued = requireValue(row.getTimestamp("issued_at")).toInstant();
        require(issued.truncatedTo(ChronoUnit.MILLIS).equals(data.issuedAt().orElseThrow()));
        require(
            issued
                .plusSeconds(28800)
                .truncatedTo(ChronoUnit.MILLIS)
                .equals(data.expiresAt().orElseThrow()));
      }
    }
  }

  private static ResponseSnapshotIdentity identity(UUID requestId) {
    return ResponseSnapshotIdentity.anonymous(requestId, "LGNRSP01", "001");
  }

  private static byte[] wire(
      FixedPayload payload, ResultCode code, UUID requestId, UUID responseId, Instant sentAt) {
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            LOGIN,
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            responseId,
            requestId,
            sentAt.truncatedTo(ChronoUnit.MILLIS),
            Optional.empty(),
            256,
            432,
            0,
            0,
            688,
            Optional.of(code));
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private static boolean secretEquals(String left, String right) {
    byte[] a = left.getBytes(StandardCharsets.US_ASCII);
    byte[] b = right.getBytes(StandardCharsets.US_ASCII);
    try {
      return MessageDigest.isEqual(a, b);
    } finally {
      Arrays.fill(a, (byte) 0);
      Arrays.fill(b, (byte) 0);
    }
  }

  private static void require(boolean valid) throws SQLException {
    if (!valid) throw new SQLException("saved login result is inconsistent", "22000");
  }
}
