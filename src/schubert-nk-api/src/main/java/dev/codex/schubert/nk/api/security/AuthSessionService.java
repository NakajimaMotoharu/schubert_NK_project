package dev.codex.schubert.nk.api.security;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import java.net.InetAddress;
import java.security.SecureRandom;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Objects;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Session issuance with atomic replacement audit; the authenticated Login/Inbox caller owns
 * transaction. Trace: NK-AUT-001, AUT-001..004, DIF-016; UI226; SS312 §4/314 §6/332 §5;
 * PT-AUT-005-I/006.
 */
public final class AuthSessionService {
  private static final int EXPECTED_AFFECTED_ROWS = 1;

  private static final String LOCK_USER =
      "select status from schubert.app_users where id=? for update";
  private static final String INSERT =
      "insert into schubert.auth_sessions "
          + "(id,user_id,context_hash,context_ciphertext,key_version,issued_at,last_accessed_at,expires_at,client_address,created_message_id)"
          + " values(?,?,?,?,?,?,?,?,cast(? as inet),?)";
  private static final String LOCK_ACTIVE =
      "select id from schubert.auth_sessions where user_id=? and not revoked and expires_at>? "
          + "order by last_accessed_at,id for update";
  private static final String REPLACE =
      "update schubert.auth_sessions set revoked=true,revoked_at=?,revoke_reason='REPLACED' "
          + "where id=? and not revoked";
  private final ContextHash hashes;
  private final AuthContextCodec codec;
  private final SecureRandom random;
  private final Supplier<UUID> ids;
  private final SessionAuditWriter audit = new SessionAuditWriter();

  public AuthSessionService(ContextHash hashes, AuthContextCodec codec) {
    this(hashes, codec, new SecureRandom(), UUID::randomUUID);
  }

  AuthSessionService(
      ContextHash hashes, AuthContextCodec codec, SecureRandom random, Supplier<UUID> ids) {
    this.hashes = Objects.requireNonNull(hashes, "hashes");
    this.codec = Objects.requireNonNull(codec, "codec");
    this.random = Objects.requireNonNull(random, "random");
    this.ids = Objects.requireNonNull(ids, "ids");
  }

  /** Caller must rollback on failure; duplicate Message IDs must take the Inbox replay path. */
  public IssuedContext issue(
      Connection connection,
      long userId,
      InetAddress client,
      UUID messageId,
      UUID correlationId,
      Instant now) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(client, "client");
    Objects.requireNonNull(messageId, "messageId");
    Objects.requireNonNull(correlationId, "correlationId");
    Objects.requireNonNull(now, "now");
    if (userId < 1 || userId > 999_999_999_999L) {
      throw new IllegalArgumentException("session owner is outside N12");
    }
    Instant issuedAt = now.truncatedTo(ChronoUnit.MICROS);
    Instant expiresAt = issuedAt.plus(8, ChronoUnit.HOURS);
    try {
      if (connection.getAutoCommit()) {
        throw new SQLException("session issue requires an explicit transaction", "25000");
      }
      try (var statement = connection.prepareStatement(LOCK_USER)) {
        statement.setLong(1, userId);
        try (var row = statement.executeQuery()) {
          if (!row.next() || !requireValue(row.getString("status")).equals("ACTIVE")) {
            throw new AuthenticationContextException();
          }
        }
      }
      AuthContextIdentity identity = new AuthContextIdentity(ids.get(), userId);
      byte[] bytes = new byte[32];
      AuthenticationContext raw;
      try {
        random.nextBytes(bytes);
        raw = AuthenticationContext.of(HexFormat.of().formatHex(bytes));
      } finally {
        Arrays.fill(bytes, (byte) 0);
      }
      EncryptedAuthContext encrypted = codec.encrypt(identity, raw);
      byte[] ciphertext = encrypted.ciphertext();
      try (var statement = connection.prepareStatement(INSERT)) {
        statement.setObject(1, identity.sessionId());
        statement.setLong(2, userId);
        statement.setString(3, hashes.calculate(raw));
        statement.setBytes(4, ciphertext);
        statement.setString(5, encrypted.keyVersion());
        statement.setObject(6, issuedAt.atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(7, issuedAt.atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(8, expiresAt.atOffset(java.time.ZoneOffset.UTC));
        statement.setString(9, client.getHostAddress());
        statement.setObject(10, messageId);
        if (statement.executeUpdate() != EXPECTED_AFFECTED_ROWS) {
          throw new SQLException("session insert did not create one row", "40001");
        }
      } finally {
        Arrays.fill(ciphertext, (byte) 0);
      }
      var active = new ArrayList<UUID>();
      try (var statement = connection.prepareStatement(LOCK_ACTIVE)) {
        statement.setLong(1, userId);
        statement.setObject(2, issuedAt.atOffset(java.time.ZoneOffset.UTC));
        try (var row = statement.executeQuery()) {
          while (row.next()) active.add(requireValue(row.getObject("id", UUID.class)));
        }
      }
      for (int index = 0; index < active.size() - 2; index++) {
        try (var statement = connection.prepareStatement(REPLACE)) {
          statement.setObject(1, issuedAt.atOffset(java.time.ZoneOffset.UTC));
          statement.setObject(2, active.get(index));
          if (statement.executeUpdate() != EXPECTED_AFFECTED_ROWS) {
            throw new SQLException("session replacement changed during issue", "40001");
          }
        }
        audit.write(
            connection,
            userId,
            userId,
            java.util.Optional.of(client),
            messageId,
            correlationId,
            issuedAt,
            SessionRevocationReason.REPLACED,
            ResultCode.SUCCESS);
      }
      return new IssuedContext(identity, raw, issuedAt, expiresAt);
    } catch (SQLException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      throw new AuthenticationInfrastructureException();
    } catch (AuthenticationContextException failure) {
      AuthenticationInfrastructureException.preserveFatal(failure);
      if (failure.getSuppressed().length != 0) {
        throw new AuthenticationInfrastructureException();
      }
      throw new AuthenticationContextException();
    }
  }
}
