package dev.codex.schubert.nk.web.security;

import dev.codex.schubert.nk.protocol.codec.HeaderCodec;
import dev.codex.schubert.nk.protocol.codec.PayloadCodec;
import dev.codex.schubert.nk.protocol.codec.PermanentProtocolException;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.PayloadTypeCatalog;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyException;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import jakarta.jms.JMSException;
import jakarta.jms.JMSRuntimeException;
import java.time.Clock;
import java.time.DateTimeException;
import java.time.Duration;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Fresh protected IF-003 read checks current context before granting a replayed Login snapshot.
 * Discards all game data, never retries Login or writes an HTTP session. NK-WEB-001;
 * FUN-001/AUT-001..004/MQ-004; UI226/232/234; SS314 §3.1/324 §6.1; SSC-043/PG-D-102;
 * PT-WEB-060..062/065/067. Every subsequent business request must still reauthenticate in API.
 */
public final class MqLoginContextProbe {
  private static final LayoutId REQUEST = new LayoutId("GAMREQ01");
  private static final LayoutId RESPONSE = new LayoutId("GAMRSP01");
  private final JmsRequestReplyClient client;
  private final JmsRequestSender sender;
  private final Clock clock;
  private final Supplier<UUID> identifiers;
  private final Duration timeout;

  /** All nonnull. IDs must be fresh, timeout 1ns..2s, shared client enforces at most12 waits. */
  public MqLoginContextProbe(
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
      throw new IllegalArgumentException("login probe wait must be between 1ns and 2s");
  }

  /** Nonnull context. Only a fully validated0102 returns false; faults throw fixed UNAVAILABLE. */
  public boolean isActive(AuthenticationContext context) {
    Objects.requireNonNull(context, "context");
    try {
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
              Optional.of(context),
              256,
              0,
              0,
              0,
              256,
              Optional.empty());
      byte[] request = HeaderCodec.standard().encode(header);
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
          return decode(reply, correlation, context);
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
        | DateTimeException failure) {
      JmsRequestReplyException.preserveFatal(failure);
      throw unavailable();
    }
  }

  private static boolean decode(byte[] reply, UUID correlation, AuthenticationContext context) {
    CommonHeader header = HeaderCodec.standard().peek(reply);
    if (!header.layoutId().equals(RESPONSE)
        || reply.length != header.totalLength()
        || !header.correlationId().equals(correlation)
        || !header.authenticationContext().orElseThrow().equals(context)) throw unavailable();
    ResultCode code = header.resultCode().orElseThrow();
    byte[] data = Arrays.copyOfRange(reply, 256, 265);
    ArrayList<byte[]> records = new ArrayList<>();
    try {
      for (int index = 0; index < header.recordCount(); index++)
        records.add(Arrays.copyOfRange(reply, 265 + 272 * index, 265 + 272 * (index + 1)));
      var values = PayloadCodec.standard().decode(RESPONSE, data, records, code);
      if (code.usesSuccessProfile()) {
        PayloadTypeCatalog.decode(values);
        return true;
      }
      if (code == ResultCode.SESSION_INVALID) return false;
      throw unavailable();
    } finally {
      Arrays.fill(data, (byte) 0);
      records.forEach(record -> Arrays.fill(record, (byte) 0));
    }
  }

  private static MqLoginExchangeException unavailable() {
    return new MqLoginExchangeException(MqLoginExchangeException.Reason.UNAVAILABLE);
  }
}
