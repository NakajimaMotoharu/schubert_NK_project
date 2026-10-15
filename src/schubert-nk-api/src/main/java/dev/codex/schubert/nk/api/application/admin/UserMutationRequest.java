package dev.codex.schubert.nk.api.application.admin;

import static dev.codex.schubert.nk.api.idempotency.CanonicalField.number;
import static dev.codex.schubert.nk.api.idempotency.CanonicalField.text;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.security.AdminCommandAuthenticator.Mutation;
import dev.codex.schubert.nk.api.security.AuthenticatedActor;
import dev.codex.schubert.nk.api.security.LoginUsername;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.admin.PasswordResetRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserCreateRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserRoleRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserStatusRequestData;
import dev.codex.schubert.nk.protocol.layout.admin.UserUnlockRequestData;
import dev.codex.schubert.nk.protocol.layout.semantic.UserId;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import java.sql.Connection;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;

/**
 * One caller-confined mutation request scope; never an authentication or Inbox NEW grant.
 * NK-ADM-001; FUN-009/MQ-006..010/AUT-002/003; UI236/241; SS312/323 §9.3/324/332/352;
 * SSC-032/PG-D-084; PT-ADM-024..027. Caller closes request and each returned canonical separately.
 */
public final class UserMutationRequest implements AutoCloseable {
  private final CommonHeader retainedHeader;
  private final Mutation retainedMutation;
  private final Optional<String> username;
  private final Optional<UserId> target;
  private final Optional<UserRole> creationRole;
  private final boolean creationEnabled;
  private final long retainedExpectedVersion;
  private final UUID retainedOperationToken;
  private final char[] password;
  private boolean closed;

  private UserMutationRequest(
      CommonHeader header,
      Mutation mutation,
      Optional<String> username,
      Optional<UserId> target,
      Optional<UserRole> creationRole,
      boolean creationEnabled,
      long expectedVersion,
      UUID operationToken,
      String password) {
    this.retainedHeader = header;
    this.retainedMutation = mutation;
    this.username = username;
    this.target = target;
    this.creationRole = creationRole;
    this.creationEnabled = creationEnabled;
    this.retainedExpectedVersion = expectedVersion;
    this.retainedOperationToken = operationToken;
    this.password = password.toCharArray();
  }

  /** Strict wire decoding before any database access. PT-ADM-024/026. */
  public static UserMutationRequest decode(WireMessage<FixedPayload> request) {
    Objects.requireNonNull(request, "request");
    byte[] bytes = request.payload().copyData();
    try {
      var header = request.header();
      header.validateAgainst(LayoutRegistry.standard().require(header.layoutId(), 1));
      var data =
          PayloadTypeCatalog.decode(
                  PayloadCodec.standard().decode(header.layoutId(), bytes, List.of(), false))
              .data();
      return switch (header.layoutId().value()) {
        case "UCRREQ01" -> {
          var value = (UserCreateRequestData) data;
          yield new UserMutationRequest(
              header,
              Mutation.CREATE,
              Optional.of(value.username()),
              Optional.empty(),
              Optional.of(value.role()),
              value.enabled(),
              0,
              value.operationToken(),
              value.initialPassword());
        }
        case "USTREQ01" -> {
          var value = (UserStatusRequestData) data;
          yield new UserMutationRequest(
              header,
              value.enabled() ? Mutation.ENABLE : Mutation.DISABLE,
              Optional.empty(),
              Optional.of(value.userId()),
              Optional.empty(),
              false,
              value.expectedVersion(),
              value.operationToken(),
              "");
        }
        case "URLREQ01" -> {
          var value = (UserRoleRequestData) data;
          yield new UserMutationRequest(
              header,
              value.newRole() == UserRole.ADMIN ? Mutation.PROMOTE : Mutation.DEMOTE,
              Optional.empty(),
              Optional.of(value.userId()),
              Optional.empty(),
              false,
              value.expectedVersion(),
              value.operationToken(),
              "");
        }
        case "UPWREQ01" -> {
          var value = (PasswordResetRequestData) data;
          yield new UserMutationRequest(
              header,
              Mutation.RESET_PASSWORD,
              Optional.empty(),
              Optional.of(value.userId()),
              Optional.empty(),
              false,
              value.expectedVersion(),
              value.operationToken(),
              value.newPassword());
        }
        case "ULKREQ01" -> {
          var value = (UserUnlockRequestData) data;
          yield new UserMutationRequest(
              header,
              Mutation.UNLOCK,
              Optional.empty(),
              Optional.of(value.userId()),
              Optional.empty(),
              false,
              value.expectedVersion(),
              value.operationToken(),
              "");
        }
        default -> throw new PermanentProtocolException("unsupported user mutation request");
      };
    } catch (PermanentProtocolException | IllegalArgumentException invalid) {
      throw new PermanentProtocolException("user mutation request is invalid");
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }

  /** Trace metadata only, not proof of current authentication. PT-ADM-024/026. */
  public CommonHeader header() {
    ensureOpen();
    return retainedHeader;
  }

  /** Prelude uses this exact decoded operation. PT-ADM-024/025/026. */
  public Mutation mutation() {
    ensureOpen();
    return retainedMutation;
  }

  /** CREATE has no target before INSERT. PT-ADM-024/025/026. */
  public OptionalLong targetUserId() {
    ensureOpen();
    return target.isEmpty() ? OptionalLong.empty() : OptionalLong.of(target.orElseThrow().value());
  }

  /** Separate Inbox key; excluded from canonical bytes. PT-ADM-024/026. */
  public UUID operationToken() {
    ensureOpen();
    return retainedOperationToken;
  }

  /** Frozen result verification only; not a current DB version. PG-D-086/PT-ADM-028/031. */
  long expectedVersion() {
    ensureOpen();
    return retainedExpectedVersion;
  }

  /** Response layout mapping is fixed by the approved request layout. PT-ADM-024/026. */
  public LayoutId responseLayoutId() {
    ensureOpen();
    return new LayoutId(retainedHeader.layoutId().value().replace("REQ", "RSP"));
  }

  /** Caller owns returned field buffers until all current/previous-key comparisons finish. */
  public CanonicalRequest canonical(AuthenticatedActor actor) {
    ensureOpen();
    Objects.requireNonNull(actor, "actor");
    String scope =
        retainedMutation == Mutation.CREATE
            ? "NEW_USER:" + new LoginUsername(username.orElseThrow()).key()
            : "USER:" + target.orElseThrow().value();
    List<CanonicalField> fields =
        switch (retainedMutation) {
          case CREATE ->
              List.of(
                  text("username", username.orElseThrow()),
                  text("usernameKey", new LoginUsername(username.orElseThrow()).key()),
                  text("password", new String(password)),
                  text("role", creationRole.orElseThrow().wireValue()),
                  flag(creationEnabled));
          case ENABLE, DISABLE ->
              List.of(
                  flag(retainedMutation == Mutation.ENABLE),
                  number("expectedVersion", retainedExpectedVersion));
          case PROMOTE, DEMOTE ->
              List.of(
                  text("role", retainedMutation == Mutation.PROMOTE ? "ADMIN" : "USER"),
                  number("expectedVersion", retainedExpectedVersion));
          case RESET_PASSWORD ->
              List.of(
                  text("password", new String(password)),
                  number("expectedVersion", retainedExpectedVersion));
          case UNLOCK -> List.of(number("expectedVersion", retainedExpectedVersion));
        };
    return new CanonicalRequest(
        Long.toString(actor.userId()), retainedHeader.layoutId().value(), "001", scope, fields);
  }

  /** Current ADMIN/prelude and Inbox NEW must precede this caller-owned write transaction. */
  public UserMutationResult apply(
      UserCommandService commands,
      Connection connection,
      AuthenticatedActor actor,
      UserCommandMetadata metadata) {
    ensureOpen();
    Objects.requireNonNull(commands, "commands");
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(actor, "actor");
    Objects.requireNonNull(metadata, "metadata");
    return switch (retainedMutation) {
      case CREATE ->
          commands.create(
              connection,
              actor,
              username.orElseThrow(),
              password.clone(),
              creationRole.orElseThrow(),
              creationEnabled,
              metadata);
      case ENABLE, DISABLE ->
          commands.changeStatus(
              connection,
              actor,
              target.orElseThrow(),
              retainedMutation == Mutation.ENABLE,
              retainedExpectedVersion,
              metadata);
      case PROMOTE, DEMOTE ->
          commands.changeRole(
              connection,
              actor,
              target.orElseThrow(),
              retainedMutation == Mutation.PROMOTE ? UserRole.ADMIN : UserRole.USER,
              retainedExpectedVersion,
              metadata);
      case RESET_PASSWORD ->
          commands.resetPassword(
              connection,
              actor,
              target.orElseThrow(),
              password.clone(),
              retainedExpectedVersion,
              metadata);
      case UNLOCK ->
          commands.unlock(
              connection, actor, target.orElseThrow(), retainedExpectedVersion, metadata);
    };
  }

  private static CanonicalField flag(boolean enabled) {
    byte[] value = {(byte) (enabled ? '1' : '0')};
    try {
      return new CanonicalField("enabled", "B1", value);
    } finally {
      Arrays.fill(value, (byte) 0);
    }
  }

  private void ensureOpen() {
    if (closed) throw new IllegalStateException("user mutation request is closed");
  }

  /** Terminal and idempotent; caller must not race close against use of this request scope. */
  @Override
  public void close() {
    Arrays.fill(password, '\0');
    closed = true;
  }

  @Override
  public String toString() {
    return "UserMutationRequest[REDACTED]";
  }
}
