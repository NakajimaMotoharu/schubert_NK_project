package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.protocol.layout.auth.LoginRequestData;
import dev.codex.schubert.nk.protocol.layout.auth.LoginResponseData;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyException;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import java.net.InetAddress;
import java.nio.CharBuffer;
import java.text.Normalizer;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * One Login exchange; no retry, password comparison, business DB or HTTP/session mutation.
 * NK-WEB-001; FUN-001/AUT-001..004/MQ-004; UI226/232/234; SS312/314/321..323/352;
 * PG-D-101/PT-WEB-054..059. Reply transport is already checked by JmsReplyDecoder.
 */
public final class MqLoginClient {
  private static final LayoutId REQUEST = new LayoutId("LGNREQ01");
  private static final LayoutId RESPONSE = new LayoutId("LGNRSP01");
  private static final Set<ResultCode> ALLOWED =
      Set.of(
          ResultCode.SUCCESS,
          ResultCode.IDEMPOTENT_SUCCESS,
          ResultCode.AUTHENTICATION_FAILED,
          ResultCode.LOCKED,
          ResultCode.TEMPORARY_FAILURE);
  private final JmsRequestReplyClient client;
  private final JmsRequestSender sender;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final Duration timeout;

  /** All dependencies nonnull; timeout 1ns..2s. The UUID supplier must generate fresh IDs. */
  public MqLoginClient(
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.client = Objects.requireNonNull(client, "client");
    this.sender = Objects.requireNonNull(sender, "sender");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
    this.timeout = Objects.requireNonNull(timeout, "timeout");
    if (timeout.isZero()
        || timeout.isNegative()
        || timeout.compareTo(JmsRequestReplyClient.MAXIMUM_WAIT) > 0)
      throw new IllegalArgumentException("login wait must be between 1ns and 2s");
  }

  /**
   * Consumes and erases the nonnull password, including on other argument failures. Address must
   * already come from the trusted Caddy boundary, never directly from arbitrary forwarded headers.
   * Returns only a fully validated reply; input and transport failures remain distinguishable.
   */
  public Reply exchange(String username, char[] password, String clientAddress) {
    Objects.requireNonNull(password, "password");
    try {
      Objects.requireNonNull(username, "username");
      Objects.requireNonNull(clientAddress, "clientAddress");
      String normalized = Normalizer.normalize(username, Normalizer.Form.NFC).trim();
      UUID correlation = Objects.requireNonNull(identifiers.get(), "identifier");
      CommonHeader header =
          new CommonHeader(
              "SCHBNK01",
              1,
              REQUEST,
              1,
              MessageKind.REQUEST,
              InteractionKind.SYNCHRONOUS,
              correlation,
              correlation,
              clock.instant().truncatedTo(ChronoUnit.MILLIS),
              Optional.empty(),
              256,
              384,
              0,
              0,
              640,
              Optional.empty());
      byte[] request = encodeRequest(header, normalized, password, clientAddress);
      try {
        byte[] reply =
            client.exchange(
                correlation,
                request,
                timeout,
                (id, bytes) -> {
                  try {
                    sender.send(id, bytes);
                  } finally {
                    Arrays.fill(bytes, (byte) 0);
                  }
                });
        try {
          return decodeReply(reply, correlation, normalized);
        } finally {
          Arrays.fill(reply, (byte) 0);
        }
      } finally {
        Arrays.fill(request, (byte) 0);
      }
    } catch (JMSException
        | JMSRuntimeException
        | JmsRequestReplyException
        | PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException
        | DateTimeException exception) {
      // BUG2834: retain fatal graph identity; existing finally still wipes every owned buffer.
      JmsRequestReplyException.preserveFatal(exception);
      throw new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);
    } finally {
      Arrays.fill(password, '\0');
    }
  }

  private static byte[] encodeRequest(
      CommonHeader header, String username, char[] password, String address) {
    try {
      // ofLiteral never performs DNS; preserve the trusted text rather than invent another IP.
      // BUG-062: the DB inet/LoginInbox contract excludes scoped IPv6, even when JDK parses it.
      if (InetAddress.ofLiteral(address).getHostAddress().contains("%"))
        throw new IllegalArgumentException("login IP scope is invalid");
      String normalized = Normalizer.normalize(CharBuffer.wrap(password), Normalizer.Form.NFC);
      PayloadValues values =
          PayloadTypeCatalog.encode(
              new TypedPayloadValues(
                  REQUEST, new LoginRequestData(username, normalized, address), List.of()));
      return FixedWidthEncoder.standard()
          .encode(new WireMessage<>(header, PayloadCodec.standard().encode(values, false)));
    } catch (IllegalArgumentException exception) {
      throw new MqLoginExchangeException(MqLoginExchangeException.Reason.INVALID_INPUT);
    }
  }

  private static Reply decodeReply(byte[] reply, UUID correlation, String username) {
    CommonHeader header = HeaderCodec.standard().peek(reply);
    if (!header.layoutId().equals(RESPONSE)
        || reply.length != 688
        || !header.correlationId().equals(correlation))
      throw new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);
    ResultCode code = header.resultCode().orElseThrow();
    if (!ALLOWED.contains(code))
      throw new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);
    byte[] data = Arrays.copyOfRange(reply, 256, 688);
    try {
      PayloadValues values = PayloadCodec.standard().decode(RESPONSE, data, List.of(), code);
      LoginResponseData decoded;
      if (code.usesSuccessProfile()) {
        // This catalog has a success-only semantic profile; never invoke it for error fillers.
        PayloadTypeCatalog.decode(values);
        decoded = LoginResponseData.from(values.data());
      } else {
        // BUG-060/YKT-055: validated error fillers are Unset, not missing required success data.
        // Zero is mandated by this error profile, not a general null-to-zero conversion.
        decoded =
            new LoginResponseData(
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                Optional.empty(),
                code == ResultCode.LOCKED
                    ? TypedFieldValues.requiredInt(values.data(), "Retry after秒")
                    : 0,
                0,
                TypedFieldValues.optionalString(values.data(), "利用者message"));
      }
      if (code.usesSuccessProfile()
          && !decoded
              .username()
              .orElseThrow()
              .toLowerCase(Locale.ROOT)
              .equals(username.toLowerCase(Locale.ROOT)))
        throw new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);
      return new Reply(code, decoded);
    } finally {
      Arrays.fill(data, (byte) 0);
    }
  }

  /**
   * Internal-only validated projection, not an authentication grant. In particular, 0200 retains
   * the original snapshot; SS324 §6.1 requires current context validation before granting a Web
   * session. Never expose its context to HTML or logs. BUG-061/YKT-056/PT-WEB-054/057.
   */
  public static final class Reply {
    private final ResultCode retainedCode;
    private final LoginResponseData retainedData;

    private Reply(ResultCode code, LoginResponseData data) {
      this.retainedCode = code;
      this.retainedData = data;
    }

    public ResultCode code() {
      return retainedCode;
    }

    public LoginResponseData data() {
      return retainedData;
    }

    @Override
    public String toString() {
      return "LoginReply[REDACTED]";
    }
  }
}
