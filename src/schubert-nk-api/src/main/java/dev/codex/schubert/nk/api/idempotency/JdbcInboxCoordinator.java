package dev.codex.schubert.nk.api.idempotency;

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Savepoint;
import java.sql.Timestamp;
import java.sql.Types;
import java.util.HexFormat;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;

/**
 * PostgreSQL Inbox coordinator that never owns, commits or rolls back the caller transaction.
 *
 * <p>Trace: NK-MSG-002, RD MQ-006..010/FUN-103..105, UI 241/242, SS 324 §4..§7,
 * PT-IDEM-004..006.
 */
public final class JdbcInboxCoordinator {
  private static final String SELECT_COLUMNS =
      "correlation_id,request_layout_id,request_version,owner_user_id,operation_token,"
          + "request_fingerprint_hmac,fingerprint_key_version,processing_state,result_ref_type,"
          + "result_ref_id,result_ref_uuid,response_layout_id,response_version,"
          + "response_body_encrypted,response_key_version,completed_at";
  private static final String SELECT_BY_MESSAGE =
      "select " + SELECT_COLUMNS + " from schubert.request_inbox where message_id=? for update";
  private static final String SELECT_BY_TOKEN =
      "select "
          + SELECT_COLUMNS
          + " from schubert.request_inbox where owner_user_id=? and operation_token=? for update";
  private static final String INSERT =
      "insert into schubert.request_inbox(message_id,correlation_id,request_layout_id,"
          + "request_version,owner_user_id,operation_token,request_fingerprint_hmac,"
          + "fingerprint_key_version,processing_state,created_at,expires_at) "
          + "values(?,?,?,?,?,?,?,?, 'PROCESSING',?,?)";
  private static final String COMPLETE =
      "update schubert.request_inbox set processing_state=?,result_ref_type=?,result_ref_id=?,"
          + "result_ref_uuid=?,response_layout_id=?,response_version=?,response_body_encrypted=?,"
          + "response_key_version=?,completed_at=? where message_id=? and processing_state='PROCESSING'";

  private final FingerprintKeyRing fingerprints;

  public JdbcInboxCoordinator(FingerprintKeyRing fingerprints) {
    this.fingerprints = Objects.requireNonNull(fingerprints, "fingerprints");
  }

  public InboxExecution execute(Connection connection, InboxRequest request, InboxHandler handler)
      throws SQLException {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(handler, "handler");
    if (connection.getAutoCommit()) {
      throw failure(
          InboxException.Reason.TRANSACTION_REQUIRED,
          "Inbox coordination requires a caller-owned transaction");
    }

    Optional<StoredRow> messageRow = selectByMessage(connection, request.messageId());
    if (messageRow.isPresent()) {
      StoredRow row = messageRow.orElseThrow();
      validateMessageIdentity(row, request);
      return existing(row);
    }

    if (request.operationToken().isPresent()) {
      Optional<StoredRow> tokenRow =
          selectByToken(
              connection,
              request.ownerUserId().orElseThrow(),
              request.operationToken().orElseThrow());
      if (tokenRow.isPresent()) {
        StoredRow row = tokenRow.orElseThrow();
        validateTokenFingerprint(row, request);
        return existing(row);
      }
    }

    Fingerprint fingerprint = fingerprints.calculate(request.canonicalRequest());
    Savepoint beforeInsert = connection.setSavepoint();
    try {
      insert(connection, request, fingerprint);
      connection.releaseSavepoint(beforeInsert);
    } catch (SQLException exception) {
      if (!"23505".equals(exception.getSQLState())) {
        throw exception;
      }
      connection.rollback(beforeInsert);
      connection.releaseSavepoint(beforeInsert);
      Optional<StoredRow> concurrentRow = selectByMessage(connection, request.messageId());
      if (concurrentRow.isPresent()) {
        StoredRow row = concurrentRow.orElseThrow();
        validateMessageIdentity(row, request);
        return existing(row);
      }
      if (request.operationToken().isPresent()) {
        concurrentRow =
            selectByToken(
                connection,
                request.ownerUserId().orElseThrow(),
                request.operationToken().orElseThrow());
        if (concurrentRow.isPresent()) {
          StoredRow row = concurrentRow.orElseThrow();
          validateTokenFingerprint(row, request);
          return existing(row);
        }
      }
      throw exception;
    }

    InboxCompletion completion =
        Objects.requireNonNull(handler.handle(connection), "handler completion");
    if (completion.completedAt().isBefore(request.receivedAt())) {
      throw failure(
          InboxException.Reason.STATE_CORRUPT,
          "Inbox completion time precedes the request receipt time");
    }
    complete(connection, request.messageId(), completion);
    return InboxExecution.executed(completion);
  }

  private Optional<StoredRow> selectByMessage(Connection connection, UUID messageId)
      throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(SELECT_BY_MESSAGE)) {
      statement.setObject(1, messageId);
      return selectOne(statement);
    }
  }

  private Optional<StoredRow> selectByToken(Connection connection, long ownerUserId, UUID token)
      throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(SELECT_BY_TOKEN)) {
      statement.setLong(1, ownerUserId);
      statement.setObject(2, token);
      return selectOne(statement);
    }
  }

  private static Optional<StoredRow> selectOne(PreparedStatement statement) throws SQLException {
    try (ResultSet result = statement.executeQuery()) {
      return result.next() ? Optional.of(read(result)) : Optional.empty();
    }
  }

  private static StoredRow read(ResultSet result) throws SQLException {
    OptionalLong owner = optionalLong(result, "owner_user_id");
    Optional<UUID> token = Optional.ofNullable(result.getObject("operation_token", UUID.class));
    Fingerprint fingerprint =
        new Fingerprint(
            requireValue(result.getString("fingerprint_key_version")),
            HexFormat.of().parseHex(requireValue(result.getString("request_fingerprint_hmac"))));
    String processingState = requireValue(result.getString("processing_state"));
    Optional<InboxCompletion> completion =
        processingState.equals("PROCESSING") ? Optional.empty() : Optional.of(readCompletion(result));
    return new StoredRow(
        requireValue(result.getObject("correlation_id", UUID.class)),
        requireValue(result.getString("request_layout_id")),
        requireValue(result.getString("request_version")),
        owner,
        token,
        fingerprint,
        processingState,
        completion);
  }

  private static InboxCompletion readCompletion(ResultSet result) throws SQLException {
    InboxCompletionState state = InboxCompletionState.valueOf(requireValue(result.getString("processing_state")));
    InboxResultReferenceType referenceType =
        InboxResultReferenceType.valueOf(requireValue(result.getString("result_ref_type")));
    InboxResultReference reference =
        new InboxResultReference(
            referenceType,
            optionalLong(result, "result_ref_id"),
            Optional.ofNullable(result.getObject("result_ref_uuid", UUID.class)));
    byte[] ciphertext = result.getBytes("response_body_encrypted");
    Optional<EncryptedResponseSnapshot> snapshot =
        ciphertext == null
            ? Optional.empty()
            : Optional.of(
                new EncryptedResponseSnapshot(requireValue(result.getString("response_key_version")), ciphertext));
    return new InboxCompletion(
        state,
        reference,
        requireValue(result.getString("response_layout_id")),
        requireValue(result.getString("response_version")),
        snapshot,
        requireValue(result.getTimestamp("completed_at")).toInstant());
  }

  private static OptionalLong optionalLong(ResultSet result, String column) throws SQLException {
    long value = result.getLong(column);
    return result.wasNull() ? OptionalLong.empty() : OptionalLong.of(value);
  }

  private static void insert(Connection connection, InboxRequest request, Fingerprint fingerprint)
      throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(INSERT)) {
      statement.setObject(1, request.messageId());
      statement.setObject(2, request.correlationId());
      statement.setString(3, request.canonicalRequest().layoutId());
      statement.setString(4, request.canonicalRequest().layoutVersion());
      setOptionalLong(statement, 5, request.ownerUserId());
      setOptionalUuid(statement, 6, request.operationToken());
      statement.setString(7, HexFormat.of().formatHex(fingerprint.digest()));
      statement.setString(8, fingerprint.keyVersion());
      statement.setTimestamp(9, Timestamp.from(request.receivedAt()));
      statement.setTimestamp(10, Timestamp.from(request.expiresAt()));
      statement.executeUpdate();
    }
  }

  private static void complete(
      Connection connection, UUID messageId, InboxCompletion completion) throws SQLException {
    try (PreparedStatement statement = connection.prepareStatement(COMPLETE)) {
      statement.setString(1, completion.state().name());
      InboxResultReference reference = completion.resultReference();
      statement.setString(2, reference.type().name());
      setOptionalLong(statement, 3, reference.numericId());
      setOptionalUuid(statement, 4, reference.uuid());
      statement.setString(5, completion.responseLayoutId());
      statement.setString(6, completion.responseVersion());
      if (completion.responseSnapshot().isPresent()) {
        EncryptedResponseSnapshot snapshot = completion.responseSnapshot().orElseThrow();
        statement.setBytes(7, snapshot.ciphertext());
        statement.setString(8, snapshot.keyVersion());
      } else {
        statement.setNull(7, Types.BINARY);
        statement.setNull(8, Types.VARCHAR);
      }
      statement.setTimestamp(9, Timestamp.from(completion.completedAt()));
      statement.setObject(10, messageId);
      if (statement.executeUpdate() != 1) {
        throw failure(
            InboxException.Reason.STATE_CORRUPT,
            "Inbox PROCESSING row disappeared before completion");
      }
    }
  }

  private void validateMessageIdentity(StoredRow stored, InboxRequest request) throws InboxException {
    boolean sameIdentity =
        stored.correlationId().equals(request.correlationId())
            && stored.layoutId().equals(request.canonicalRequest().layoutId())
            && stored.layoutVersion().equals(request.canonicalRequest().layoutVersion())
            && stored.ownerUserId().equals(request.ownerUserId())
            && stored.operationToken().equals(request.operationToken());
    if (!sameIdentity) {
      throw failure(
          InboxException.Reason.MESSAGE_ID_REUSE,
          "Message ID was reused with different request identity");
    }
    validateFingerprint(
        stored.fingerprint(),
        request.canonicalRequest(),
        InboxException.Reason.MESSAGE_ID_REUSE,
        "Message ID was reused with a different request payload");
  }

  private void validateTokenFingerprint(StoredRow stored, InboxRequest request) throws InboxException {
    validateFingerprint(
        stored.fingerprint(),
        request.canonicalRequest(),
        InboxException.Reason.OPERATION_TOKEN_REUSE,
        "Operation token was reused with a different request payload");
  }

  private void validateFingerprint(
      Fingerprint stored,
      CanonicalRequest request,
      InboxException.Reason mismatchReason,
      String mismatchMessage)
      throws InboxException {
    FingerprintVerification verification = fingerprints.verify(stored, request);
    if (verification == FingerprintVerification.MATCH) {
      return;
    }
    if (verification == FingerprintVerification.MISMATCH) {
      throw failure(mismatchReason, mismatchMessage);
    }
    throw failure(
        InboxException.Reason.FINGERPRINT_KEY_UNAVAILABLE,
        "Stored Inbox fingerprint key version is unavailable");
  }

  private static InboxExecution existing(StoredRow row) throws InboxException {
    if (row.processingState().equals("PROCESSING")) {
      return InboxExecution.inProgress();
    }
    return InboxExecution.replay(row.completion().orElseThrow());
  }

  private static void setOptionalLong(
      PreparedStatement statement, int parameter, OptionalLong value) throws SQLException {
    if (value.isPresent()) {
      statement.setLong(parameter, value.getAsLong());
    } else {
      statement.setNull(parameter, Types.BIGINT);
    }
  }

  private static void setOptionalUuid(
      PreparedStatement statement, int parameter, Optional<UUID> value) throws SQLException {
    if (value.isPresent()) {
      statement.setObject(parameter, value.orElseThrow());
    } else {
      statement.setNull(parameter, Types.OTHER);
    }
  }

  private static InboxException failure(InboxException.Reason reason, String message) {
    return new InboxException(reason, message);
  }

  private record StoredRow(
      UUID correlationId,
      String layoutId,
      String layoutVersion,
      OptionalLong ownerUserId,
      Optional<UUID> operationToken,
      Fingerprint fingerprint,
      String processingState,
      Optional<InboxCompletion> completion) {}
}
