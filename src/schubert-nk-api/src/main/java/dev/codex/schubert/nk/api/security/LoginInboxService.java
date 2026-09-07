package dev.codex.schubert.nk.api.security;

import dev.codex.schubert.nk.api.idempotency.CanonicalField;
import dev.codex.schubert.nk.api.idempotency.CanonicalRequest;
import dev.codex.schubert.nk.api.idempotency.InboxException;
import dev.codex.schubert.nk.api.idempotency.InboxExecutionStatus;
import dev.codex.schubert.nk.api.idempotency.InboxRequest;
import dev.codex.schubert.nk.api.idempotency.JdbcInboxCoordinator;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.auth.LoginRequestData;
import java.net.InetAddress;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.SQLException;
import java.time.Clock;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Anonymous Login Inbox and application transaction participant. No commits, JMS or HTTP here.
 * NK-AUT-001/NK-MSG-002; AUT-001/MQ-006..010; UI226/234/241; SS312/314/323/324; PG-D-049,
 * PT-AUT-INBOX-001..006. Transport property validation precedes this boundary.
 */
public final class LoginInboxService {
  private static final LayoutId LOGIN = new LayoutId("LGNREQ01");
  private final JdbcInboxCoordinator inbox;
  private final AuthenticationService authentication;
  private final LoginReplayService responses;
  private final Clock clock;
  private final Supplier<UUID> responseIds;

  public LoginInboxService(
      JdbcInboxCoordinator inbox,
      AuthenticationService authentication,
      LoginReplayService responses,
      Clock clock) {
    this(inbox, authentication, responses, clock, UUID::randomUUID);
  }

  LoginInboxService(
      JdbcInboxCoordinator inbox,
      AuthenticationService authentication,
      LoginReplayService responses,
      Clock clock,
      Supplier<UUID> responseIds) {
    this.inbox = Objects.requireNonNull(inbox, "inbox");
    this.authentication = Objects.requireNonNull(authentication, "authentication");
    this.responses = Objects.requireNonNull(responses, "responses");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.responseIds = Objects.requireNonNull(responseIds, "responseIds");
  }

  /** Caller commits returned success/business error or rolls back any exception before replying. */
  public byte[] execute(
      Connection connection, WireMessage<FixedPayload> request, Instant receivedAt) {
    Objects.requireNonNull(connection, "connection");
    Objects.requireNonNull(request, "request");
    Objects.requireNonNull(receivedAt, "receivedAt");
    LoginRequestData data = decode(request);
    LoginUsername name;
    InetAddress client;
    char[] password;
    try {
      name = new LoginUsername(data.username());
      if (data.clientAddress().contains("%")) throw new IllegalArgumentException("scoped IP");
      client = InetAddress.ofLiteral(data.clientAddress());
      password = new PasswordPolicy().normalizeForLogin(data.password().toCharArray());
    } catch (IllegalArgumentException invalid) {
      throw new PermanentProtocolException("login request fields are invalid");
    }
    try (var canonical = canonical(name, password, client)) {
      UUID message = request.header().messageId();
      UUID response = Objects.requireNonNull(responseIds.get(), "response ID");
      Instant received = receivedAt.truncatedTo(ChronoUnit.MICROS);
      // Login updates counters/session/audit: seven-day update retention, despite having no token.
      var identity =
          new InboxRequest(
              message,
              request.header().correlationId(),
              OptionalLong.empty(),
              Optional.empty(),
              canonical,
              received,
              received.plusSeconds(604800));
      var execution =
          inbox.execute(
              connection,
              identity,
              transaction -> {
                LoginResult result =
                    authentication.authenticate(
                        transaction,
                        name.value(),
                        password,
                        client,
                        message,
                        request.header().correlationId(),
                        clock.instant());
                return responses.capture(result, message, response, clock.instant());
              });
      if (execution.status() == InboxExecutionStatus.IN_PROGRESS) {
        return responses.temporaryFailure(message, response, clock.instant());
      }
      return responses.restore(
          connection,
          execution.completion().orElseThrow(),
          message,
          response,
          clock.instant(),
          execution.status() == InboxExecutionStatus.REPLAY);
    } catch (InboxException failure) {
      if (failure.reason() == InboxException.Reason.MESSAGE_ID_REUSE) {
        throw new PermanentProtocolException(
            "login request identity differs from its saved request");
      }
      throw new AuthenticationInfrastructureException();
    } catch (SQLException | IllegalStateException failure) {
      throw new AuthenticationInfrastructureException();
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  private static LoginRequestData decode(WireMessage<FixedPayload> request) {
    try {
      request.header().validateAgainst(LayoutRegistry.standard().require(LOGIN, 1));
      byte[] data = request.payload().copyData();
      try {
        return (LoginRequestData)
            PayloadTypeCatalog.decode(PayloadCodec.standard().decode(LOGIN, data, List.of(), false))
                .data();
      } finally {
        Arrays.fill(data, (byte) 0);
      }
    } catch (PermanentProtocolException | IllegalArgumentException invalid) {
      throw new PermanentProtocolException("login request payload is invalid");
    }
  }

  /**
   * Caller-owned canonical fields; no cleartext is persisted. Close after all Inbox comparisons.
   */
  static CanonicalRequest canonical(LoginUsername name, char[] password, InetAddress client) {
    return new CanonicalRequest(
        "ANONYMOUS",
        "LGNREQ01",
        "001",
        "LOGIN:" + name.key() + ":" + client.getHostAddress(),
        List.of(
            field("username", name.value()),
            field("password", new String(password)),
            field("clientAddress", client.getHostAddress())));
  }

  private static CanonicalField field(String name, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    try {
      return new CanonicalField(name, "X1", bytes);
    } finally {
      Arrays.fill(bytes, (byte) 0);
    }
  }
}
