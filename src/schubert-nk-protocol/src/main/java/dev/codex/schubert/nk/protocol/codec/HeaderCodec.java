package dev.codex.schubert.nk.protocol.codec;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.LayoutDefinition;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutRegistry;
import dev.codex.schubert.nk.protocol.time.JstWireTimestamp;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.jspecify.annotations.Nullable;

/** Exact 256-byte header codec. Trace: NK-PRO-002, UI 232 §3, SS 322 §4/§5. */
public final class HeaderCodec {
  private static final int HEADER_LENGTH = 256;
  private static final int RESULT_START = 208;
  private static final int RESERVED_START = 212;

  private final LayoutRegistry registry;

  public HeaderCodec(LayoutRegistry registry) {
    this.registry = Objects.requireNonNull(registry, "registry");
  }

  public static HeaderCodec standard() {
    return new HeaderCodec(LayoutRegistry.standard());
  }

  public byte[] encode(CommonHeader header) {
    Objects.requireNonNull(header, "header");
    try {
      LayoutDefinition definition = registry.require(header.layoutId(), header.layoutVersion());
      header.validateAgainst(definition);
      byte[] encoded = new byte[HEADER_LENGTH];
      put(encoded, 0, FieldCodec.encodeText(header.protocolIdentifier(), 8, true));
      put(encoded, 8, FieldCodec.encodeNumeric(header.headerVersion(), 3, 1, 1));
      put(encoded, 11, FieldCodec.encodeText(header.layoutId().value(), 8, true));
      put(encoded, 19, FieldCodec.encodeNumeric(header.layoutVersion(), 3, 1, 1));
      encoded[22] = (byte) header.messageKind().wireValue();
      encoded[23] = (byte) header.interactionKind().wireValue();
      put(encoded, 24, FieldCodec.encodeText(header.messageId().toString(), 36, true));
      put(encoded, 60, FieldCodec.encodeText(header.correlationId().toString(), 36, true));
      put(
          encoded,
          96,
          JstWireTimestamp.format(header.sentAt()).getBytes(StandardCharsets.US_ASCII));
      put(
          encoded,
          113,
          FieldCodec.encodeText(
              header.authenticationContext().map(AuthenticationContext::wireValue).orElse(null),
              64,
              false));
      put(encoded, 177, FieldCodec.encodeNumeric(header.headerLength(), 4, 256, 256));
      put(encoded, 181, FieldCodec.encodeNumeric(header.dataLength(), 6, 0, 999_999));
      put(encoded, 187, FieldCodec.encodeNumeric(header.recordLength(), 6, 0, 999_999));
      put(encoded, 193, FieldCodec.encodeNumeric(header.recordCount(), 6, 0, 999_999));
      put(encoded, 199, FieldCodec.encodeNumeric(header.totalLength(), 9, 256, 1_000_000));
      put(
          encoded,
          RESULT_START,
          FieldCodec.encodeText(
              header.resultCode().map(ResultCode::wireValue).orElse(null), 4, false));
      Arrays.fill(encoded, RESERVED_START, HEADER_LENGTH, (byte) ' ');
      return encoded;
    } catch (IllegalArgumentException exception) {
      throw new MessageEncodingException("header could not be encoded", exception);
    }
  }

  public CommonHeader peek(byte @Nullable [] body) {
    if (body == null) {
      throw new PermanentProtocolException("message body is null");
    }
    if (body.length < HEADER_LENGTH) {
      throw new PermanentProtocolException("message body is shorter than the common header");
    }
    try {
      String protocol = requiredText(body, 0, 8);
      int headerVersion = numericInt(body, 8, 11, 1, 1);
      LayoutId layoutId = new LayoutId(requiredText(body, 11, 19));
      int layoutVersion = numericInt(body, 19, 22, 1, 1);
      MessageKind messageKind = MessageKind.fromWire(requiredText(body, 22, 23));
      InteractionKind interactionKind = InteractionKind.fromWire(requiredText(body, 23, 24));
      UUID messageId = canonicalUuid(requiredText(body, 24, 60));
      UUID correlationId = canonicalUuid(requiredText(body, 60, 96));
      Instant sentAt = JstWireTimestamp.parse(requiredText(body, 96, 113));
      Optional<AuthenticationContext> authenticationContext =
          FieldCodec.decodeText(slice(body, 113, 177), false).map(AuthenticationContext::of);
      int headerLength = numericInt(body, 177, 181, 256, 256);
      int dataLength = numericInt(body, 181, 187, 0, 999_999);
      int recordLength = numericInt(body, 187, 193, 0, 999_999);
      int recordCount = numericInt(body, 193, 199, 0, 999_999);
      int totalLength = numericInt(body, 199, 208, 256, 1_000_000);
      Optional<ResultCode> resultCode =
          FieldCodec.decodeText(slice(body, RESULT_START, RESERVED_START), false)
              .map(ResultCode::fromWire);
      FieldCodec.requireSpaces(slice(body, RESERVED_START, HEADER_LENGTH));
      CommonHeader header =
          new CommonHeader(
              protocol,
              headerVersion,
              layoutId,
              layoutVersion,
              messageKind,
              interactionKind,
              messageId,
              correlationId,
              sentAt,
              authenticationContext,
              headerLength,
              dataLength,
              recordLength,
              recordCount,
              totalLength,
              resultCode);
      header.validateAgainst(registry.require(layoutId, layoutVersion));
      return header;
    } catch (PermanentProtocolException exception) {
      throw exception;
    } catch (IllegalArgumentException exception) {
      throw new PermanentProtocolException("common header validation failed", exception);
    }
  }

  private static UUID canonicalUuid(String value) {
    UUID uuid = UUID.fromString(value);
    if (!uuid.toString().equals(value)) {
      throw new IllegalArgumentException("UUID is not lowercase canonical form");
    }
    return uuid;
  }

  private static String requiredText(byte[] body, int start, int end) {
    return FieldCodec.decodeText(slice(body, start, end), true).orElseThrow();
  }

  private static int numericInt(byte[] body, int start, int end, int minimum, int maximum) {
    return Math.toIntExact(FieldCodec.decodeNumeric(slice(body, start, end), minimum, maximum));
  }

  private static byte[] slice(byte[] source, int start, int end) {
    return Arrays.copyOfRange(source, start, end);
  }

  private static void put(byte[] target, int start, byte[] value) {
    System.arraycopy(value, 0, target, start, value.length);
  }
}
