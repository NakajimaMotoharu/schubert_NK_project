package dev.codex.schubert.nk.api.application.admin;

// PG-D-160/SSC056/BUG167/YKT128: SS332 JDBC4.2 UTC; existing Program/PT trace remains applicable.

import dev.codex.schubert.nk.api.error.TemporaryInfrastructureException;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.api.security.AuthSessionRevocationService;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.AuthorizationService;
import dev.codex.schubert.nk.api.security.LoginUsername;
import dev.codex.schubert.nk.api.security.PasswordHasher;
import dev.codex.schubert.nk.api.security.PasswordPolicy;
import dev.codex.schubert.nk.api.security.SessionRevocationReason;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Savepoint;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;

/**
 * Definite User mutations and mandatory audit in a caller-owned write transaction. Requires SSC031
 * prelude then current ADMIN authentication and a NEW Inbox execution; no direct HTTP registration.
 * NK-ADM-001; FUN-009/AUT-002/003/MON-004; UI225/226/236/242; SS312/314/324/331/332/351/352;
 * PG-D-083; PT-ADM-014..023.
 */
public final class UserCommandService {
  private static final int MAXIMUM_USER_VERSION = 999_999_999;

  private static final java.lang.String LITERAL_ACTIVE = "ACTIVE";

  @FunctionalInterface
  interface PasswordEncoding {
    String encode(char[] password);
  }

  private final PasswordEncoding passwords;
  private final AuthSessionRevocationService revocations;
  private final UserAuditWriter audit = new UserAuditWriter();
  private final PasswordPolicy policy = new PasswordPolicy();

  private enum Update {
    ENABLE,
    DISABLE,
    PROMOTE,
    DEMOTE,
    RESET_PASSWORD,
    UNLOCK
  }

  public UserCommandService(PasswordHasher passwords, AuthSessionRevocationService revocations) {
    Objects.requireNonNull(passwords, "passwords");
    this.passwords = passwords::encode;
    this.revocations = Objects.requireNonNull(revocations, "revocations");
  }

  UserCommandService(PasswordEncoding passwords, AuthSessionRevocationService revocations) {
    this.passwords = Objects.requireNonNull(passwords, "passwords");
    this.revocations = Objects.requireNonNull(revocations, "revocations");
  }

  /** Consumes password even when any other boundary argument fails. PT-ADM-014/019..023. */
  public UserMutationResult create(
      Connection c,
      AuthenticatedActor actor,
      String username,
      char[] password,
      UserRole role,
      boolean enabled,
      UserCommandMetadata metadata) {
    Objects.requireNonNull(password, "password");
    try {
      Objects.requireNonNull(username, "username");
      Objects.requireNonNull(role, "role");
      return execute(
          c,
          actor,
          Mutation.CREATE,
          metadata,
          () -> {
            LoginUsername name;
            char[] normalized;
            try {
              name = new LoginUsername(username);
              if (!name.value().matches("[A-Za-z0-9._-]+"))
                return rejected(ResultCode.VALIDATION_ERROR, Optional.empty(), Optional.empty());
              normalized = policy.normalizeForCreation(password, name.value());
            } catch (IllegalArgumentException invalid) {
              TemporaryInfrastructureException.preserveFatal(invalid);
              return rejected(ResultCode.VALIDATION_ERROR, Optional.empty(), Optional.empty());
            }
            String hash = encode(normalized);
            Savepoint savepoint = c.setSavepoint();
            Optional<UserId> created;
            try {
              try (var s =
                  c.prepareStatement(
                      """
              insert into schubert.app_users(username,username_key,password_hash,role,status,
                password_changed_at,created_at,updated_at,created_by,updated_by)
              values (?,?,?,?,?,?,?,?,?,?) on conflict(username_key) do nothing returning id
              """)) {
                s.setString(1, name.value());
                s.setString(2, name.key());
                s.setString(3, hash);
                s.setString(4, role.wireValue());
                s.setString(5, enabled ? LITERAL_ACTIVE : "DISABLED");
                for (int index = 6; index <= 8; index++)
                  s.setObject(index, metadata.at().atOffset(java.time.ZoneOffset.UTC));
                s.setLong(9, actor.userId());
                s.setLong(10, actor.userId());
                try (var r = s.executeQuery()) {
                  created = r.next() ? Optional.of(new UserId(number(r, "id"))) : Optional.empty();
                  require(!r.next());
                }
              }
            } catch (SQLException failure) {
              TemporaryInfrastructureException.preserveFatal(failure);
              if (!"2200H".equals(failure.getSQLState()) || failure.getSuppressed().length != 0)
                throw failure;
              c.rollback(savepoint);
              c.releaseSavepoint(savepoint);
              return rejected(ResultCode.RESOURCE_LIMIT, Optional.empty(), Optional.empty());
            }
            c.releaseSavepoint(savepoint);
            if (created.isEmpty())
              return rejected(ResultCode.CONFLICT, Optional.empty(), Optional.empty());
            State after =
                read(c, created.orElseThrow())
                    .orElseThrow(() -> new SQLException("created user is missing"));
            require(after.version() == 0);
            return accepted(Optional.empty(), after, ResultCode.SUCCESS);
          });
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  /** PT-ADM-015/019/020/022: target/ADMIN locks are already held by the required prelude. */
  public UserMutationResult changeStatus(
      Connection c,
      AuthenticatedActor actor,
      UserId id,
      boolean enabled,
      long expectedVersion,
      UserCommandMetadata metadata) {
    return update(
        c,
        actor,
        id,
        expectedVersion,
        enabled ? Update.ENABLE : Update.DISABLE,
        metadata,
        before -> new Values(before.role(), enabled, Optional.empty()));
  }

  /** PT-ADM-016/019/020/022: no implicit same-value bypass of the approved version update. */
  public UserMutationResult changeRole(
      Connection c,
      AuthenticatedActor actor,
      UserId id,
      UserRole role,
      long expectedVersion,
      UserCommandMetadata metadata) {
    Objects.requireNonNull(role, "role");
    return update(
        c,
        actor,
        id,
        expectedVersion,
        role == UserRole.ADMIN ? Update.PROMOTE : Update.DEMOTE,
        metadata,
        before -> new Values(role, before.enabled(), Optional.empty()));
  }

  /**
   * Consumes password on success, policy denial, conflict and infrastructure failure.
   * PT-ADM-017/021.
   */
  public UserMutationResult resetPassword(
      Connection c,
      AuthenticatedActor actor,
      UserId id,
      char[] password,
      long expectedVersion,
      UserCommandMetadata metadata) {
    Objects.requireNonNull(password, "password");
    try {
      return update(
          c,
          actor,
          id,
          expectedVersion,
          Update.RESET_PASSWORD,
          metadata,
          before -> {
            char[] normalized = policy.normalizeForCreation(password, before.username());
            String hash = encode(normalized);
            return new Values(before.role(), before.enabled(), Optional.of(hash));
          });
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  /** PT-ADM-018: absent/expired lock is 0200 with unchanged version and no session revocation. */
  public UserMutationResult unlock(
      Connection c,
      AuthenticatedActor actor,
      UserId id,
      long expectedVersion,
      UserCommandMetadata metadata) {
    return update(
        c,
        actor,
        id,
        expectedVersion,
        Update.UNLOCK,
        metadata,
        before -> new Values(before.role(), before.enabled(), Optional.empty()));
  }

  private UserMutationResult update(
      Connection c,
      AuthenticatedActor actor,
      UserId id,
      long expectedVersion,
      Update kind,
      UserCommandMetadata metadata,
      ValueOperation values) {
    Objects.requireNonNull(id, "id");
    if (expectedVersion < 0 || expectedVersion > 999_999_999)
      throw new IllegalArgumentException("expected version is outside N9");
    return execute(
        c,
        actor,
        Mutation.valueOf(kind.name()),
        metadata,
        () -> {
          Optional<State> stored = read(c, id);
          if (stored.isEmpty()) return rejected(ResultCode.NOT_FOUND, Optional.of(id), stored);
          State before = stored.orElseThrow();
          if (before.version() != expectedVersion)
            return rejected(ResultCode.CONFLICT, Optional.of(id), stored);
          if ((kind == Update.DISABLE || kind == Update.DEMOTE) && id.value() == actor.userId())
            return rejected(ResultCode.CONFLICT, Optional.of(id), stored);
          if (kind == Update.UNLOCK
              && !before.lockedUntil().map(time -> time.isAfter(metadata.at())).orElse(false))
            return accepted(stored, before, ResultCode.IDEMPOTENT_SUCCESS);
          if (before.version() == MAXIMUM_USER_VERSION)
            return rejected(ResultCode.RESOURCE_LIMIT, Optional.of(id), stored);
          Values next;
          try {
            next = values.make(before);
          } catch (IllegalArgumentException invalid) {
            TemporaryInfrastructureException.preserveFatal(invalid);
            return rejected(ResultCode.VALIDATION_ERROR, Optional.of(id), stored);
          }
          if (before.role() == UserRole.ADMIN
              && before.enabled()
              && (!next.enabled() || next.role() != UserRole.ADMIN)
              && activeAdmins(c) <= 1)
            return rejected(ResultCode.CONFLICT, Optional.of(id), stored);
          int changed;
          // BUG-047: whole statements are fixed literals; all external values remain bind-only.
          try (var s =
              switch (kind) {
                case ENABLE, DISABLE ->
                    c.prepareStatement(
                        "update schubert.app_users set status=?,version=version+1,updated_at=?,updated_by=? where id=? and version=?");
                case PROMOTE, DEMOTE ->
                    c.prepareStatement(
                        "update schubert.app_users set role=?,version=version+1,updated_at=?,updated_by=? where id=? and version=?");
                case RESET_PASSWORD ->
                    c.prepareStatement(
                        "update schubert.app_users set password_hash=?,password_changed_at=?,version=version+1,updated_at=?,updated_by=? where id=? and version=?");
                case UNLOCK ->
                    c.prepareStatement(
                        "update schubert.app_users set failed_count=0,failure_window_started_at=null,locked_until=null,version=version+1,updated_at=?,updated_by=? where id=? and version=?");
              }) {
            int p = 1;
            switch (kind) {
              case ENABLE, DISABLE -> {
                s.setString(p, next.enabled() ? LITERAL_ACTIVE : "DISABLED");
                p++;
              }
              case PROMOTE, DEMOTE -> {
                s.setString(p, next.role().wireValue());
                p++;
              }
              case RESET_PASSWORD -> {
                s.setString(p, next.hash().orElseThrow());
                p++;
                s.setObject(p, metadata.at().atOffset(java.time.ZoneOffset.UTC));
                p++;
              }
              case UNLOCK -> {}
            }
            s.setObject(p, metadata.at().atOffset(java.time.ZoneOffset.UTC));
            p++;
            s.setLong(p, actor.userId());
            p++;
            s.setLong(p, id.value());
            p++;
            s.setLong(p, expectedVersion);
            changed = s.executeUpdate();
          }
          if (changed == 0) {
            Optional<State> current = read(c, id);
            if (current.isEmpty()) return rejected(ResultCode.NOT_FOUND, Optional.of(id), stored);
            if (current.orElseThrow().version() != expectedVersion)
              return rejected(ResultCode.CONFLICT, Optional.of(id), stored);
            throw new SQLException("locked user was not updated");
          }
          require(changed == 1);
          if (kind != Update.UNLOCK) {
            SessionRevocationReason reason =
                kind == Update.DISABLE
                    ? SessionRevocationReason.DISABLED
                    : kind == Update.RESET_PASSWORD
                        ? SessionRevocationReason.PASSWORD_RESET
                        : SessionRevocationReason.ADMIN;
            revocations.revokeAll(
                c,
                actor,
                id.value(),
                reason,
                Optional.empty(),
                metadata.messageId(),
                metadata.correlationId(),
                metadata.at());
          }
          if ((kind == Update.DISABLE || kind == Update.DEMOTE) && activeAdmins(c) < 1)
            throw new SQLException("active administrator invariant failed");
          State after = read(c, id).orElseThrow(() -> new SQLException("updated user is missing"));
          require(after.version() == expectedVersion + 1);
          return accepted(stored, after, ResultCode.SUCCESS);
        });
  }

  private UserMutationResult execute(
      Connection c,
      AuthenticatedActor actor,
      Mutation kind,
      UserCommandMetadata metadata,
      Operation operation) {
    Objects.requireNonNull(c, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(metadata, "metadata");
    new AuthorizationService().requireAdmin(actor);
    try {
      require(!c.getAutoCommit() && !c.isReadOnly());
      Change change = operation.run();
      audit.write(c, actor, kind, change, metadata);
      return change.result();
    } catch (SQLException
        | IllegalArgumentException
        | IllegalStateException
        | ArithmeticException
        | java.time.DateTimeException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      // BUG-045: DB typed-value and clock conversion failures are not input-policy denials.
      throw new TemporaryInfrastructureException();
    }
  }

  private static Optional<State> read(Connection c, UserId id) throws SQLException {
    try (var s =
        c.prepareStatement(
            "select id,username,role,status,version,locked_until,failed_count from schubert.app_users where id=? for update")) {
      s.setLong(1, id.value());
      try (var r = s.executeQuery()) {
        Optional<State> value = Optional.empty();
        if (r.next()) {
          String status = text(r, "status");
          require(status.equals(LITERAL_ACTIVE) || status.equals("DISABLED"));
          long version = number(r, "version");
          long failed = number(r, "failed_count");
          require(version >= 0 && version <= 999_999_999 && failed >= 0 && failed <= 5);
          java.time.OffsetDateTime locked =
              r.getObject("locked_until", java.time.OffsetDateTime.class);
          value =
              Optional.of(
                  new State(
                      new UserId(number(r, "id")),
                      text(r, "username"),
                      UserRole.valueOf(text(r, "role")),
                      status.equals(LITERAL_ACTIVE),
                      version,
                      locked == null ? Optional.empty() : Optional.of(locked.toInstant()),
                      Math.toIntExact(failed)));
          require(value.orElseThrow().id().equals(id));
          require(!r.next());
        }
        return value;
      }
    } catch (IllegalArgumentException invalid) {
      TemporaryInfrastructureException.preserveFatal(invalid);
      throw new SQLException("stored user is invalid");
    }
  }

  private String encode(char[] normalized) throws SQLException {
    try {
      String hash = passwords.encode(normalized);
      require(hash != null && hash.matches("\\{pbkdf2-v1}[0-9a-f]{96}"));
      return hash;
    } catch (IllegalArgumentException failure) {
      TemporaryInfrastructureException.preserveFatal(failure);
      throw new SQLException("password encoding is unavailable");
    } finally {
      Arrays.fill(normalized, '\0');
    }
  }

  private static long activeAdmins(Connection c) throws SQLException {
    try (var s =
            c.prepareStatement(
                "select count(*) as count from schubert.app_users where role='ADMIN' and status='ACTIVE'");
        var r = s.executeQuery()) {
      require(r.next());
      long count = number(r, "count");
      require(count >= 0);
      require(!r.next());
      return count;
    }
  }

  private static Change accepted(Optional<State> before, State after, ResultCode code) {
    return new Change(
        UserMutationResult.accepted(after.id(), after.version(), code),
        before,
        Optional.of(after),
        Optional.of(after.id()));
  }

  private static Change rejected(ResultCode code, Optional<UserId> target, Optional<State> before) {
    return new Change(UserMutationResult.rejected(code), before, before, target);
  }

  private static long number(ResultSet r, String name) throws SQLException {
    long value = r.getLong(name);
    require(!r.wasNull());
    return value;
  }

  private static String text(ResultSet r, String name) throws SQLException {
    String value = r.getString(name);
    if (value == null) throw new SQLException("required user value is missing");
    return value;
  }

  private static void require(boolean valid) throws SQLException {
    if (!valid) throw new SQLException("user command invariant failed");
  }

  @FunctionalInterface
  private interface Operation {
    Change run() throws SQLException;
  }

  @FunctionalInterface
  private interface ValueOperation {
    Values make(State state) throws SQLException;
  }

  record State(
      UserId id,
      String username,
      UserRole role,
      boolean enabled,
      long version,
      Optional<Instant> lockedUntil,
      int failedCount) {}

  record Change(
      UserMutationResult result,
      Optional<State> before,
      Optional<State> after,
      Optional<UserId> target) {}

  private record Values(UserRole role, boolean enabled, Optional<String> hash) {}
}
