package dev.codex.schubert.nk.web.session;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLDataException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/**
 * Ciphertext-only technical SQL, caller-owned short transaction, never UPSERT or business schema.
 * NK-WEB-001/NK-AUT-001; FUN-001/AUT-001..004; UI226/242; SS312/314 §7.2.3/331 §9.1/352;
 * SSC-040/PG-D-096/PT-WEB-024..031. Public arguments nonnull; no connection lifecycle ownership.
 */
public final class JdbcWebSessionStore {
  private static final String COLUMNS =
      "id,session_id_hash,attributes_ciphertext,key_version,created_at,last_accessed_at,expires_at,max_inactive_seconds,version";

  /**
   * Locks by hash, including expired rows for outer lifecycle handling; absence is not creation.
   */
  public Optional<WebSessionRow> findLocked(Connection connection, String hash) {
    Objects.requireNonNull(connection, "connection");
    requireHash(hash);
    try {
      transaction(connection);
      try (var statement =
          required(
              connection.prepareStatement(
                  "select "
                      + COLUMNS
                      + " from schubert_web_session.web_http_sessions where session_id_hash=? for update"))) {
        statement.setString(1, hash);
        try (var result = required(statement.executeQuery())) {
          Optional<WebSessionRow> found = Optional.empty();
          if (result.next()) {
            var row = read(result);
            if (result.next()) throw new InvalidSessionRowException();
            found = Optional.of(row);
          }
          return found;
        }
      }
    } catch (InvalidSessionRowException failure) {
      throw new InvalidSessionRowException();
    } catch (SQLException
        | IllegalArgumentException
        | java.time.DateTimeException
        | SessionStoreException failure) {
      throw new SessionStoreException();
    }
  }

  /** Inserts only an explicitly new version0 row; failure never degrades into an update. */
  public void insert(Connection connection, WebSessionRow row) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(row, "row");
    if (row.version() != 0) throw new IllegalArgumentException("new session version must be zero");
    try {
      transaction(connection);
      try (var statement =
          required(
              connection.prepareStatement(
                  "insert into schubert_web_session.web_http_sessions ("
                      + COLUMNS
                      + ") values (?,?,?,?,?,?,?,?,?)"))) {
        statement.setObject(1, row.identity().id());
        statement.setString(2, row.identity().sessionIdHash());
        statement.setBytes(3, row.payload().ciphertext());
        statement.setString(4, row.payload().keyVersion());
        statement.setObject(5, row.identity().createdAt().atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(6, row.lastAccessedAt().atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(7, row.expiresAt().atOffset(java.time.ZoneOffset.UTC));
        statement.setInt(8, row.maxInactiveSeconds());
        statement.setLong(9, row.version());
        if (statement.executeUpdate() != 1) throw new SessionStoreException();
      }
    } catch (SQLException
        | IllegalArgumentException
        | java.time.DateTimeException
        | SessionStoreException failure) {
      throw new SessionStoreException();
    }
  }

  /**
   * Identity must stay equal and version increment exactly once; stale/deleted rows return false.
   */
  public boolean replace(Connection connection, WebSessionRow original, WebSessionRow replacement) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(original, "original");
    Objects.requireNonNull(replacement, "replacement");
    if (!original.identity().equals(replacement.identity())
        || replacement.version() != original.version() + 1)
      throw new IllegalArgumentException("session replacement identity or version is invalid");
    try {
      transaction(connection);
      try (var statement =
          required(
              connection.prepareStatement(
                  "update schubert_web_session.web_http_sessions set attributes_ciphertext=?,key_version=?,"
                      + "last_accessed_at=?,expires_at=?,max_inactive_seconds=?,version=? "
                      + "where id=? and session_id_hash=? and created_at=? and version=?"))) {
        statement.setBytes(1, replacement.payload().ciphertext());
        statement.setString(2, replacement.payload().keyVersion());
        statement.setObject(3, replacement.lastAccessedAt().atOffset(java.time.ZoneOffset.UTC));
        statement.setObject(4, replacement.expiresAt().atOffset(java.time.ZoneOffset.UTC));
        statement.setInt(5, replacement.maxInactiveSeconds());
        statement.setLong(6, replacement.version());
        identity(statement, 7, original.identity());
        statement.setLong(10, original.version());
        return changed(statement.executeUpdate());
      }
    } catch (SQLException
        | IllegalArgumentException
        | java.time.DateTimeException
        | SessionStoreException failure) {
      throw new SessionStoreException();
    }
  }

  /** Deletes only the observed identity/version, permitting atomic fixation in the caller TX. */
  public boolean delete(Connection connection, SessionPayloadIdentity identity, long version) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(identity, "identity");
    WebSessionRow.requireVersion(version);
    try {
      transaction(connection);
      try (var statement =
          required(
              connection.prepareStatement(
                  "delete from schubert_web_session.web_http_sessions where id=? and session_id_hash=? and created_at=? and version=?"))) {
        identity(statement, 1, identity);
        statement.setLong(4, version);
        return changed(statement.executeUpdate());
      }
    } catch (SQLException
        | IllegalArgumentException
        | java.time.DateTimeException
        | SessionStoreException failure) {
      throw new SessionStoreException();
    }
  }

  private static WebSessionRow read(ResultSet result) throws SQLException {
    try {
      return new WebSessionRow(
          new SessionPayloadIdentity(
              column(result.getObject("id", UUID.class)),
              column(result.getString("session_id_hash")),
              column(result.getObject("created_at", OffsetDateTime.class)).toInstant()),
          new EncryptedSessionPayload(
              column(result.getString("key_version")),
              column(result.getBytes("attributes_ciphertext"))),
          column(result.getObject("last_accessed_at", OffsetDateTime.class)).toInstant(),
          column(result.getObject("expires_at", OffsetDateTime.class)).toInstant(),
          column(result.getObject("max_inactive_seconds", Integer.class)),
          column(result.getObject("version", Long.class)));
    } catch (IllegalArgumentException | SQLDataException failure) {
      throw new InvalidSessionRowException();
    }
  }

  /** SSC-041/PT-WEB-037/041: invalidates even an unreadable row, using only the validated hash. */
  public boolean deleteByHash(Connection connection, String hash) {
    Objects.requireNonNull(connection, "connection");
    requireHash(hash);
    try {
      transaction(connection);
      try (var statement =
          required(
              connection.prepareStatement(
                  "delete from schubert_web_session.web_http_sessions where session_id_hash=?"))) {
        statement.setString(1, hash);
        return changed(statement.executeUpdate());
      }
    } catch (SQLException | SessionStoreException failure) {
      throw new SessionStoreException();
    }
  }

  private static void requireHash(String hash) {
    Objects.requireNonNull(hash, "hash");
    if (!hash.matches("[0-9a-f]{64}"))
      throw new IllegalArgumentException("session lookup is invalid");
  }

  private static <T> T column(@Nullable T value) {
    if (value == null) throw new InvalidSessionRowException();
    return value;
  }

  private static void identity(
      PreparedStatement statement, int index, SessionPayloadIdentity identity) throws SQLException {
    statement.setObject(index, identity.id());
    statement.setString(index + 1, identity.sessionIdHash());
    statement.setObject(index + 2, identity.createdAt().atOffset(java.time.ZoneOffset.UTC));
  }

  private static boolean changed(int count) {
    if (count < 0 || count > 1) throw new SessionStoreException();
    return count == 1;
  }

  private static void transaction(Connection connection) throws SQLException {
    if (connection.getAutoCommit() || connection.isReadOnly()) throw new SessionStoreException();
  }

  private static <T> T required(@Nullable T value) {
    if (value == null) throw new SessionStoreException();
    return value;
  }
}
