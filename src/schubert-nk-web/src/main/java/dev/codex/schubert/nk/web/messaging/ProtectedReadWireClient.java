package dev.codex.schubert.nk.web.messaging;

import dev.codex.schubert.nk.protocol.codec.FixedWidthEncoder;
import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.protocol.layout.TypedPayloadValues;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import dev.codex.schubert.nk.web.messaging.ProtectedReadWireException.Reason;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Trusted-facade protected read exchange; JMS ACL/property validation remains upstream.
 * NK-WEB001/NK-SCN001/NK-MED001/FUN004,006/MQ/AUT/UI232,234,235/SS311,312,321,322,323,352;
 * PG206/PT-WEB166..173,238..245. Package construction prevents HTTP-selected capabilities.
 */
public final class ProtectedReadWireClient {
  private final Set<String> requests;
  private final JmsRequestReplyClient client;
  private final JmsRequestSender sender;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final Duration timeout;

  ProtectedReadWireClient(
      Set<String> requestLayouts,
      JmsRequestReplyClient client,
      JmsRequestSender sender,
      Clock clock,
      Supplier<UUID> identifiers,
      Duration timeout) {
    this.requests = Set.copyOf(requestLayouts);
    this.client = Objects.requireNonNull(client, "client");
    this.sender = Objects.requireNonNull(sender, "sender");
    this.clock = Objects.requireNonNull(clock, "clock");
    this.identifiers = Objects.requireNonNull(identifiers, "identifiers");
    this.timeout = Objects.requireNonNull(timeout, "timeout");
    if (timeout.isZero()
        || timeout.isNegative()
        || timeout.compareTo(JmsRequestReplyClient.MAXIMUM_WAIT) > 0)
      throw new IllegalArgumentException("protected read wait must be between 1ns and 2s");
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
              layout.interactionKind(),
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
      JmsRequestReplyException.preserveFatal(failure);
      throw new ProtectedReadWireException(Reason.UNAVAILABLE);
    }
  }

  private FixedPayload requestPayload(TypedPayloadValues input) {
    try {
      if (!requests.contains(input.layoutId().value()) || !input.records().isEmpty())
        throw new IllegalArgumentException();
      return PayloadCodec.standard().encode(PayloadTypeCatalog.encode(input), false);
    } catch (IllegalArgumentException | PermanentProtocolException failure) {
      throw new ProtectedReadWireException(Reason.INVALID_INPUT);
    }
  }

  private static Result decode(
      LayoutId expected, byte[] response, UUID correlation, AuthenticationContext context) {
    var definition = LayoutRegistry.standard().require(expected, 1);
    if (response.length < 256 + definition.dataLength()
        || response.length > definition.maximumTotalLength())
      throw new ProtectedReadWireException(Reason.INVALID_RESPONSE);
    try {
      var header = HeaderCodec.standard().peek(response);
      if (!header.layoutId().equals(expected)
          || header.totalLength() != response.length
          || !header.correlationId().equals(correlation)
          || !sameContext(header.authenticationContext().orElseThrow(), context))
        throw new ProtectedReadWireException(Reason.INVALID_RESPONSE);
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
      throw new ProtectedReadWireException(Reason.INVALID_RESPONSE);
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
    private final Optional<TypedPayloadValues> retainedPayload;

    private Result(ResultCode code, Optional<TypedPayloadValues> payload) {
      this.code = code;
      this.retainedPayload = payload;
    }

    public ResultCode resultCode() {
      return code;
    }

    public Optional<TypedPayloadValues> payload() {
      return retainedPayload;
    }

    @Override
    public String toString() {
      return "ProtectedReadResponse[REDACTED]";
    }
  }
}
