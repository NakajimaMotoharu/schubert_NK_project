package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.codec.*;
import dev.codex.schubert.nk.protocol.header.*;
import dev.codex.schubert.nk.protocol.layout.*;
import dev.codex.schubert.nk.web.messaging.ScenarioWireException.Reason;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.function.Supplier;

/**
 * Six protected Scenario reads only. Upstream JMS ACL/property/correlation validation is still
 * mandatory; downstream facade owns request-specific binding, file verification and safe views.
 * NK-WEB-001/NK-SCN-001; FUN-003..005/MQ-003..010/AUT/TST; UI221/223/231/232/234/237;
 * SS311/312/313/321/322/323/333/352; PG-D-118/PT-WEB-166..173.
 */
public final class ScenarioWireClient {
  private static final Set<String> REQUESTS =
      Set.of("GAMREQ01", "SPKREQ01", "SRCREQ01", "RTEREQ01", "SCFREQ01", "SCNREQ01");
  private final JmsRequestReplyClient client;
  private final JmsRequestSender sender;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final Duration timeout;

  public ScenarioWireClient(
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
      throw new IllegalArgumentException("scenario wait must be between 1ns and 2s");
  }

  /**
   * No HTTP request/session, raw credentials, retries or DB calls. Null is a caller contract error.
   */
  public Result exchange(TypedPayloadValues input, AuthenticationContext context) {
    Objects.requireNonNull(input, "input");
    Objects.requireNonNull(context, "context");
    FixedPayload payload = requestPayload(input);
    try {
      var layout = LayoutRegistry.standard().require(input.layoutId(), 1);
      UUID id = Objects.requireNonNull(identifiers.get(), "identifier");
      var header =
          new CommonHeader(
              "SCHBNK01",
              1,
              input.layoutId(),
              1,
              MessageKind.REQUEST,
              InteractionKind.SYNCHRONOUS,
              id,
              id,
              Objects.requireNonNull(clock.instant(), "instant").truncatedTo(ChronoUnit.MILLIS),
              Optional.of(context),
              256,
              layout.dataLength(),
              0,
              0,
              256 + layout.dataLength(),
              Optional.empty());
      byte[] request = FixedWidthEncoder.standard().encode(new WireMessage<>(header, payload));
      try {
        byte[] response =
            client.exchange(
                id,
                request,
                timeout,
                (correlation, bytes) -> {
                  try {
                    sender.send(correlation, bytes);
                  } finally {
                    Arrays.fill(bytes, (byte) 0);
                  }
                });
        try {
          return decode(
              new LayoutId(input.layoutId().value().replace("REQ", "RSP")), response, id, context);
        } finally {
          Arrays.fill(response, (byte) 0);
        }
      } finally {
        Arrays.fill(request, (byte) 0);
      }
    } catch (JMSException
        | JMSRuntimeException
        | JmsRequestReplyException
        | IllegalArgumentException
        | IllegalStateException
        | DateTimeException failure) {
      throw new ScenarioWireException(Reason.UNAVAILABLE);
    }
  }

  private static FixedPayload requestPayload(TypedPayloadValues input) {
    try {
      if (!REQUESTS.contains(input.layoutId().value()) || !input.records().isEmpty())
        throw new IllegalArgumentException();
      return PayloadCodec.standard().encode(PayloadTypeCatalog.encode(input), false);
    } catch (IllegalArgumentException | PermanentProtocolException failure) {
      throw new ScenarioWireException(Reason.INVALID_INPUT);
    }
  }

  private static Result decode(
      LayoutId expected, byte[] response, UUID correlation, AuthenticationContext context) {
    var definition = LayoutRegistry.standard().require(expected, 1);
    if (response.length < 256 + definition.dataLength()
        || response.length > definition.maximumTotalLength())
      throw new ScenarioWireException(Reason.INVALID_RESPONSE);
    try {
      var header = HeaderCodec.standard().peek(response);
      if (!header.layoutId().equals(expected)
          || header.totalLength() != response.length
          || !header.correlationId().equals(correlation)
          || !sameContext(header.authenticationContext().orElseThrow(), context))
        throw new ScenarioWireException(Reason.INVALID_RESPONSE);
      ResultCode code = header.resultCode().orElseThrow();
      int offset = 256 + header.dataLength();
      byte[] data = Arrays.copyOfRange(response, 256, offset);
      var records = new ArrayList<byte[]>();
      try {
        for (int index = 0; index < header.recordCount(); index++) {
          records.add(Arrays.copyOfRange(response, offset, offset + header.recordLength()));
          offset += header.recordLength();
        }
        var values = PayloadCodec.standard().decode(expected, data, records, code);
        return new Result(
            code,
            code.usesSuccessProfile()
                ? Optional.of(PayloadTypeCatalog.decode(values))
                : Optional.empty());
      } finally {
        Arrays.fill(data, (byte) 0);
        records.forEach(bytes -> Arrays.fill(bytes, (byte) 0));
      }
    } catch (PermanentProtocolException
        | IllegalArgumentException
        | IllegalStateException failure) {
      throw new ScenarioWireException(Reason.INVALID_RESPONSE);
    }
  }

  private static boolean sameContext(AuthenticationContext left, AuthenticationContext right) {
    byte[] first = left.wireValue().getBytes(StandardCharsets.US_ASCII);
    byte[] second = right.wireValue().getBytes(StandardCharsets.US_ASCII);
    try {
      return MessageDigest.isEqual(first, second);
    } finally {
      Arrays.fill(first, (byte) 0);
      Arrays.fill(second, (byte) 0);
    }
  }

  /** Safe internal value projection, not an HTML model and not a session grant. */
  public static final class Result {
    private final ResultCode code;
    private final Optional<TypedPayloadValues> payload;

    private Result(ResultCode code, Optional<TypedPayloadValues> payload) {
      this.code = code;
      this.payload = payload;
    }

    public ResultCode resultCode() {
      return code;
    }

    public Optional<TypedPayloadValues> payload() {
      return payload;
    }

    @Override
    public String toString() {
      return "ScenarioResponse[REDACTED]";
    }
  }
}
