package dev.codex.schubert.nk.api.security;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import static dev.codex.schubert.nk.api.database.RequiredColumn.requireValue;

import dev.codex.schubert.nk.api.database.JdbcResourceCleanup;
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
import org.jspecify.annotations.Nullable;

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
      // SSC424: provider-null is an integrity error; close only established owned resources.
      var userStatement = requireValue(connection.prepareStatement(LOCK_USER));
      @Nullable Throwable userFailure = null;
      try {
        userStatement.setLong(1, userId);
        var userRows = requireValue(userStatement.executeQuery());
        @Nullable Throwable userRowsFailure = null;
        try {
          if (!userRows.next() || !requireValue(userRows.getString("status")).equals("ACTIVE")) {
            throw new AuthenticationContextException();
          }
        } catch (SQLException | RuntimeException | Error failure) {
          userRowsFailure = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeRows(userRowsFailure, userRows);
        }
      } catch (SQLException | RuntimeException | Error failure) {
        userFailure = failure;
        throw failure;
      } finally {
        JdbcResourceCleanup.closeStatement(userFailure, userStatement);
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
      try {
        var insertStatement = requireValue(connection.prepareStatement(INSERT));
        @Nullable Throwable insertFailure = null;
        try {
          insertStatement.setObject(1, identity.sessionId());
          insertStatement.setLong(2, userId);
          insertStatement.setString(3, hashes.calculate(raw));
          insertStatement.setBytes(4, ciphertext);
          insertStatement.setString(5, encrypted.keyVersion());
          insertStatement.setObject(6, issuedAt.atOffset(java.time.ZoneOffset.UTC));
          insertStatement.setObject(7, issuedAt.atOffset(java.time.ZoneOffset.UTC));
          insertStatement.setObject(8, expiresAt.atOffset(java.time.ZoneOffset.UTC));
          insertStatement.setString(9, client.getHostAddress());
          insertStatement.setObject(10, messageId);
          if (insertStatement.executeUpdate() != EXPECTED_AFFECTED_ROWS) {
            throw new SQLException("session insert did not create one row", "40001");
          }
        } catch (SQLException | RuntimeException | Error failure) {
          insertFailure = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(insertFailure, insertStatement);
        }
      } finally {
        Arrays.fill(ciphertext, (byte) 0);
      }
      var active = new ArrayList<UUID>();
      var activeStatement = requireValue(connection.prepareStatement(LOCK_ACTIVE));
      @Nullable Throwable activeFailure = null;
      try {
        activeStatement.setLong(1, userId);
        activeStatement.setObject(2, issuedAt.atOffset(java.time.ZoneOffset.UTC));
        var activeRows = requireValue(activeStatement.executeQuery());
        @Nullable Throwable activeRowsFailure = null;
        try {
          while (activeRows.next())
            active.add(requireValue(activeRows.getObject("id", UUID.class)));
        } catch (SQLException | RuntimeException | Error failure) {
          activeRowsFailure = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeRows(activeRowsFailure, activeRows);
        }
      } catch (SQLException | RuntimeException | Error failure) {
        activeFailure = failure;
        throw failure;
      } finally {
        JdbcResourceCleanup.closeStatement(activeFailure, activeStatement);
      }
      for (int index = 0; index < active.size() - 2; index++) {
        var replacementStatement = requireValue(connection.prepareStatement(REPLACE));
        @Nullable Throwable replacementFailure = null;
        try {
          replacementStatement.setObject(1, issuedAt.atOffset(java.time.ZoneOffset.UTC));
          replacementStatement.setObject(2, active.get(index));
          if (replacementStatement.executeUpdate() != EXPECTED_AFFECTED_ROWS) {
            throw new SQLException("session replacement changed during issue", "40001");
          }
        } catch (SQLException | RuntimeException | Error failure) {
          replacementFailure = failure;
          throw failure;
        } finally {
          JdbcResourceCleanup.closeStatement(replacementFailure, replacementStatement);
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
