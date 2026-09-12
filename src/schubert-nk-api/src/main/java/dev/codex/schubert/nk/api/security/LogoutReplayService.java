package dev.codex.schubert.nk.api.security;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.idempotency.*;
import dev.codex.schubert.nk.protocol.codec.*;
import dev.codex.schubert.nk.protocol.header.*;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.protocol.layout.auth.LogoutResponseData;
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
 * Immutable Logout result with owner/session reference verification. Never authenticates a caller.
 * NK-AUT-001/NK-MSG-002; AUT-004/MQ-006..010; UI232/234/241; SS314/324 section 6.2, SSC-015;
 * PT-AUT-LOGOUT-INBOX-001..006. Caller owns the transaction and rolls back any failure.
 */
public final class LogoutReplayService {
  private static final LayoutId LOGOUT = new LayoutId("LOGRSP01");
  private final ResponseSnapshotCodec snapshots;
  private final ContextHash hashes;

  public LogoutReplayService(ResponseSnapshotCodec snapshots, ContextHash hashes) {
    this.snapshots = Objects.requireNonNull(snapshots, "snapshots");
    this.hashes = Objects.requireNonNull(hashes, "hashes");
  }

  public InboxCompletion captureSuccess(
      RevokedContext result, AuthenticationContext raw, UUID request, UUID response, Instant at) {
    Objects.requireNonNull(result, "result");
    return capture(
        result.identity().userId(),
        InboxCompletionState.COMPLETED,
        InboxResultReference.authSession(result.identity().sessionId()),
        wire(
            new AuthenticationResponseMapper().logout(result),
            result.resultCode(),
            raw,
            request,
            response,
            at),
        request,
        at);
  }

  public InboxCompletion captureDenied(
      long owner, AuthenticationContext raw, UUID request, UUID response, Instant at) {
    return capture(
        owner,
        InboxCompletionState.ERROR,
        InboxResultReference.none(),
        failure(ResultCode.SESSION_INVALID, raw, request, response, at),
        request,
        at);
  }

  /**
   * Non-persisted invalid-context/PROCESSING response only; caller must not treat it as success.
   */
  public byte[] failure(
      ResultCode code, AuthenticationContext raw, UUID request, UUID response, Instant at) {
    Objects.requireNonNull(code, "code");
    if (code != ResultCode.SESSION_INVALID && code != ResultCode.TEMPORARY_FAILURE)
      throw new IllegalArgumentException("invalid Logout failure code");
    var payload =
        PayloadCodec.standard()
            .encode(new PayloadValues(LOGOUT, FieldValueSet.empty(), List.of()), code);
    return wire(payload, code, raw, request, response, at);
  }

  private InboxCompletion capture(
      long owner,
      InboxCompletionState state,
      InboxResultReference reference,
      byte[] body,
      UUID request,
      Instant at) {
    try {
      return new InboxCompletion(
          state,
          reference,
          "LOGRSP01",
          "001",
          Optional.of(snapshots.encrypt(identity(request, owner), body)),
          at.truncatedTo(ChronoUnit.MICROS));
    } catch (ResponseSnapshotException | IllegalStateException failure) {
      throw new AuthenticationInfrastructureException();
    } finally {
      Arrays.fill(body, (byte) 0);
    }
  }

  /** Fresh header, original DATA/error, no updates or permission grant. */
  public byte[] restore(
      Connection connection,
      InboxCompletion saved,
      long owner,
      AuthenticationContext currentRaw,
      UUID request,
      UUID response,
      Instant at,
      boolean replay) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(saved, "saved");
    Objects.requireNonNull(currentRaw, "currentRaw");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(response, "response");
    Objects.requireNonNull(at, "at");
    try {
      require(!connection.getAutoCommit());
      require(saved.responseLayoutId().equals("LOGRSP01"));
      require(saved.responseVersion().equals("001"));
      var encrypted = saved.responseSnapshot().orElseThrow(SQLException::new);
      byte[] body = snapshots.decrypt(identity(request, owner), encrypted);
      try {
        require(body.length == 280);
        CommonHeader original = HeaderCodec.standard().peek(body);
        require(original.layoutId().equals(LOGOUT));
        require(original.correlationId().equals(request));
        ResultCode code = original.resultCode().orElseThrow(SQLException::new);
        byte[] data = Arrays.copyOfRange(body, 256, 280);
        try {
          var values = PayloadCodec.standard().decode(LOGOUT, data, List.of(), code);
          if (code.usesSuccessProfile()) {
            require(saved.state() == InboxCompletionState.COMPLETED);
            require(saved.resultReference().type() == InboxResultReferenceType.AUTH_SESSION);
            var typed = (LogoutResponseData) PayloadTypeCatalog.decode(values).data();
            validateSession(
                connection,
                saved.resultReference().uuid().orElseThrow(),
                owner,
                original.authenticationContext().orElseThrow(),
                typed);
            if (replay) code = ResultCode.IDEMPOTENT_SUCCESS;
          } else {
            require(code == ResultCode.SESSION_INVALID);
            require(saved.state() == InboxCompletionState.ERROR);
            require(saved.resultReference().type() == InboxResultReferenceType.NONE);
          }
          return wire(
              PayloadCodec.standard().encode(values, code),
              code,
              currentRaw,
              request,
              response,
              at);
        } finally {
          Arrays.fill(data, (byte) 0);
        }
      } finally {
        Arrays.fill(body, (byte) 0);
      }
    } catch (SQLException
        | ResponseSnapshotException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      throw new AuthenticationInfrastructureException();
    }
  }

  private void validateSession(
      Connection connection,
      UUID id,
      long owner,
      AuthenticationContext original,
      LogoutResponseData data)
      throws SQLException {
    try (var statement =
        connection.prepareStatement(
            "select user_id,context_hash,revoked,revoked_at from schubert.auth_sessions where id=?")) {
      statement.setObject(1, id);
      try (var row = statement.executeQuery()) {
        require(row.next());
        require(requireValue(row.getObject("user_id", Long.class)) == owner);
        require(requireValue(row.getObject("revoked", Boolean.class)));
        require(
            requireValue(row.getObject("revoked_at", java.time.OffsetDateTime.class))
                .toInstant()
                .truncatedTo(ChronoUnit.MILLIS)
                .equals(data.sessionRevokedAt()));
        byte[] actual =
            requireValue(row.getString("context_hash")).getBytes(StandardCharsets.US_ASCII);
        byte[] expected = hashes.calculate(original).getBytes(StandardCharsets.US_ASCII);
        try {
          require(MessageDigest.isEqual(expected, actual));
        } finally {
          Arrays.fill(actual, (byte) 0);
          Arrays.fill(expected, (byte) 0);
        }
      }
    }
  }

  private static ResponseSnapshotIdentity identity(UUID request, long owner) {
    return ResponseSnapshotIdentity.authenticated(request, "LOGRSP01", "001", owner);
  }

  private static byte[] wire(
      FixedPayload payload,
      ResultCode code,
      AuthenticationContext raw,
      UUID request,
      UUID response,
      Instant at) {
    var header =
        new CommonHeader(
            "SCHBNK01",
            1,
            LOGOUT,
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            response,
            request,
            at.truncatedTo(ChronoUnit.MILLIS),
            Optional.of(raw),
            256,
            24,
            0,
            0,
            280,
            Optional.of(code));
    return FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
  }

  private static void require(boolean valid) throws SQLException {
    if (!valid) throw new SQLException("saved Logout result is inconsistent", "22000");
  }
}
