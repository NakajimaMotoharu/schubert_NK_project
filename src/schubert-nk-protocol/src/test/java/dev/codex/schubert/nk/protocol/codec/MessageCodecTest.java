package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.WireMessage;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;

class MessageCodecTest {
  private static final String PROTOCOL_MAGIC = "SCHBNK01";
  private static final String LAYOUT_VERSION = "001";
  private static final String GAME_RESPONSE = "GAMRSP01";
  private static final String SYNC_REPLY_ADDRESS = "nk.sync.reply.web";
  private static final String SYNC_REQUEST_ADDRESS = "nk.sync.request";
  private static final String JMS_FIXTURE_ID = "ID:1";
  private static final String REPLY_ADDRESS = "reply";
  private static final String DESTINATION_ADDRESS = "destination";
  private static final UUID MESSAGE_ID = UUID.fromString("123e4567-e89b-12d3-a456-426614174000");
  private static final UUID CORRELATION_ID =
      UUID.fromString("223e4567-e89b-12d3-a456-426614174000");
  private static final Instant SENT_AT = Instant.parse("2026-09-02T03:34:56.789Z");
  private static final AuthenticationContext CONTEXT = AuthenticationContext.of("a".repeat(64));

  @Test
  void headerEncodingMatchesIndependentUi232GoldenVector() {
    CommonHeader header = requestHeader("LGNREQ01", 384);
    byte[] actual = HeaderCodec.standard().encode(header);
    byte[] expected = new byte[256];
    Arrays.fill(expected, (byte) ' ');
    ascii(expected, 0, PROTOCOL_MAGIC);
    ascii(expected, 8, LAYOUT_VERSION);
    ascii(expected, 11, "LGNREQ01");
    ascii(expected, 19, LAYOUT_VERSION);
    ascii(expected, 22, "QS");
    ascii(expected, 24, MESSAGE_ID.toString());
    ascii(expected, 60, MESSAGE_ID.toString());
    ascii(expected, 96, "20260902123456789");
    ascii(expected, 177, "0256");
    ascii(expected, 181, "000384");
    ascii(expected, 187, "000000");
    ascii(expected, 193, "000000");
    ascii(expected, 199, "000000640");

    assertArrayEquals(expected, actual);
    assertEquals(header, HeaderCodec.standard().peek(actual));
    assertThrows(NullPointerException.class, () -> new HeaderCodec(null));
    assertThrows(NullPointerException.class, () -> HeaderCodec.standard().encode(null));
    assertThrows(PermanentProtocolException.class, () -> HeaderCodec.standard().peek(null));
    assertThrows(
        PermanentProtocolException.class, () -> HeaderCodec.standard().peek(new byte[255]));
  }

  @Test
  void responseAndEventHeadersRoundTripWithoutLeakingContext() {
    CommonHeader response = responseHeader(GAME_RESPONSE, 9, 272, 1, ResultCode.SUCCESS);
    CommonHeader decoded = HeaderCodec.standard().peek(HeaderCodec.standard().encode(response));
    assertEquals(response, decoded);
    assertEquals(Optional.of(CONTEXT), decoded.authenticationContext());

    CommonHeader event = eventHeader();
    assertEquals(event, HeaderCodec.standard().peek(HeaderCodec.standard().encode(event)));

    // PT-PRO-002-H01 / BUG1806: UI232 literal 256-byte vectors, never codec-derived expected.
    String literalIdsAndJst =
        "123e4567-e89b-12d3-a456-426614174000"
            + "223e4567-e89b-12d3-a456-426614174000"
            + "20260902123456789";
    byte[] responseGolden =
        ("SCHBNK01001GAMRSP01001SS"
                + literalIdsAndJst
                + "a".repeat(64)
                + "02560000090002720000010000005370000"
                + " ".repeat(44))
            .getBytes(StandardCharsets.US_ASCII);
    byte[] eventGolden =
        ("SCHBNK01001WLGEVT01001EI"
                + literalIdsAndJst
                + " ".repeat(64)
                + "0256002080000000000000000002336"
                + " ".repeat(48))
            .getBytes(StandardCharsets.US_ASCII);
    assertEquals(256, responseGolden.length);
    assertEquals(256, eventGolden.length);
    assertArrayEquals(responseGolden, HeaderCodec.standard().encode(response));
    assertEquals(response, HeaderCodec.standard().peek(responseGolden));
    assertArrayEquals(eventGolden, HeaderCodec.standard().encode(event));
    assertEquals(event, HeaderCodec.standard().peek(eventGolden));
  }

  @Test
  void headerDecoderRejectsEveryFixedFieldAndProfileCorruption() {
    byte[] login = HeaderCodec.standard().encode(requestHeader("LGNREQ01", 384));
    corrupt(login, bytes -> bytes[0] = 'X');
    corrupt(login, bytes -> bytes[8] = '2');
    corrupt(login, bytes -> bytes[11] = 'x');
    corrupt(login, bytes -> ascii(bytes, 11, "ABCREQ01"));
    corrupt(login, bytes -> bytes[19] = '2');
    corrupt(login, bytes -> bytes[22] = 'X');
    corrupt(login, bytes -> bytes[23] = 'X');
    corrupt(login, bytes -> bytes[24] = 'X');
    corrupt(login, bytes -> bytes[25] = 'A');
    corrupt(login, bytes -> bytes[60] = 'X');
    corrupt(login, bytes -> bytes[96] = 'X');
    corrupt(login, bytes -> ascii(bytes, 96, "20260230000000000"));
    corrupt(login, bytes -> bytes[113] = 'g');
    corrupt(login, bytes -> ascii(bytes, 177, "0255"));
    corrupt(login, bytes -> ascii(bytes, 181, "000383"));
    corrupt(login, bytes -> ascii(bytes, 187, "000001"));
    corrupt(login, bytes -> ascii(bytes, 193, "000001"));
    corrupt(login, bytes -> ascii(bytes, 199, "000000639"));
    corrupt(login, bytes -> ascii(bytes, 208, "0000"));
    corrupt(login, bytes -> bytes[212] = 'X');

    byte[] response =
        HeaderCodec.standard()
            .encode(responseHeader(GAME_RESPONSE, 9, 272, 0, ResultCode.NOT_FOUND));
    corrupt(response, bytes -> ascii(bytes, 208, "9999"));
    corrupt(response, bytes -> Arrays.fill(bytes, 208, 212, (byte) ' '));
    corrupt(response, bytes -> ascii(bytes, 193, "000001"));

    CommonHeader unknownHeader =
        new CommonHeader(
            PROTOCOL_MAGIC,
            1,
            new LayoutId("ABCREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            MESSAGE_ID,
            MESSAGE_ID,
            SENT_AT,
            Optional.of(CONTEXT),
            256,
            0,
            0,
            0,
            256,
            Optional.empty());
    assertThrows(
        MessageEncodingException.class, () -> HeaderCodec.standard().encode(unknownHeader));
  }

  @Test
  void fixedPayloadIsDefensiveAndWireMessageChecksLengths() {
    byte[] data = new byte[] {1, 2};
    byte[] record = new byte[] {3, 4, 5};
    List<byte[]> inputs = new ArrayList<>();
    inputs.add(record);
    FixedPayload payload = new FixedPayload(data, 3, inputs);
    data[0] = 9;
    record[0] = 9;
    inputs.clear();
    assertArrayEquals(new byte[] {1, 2}, payload.copyData());
    assertArrayEquals(new byte[] {3, 4, 5}, payload.copyRecords().getFirst());
    byte[] copiedData = payload.copyData();
    copiedData[0] = 8;
    List<byte[]> copiedRecords = payload.copyRecords();
    copiedRecords.getFirst()[0] = 8;
    assertArrayEquals(new byte[] {1, 2}, payload.copyData());
    assertArrayEquals(new byte[] {3, 4, 5}, payload.copyRecords().getFirst());
    assertThrows(UnsupportedOperationException.class, () -> copiedRecords.clear());
    assertEquals(2, payload.dataLength());
    assertEquals(3, payload.recordLength());
    assertEquals(1, payload.recordCount());
    assertTrue(payload.toString().contains("dataLength=2"));
    assertFalse(payload.toString().contains("[1, 2]"));
    assertThrows(NullPointerException.class, () -> new FixedPayload(null, 0, List.of()));
    assertThrows(NullPointerException.class, () -> new FixedPayload(new byte[0], 0, null));
    assertThrows(
        LayoutValidationException.class, () -> new FixedPayload(new byte[0], -1, List.of()));
    ArrayList<byte[]> withNull = new ArrayList<>();
    withNull.add(null);
    assertThrows(NullPointerException.class, () -> new FixedPayload(new byte[0], 0, withNull));
    assertThrows(
        LayoutValidationException.class,
        () -> new FixedPayload(new byte[0], 2, List.of(new byte[1])));

    CommonHeader valid = responseHeader(GAME_RESPONSE, 9, 272, 1, ResultCode.SUCCESS);
    FixedPayload validPayload = new FixedPayload(new byte[9], 272, List.of(new byte[272]));
    WireMessage<FixedPayload> message = new WireMessage<>(valid, validPayload);
    assertEquals(valid, message.header());
    assertThrows(NullPointerException.class, () -> new WireMessage<>(null, validPayload));
    assertThrows(NullPointerException.class, () -> new WireMessage<>(valid, null));
    assertThrows(
        LayoutValidationException.class,
        () -> new WireMessage<>(valid, new FixedPayload(new byte[8], 272, List.of(new byte[272]))));
    assertThrows(
        LayoutValidationException.class,
        () -> new WireMessage<>(valid, new FixedPayload(new byte[9], 271, List.of(new byte[271]))));
    assertThrows(
        LayoutValidationException.class,
        () -> new WireMessage<>(valid, new FixedPayload(new byte[9], 272, List.of())));
  }

  @Test
  void fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizes() {
    MessageEncodingException direct = new MessageEncodingException("safe encoding failure");
    assertEquals("safe encoding failure", direct.getMessage());
    CommonHeader header = responseHeader(GAME_RESPONSE, 9, 272, 1, ResultCode.SUCCESS);
    byte[] data = new byte[9];
    Arrays.fill(data, (byte) ' ');
    byte[] record = new byte[272];
    Arrays.fill(record, (byte) ' ');
    WireMessage<FixedPayload> message =
        new WireMessage<>(header, new FixedPayload(data, 272, List.of(record)));
    FixedWidthEncoder encoder = FixedWidthEncoder.standard();
    byte[] body = encoder.encode(message);
    TransportMetadata metadata =
        metadata(
            header,
            TransportBodyType.BYTES,
            2,
            Optional.empty(),
            1_800_000_000_000L,
            SYNC_REPLY_ADDRESS);
    ExpectedRoute route =
        new ExpectedRoute(
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            SYNC_REPLY_ADDRESS,
            Optional.empty(),
            true);
    WireMessage<FixedPayload> decoded = FixedWidthDecoder.standard().decode(body, metadata, route);
    assertEquals(header, decoded.header());
    assertArrayEquals(data, decoded.payload().copyData());
    assertArrayEquals(record, decoded.payload().copyRecords().getFirst());
    assertNotSame(body, decoded.payload().copyData());
    assertThrows(NullPointerException.class, () -> new FixedWidthEncoder(null));
    assertThrows(NullPointerException.class, () -> new FixedWidthDecoder(null));
    assertThrows(NullPointerException.class, () -> encoder.encode(null));
    assertThrows(
        NullPointerException.class, () -> FixedWidthDecoder.standard().decode(body, null, route));
    assertThrows(
        NullPointerException.class,
        () -> FixedWidthDecoder.standard().decode(body, metadata, null));
    assertThrows(
        PermanentProtocolException.class,
        () -> FixedWidthDecoder.standard().decode(null, metadata, route));
    assertThrows(
        PermanentProtocolException.class,
        () -> FixedWidthDecoder.standard().decode(new byte[255], metadata, route));
    assertThrows(
        PermanentProtocolException.class,
        () -> FixedWidthDecoder.standard().decode(new byte[1_000_001], metadata, route));
    ExpectedRoute workRoute =
        new ExpectedRoute(
            MessageKind.EVENT, InteractionKind.INTERNAL, "nk.async.work", Optional.empty(), false);
    assertThrows(
        PermanentProtocolException.class,
        () -> FixedWidthDecoder.standard().decode(new byte[1_001], metadata, workRoute));
    byte[] extra = Arrays.copyOf(body, body.length + 1);
    assertThrows(
        PermanentProtocolException.class,
        () -> FixedWidthDecoder.standard().decode(extra, metadata, route));

    CommonHeader unknownHeader =
        new CommonHeader(
            PROTOCOL_MAGIC,
            1,
            new LayoutId("ABCREQ01"),
            1,
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            MESSAGE_ID,
            MESSAGE_ID,
            SENT_AT,
            Optional.of(CONTEXT),
            256,
            0,
            0,
            0,
            256,
            Optional.empty());
    assertThrows(
        MessageEncodingException.class,
        () ->
            encoder.encode(
                new WireMessage<>(unknownHeader, new FixedPayload(new byte[0], 0, List.of()))));
  }

  @Test
  void transportAndRouteContractsRejectEveryMismatch() {
    CommonHeader request = regularRequestHeader();
    TransportMetadata valid =
        metadata(
            request,
            TransportBodyType.BYTES,
            2,
            Optional.of(SYNC_REPLY_ADDRESS),
            1_800_000_000_000L,
            SYNC_REQUEST_ADDRESS);
    ExpectedRoute route =
        new ExpectedRoute(
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            SYNC_REQUEST_ADDRESS,
            Optional.of(SYNC_REPLY_ADDRESS),
            true);
    ProtocolValidator.validateTransport(request, valid, route);
    assertEquals(4, TransportBodyType.values().length);
    assertEquals(TransportBodyType.BYTES, TransportBodyType.valueOf("BYTES"));
    assertThrows(
        NullPointerException.class, () -> ProtocolValidator.validateTransport(null, valid, route));
    assertThrows(
        NullPointerException.class,
        () -> ProtocolValidator.validateTransport(request, null, route));
    assertThrows(
        NullPointerException.class,
        () -> ProtocolValidator.validateTransport(request, valid, null));
    invalidTransport(
        request,
        route,
        metadata(
            request,
            TransportBodyType.TEXT,
            2,
            Optional.of(SYNC_REPLY_ADDRESS),
            1,
            SYNC_REQUEST_ADDRESS));
    invalidTransport(
        request,
        route,
        metadata(
            request,
            TransportBodyType.BYTES,
            1,
            Optional.of(SYNC_REPLY_ADDRESS),
            1,
            SYNC_REQUEST_ADDRESS));
    invalidTransport(
        request,
        route,
        new TransportMetadata(
            TransportBodyType.BYTES,
            JMS_FIXTURE_ID,
            request.correlationId(),
            Optional.of(SYNC_REPLY_ADDRESS),
            1,
            2,
            1,
            request.messageId(),
            request.layoutId(),
            "002",
            SYNC_REQUEST_ADDRESS));
    invalidTransport(
        request,
        route,
        new TransportMetadata(
            TransportBodyType.BYTES,
            JMS_FIXTURE_ID,
            request.correlationId(),
            Optional.of(SYNC_REPLY_ADDRESS),
            1,
            2,
            1,
            CORRELATION_ID,
            request.layoutId(),
            LAYOUT_VERSION,
            SYNC_REQUEST_ADDRESS));
    invalidTransport(
        request,
        route,
        new TransportMetadata(
            TransportBodyType.BYTES,
            JMS_FIXTURE_ID,
            request.correlationId(),
            Optional.of(SYNC_REPLY_ADDRESS),
            1,
            2,
            1,
            request.messageId(),
            new LayoutId("GAMREQ01"),
            LAYOUT_VERSION,
            SYNC_REQUEST_ADDRESS));
    invalidTransport(
        request,
        route,
        new TransportMetadata(
            TransportBodyType.BYTES,
            JMS_FIXTURE_ID,
            CORRELATION_ID,
            Optional.of(SYNC_REPLY_ADDRESS),
            1,
            2,
            1,
            request.messageId(),
            request.layoutId(),
            LAYOUT_VERSION,
            SYNC_REQUEST_ADDRESS));
    invalidTransport(
        request,
        new ExpectedRoute(
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            SYNC_REQUEST_ADDRESS,
            Optional.empty(),
            true),
        valid);
    invalidTransport(
        request,
        new ExpectedRoute(
            MessageKind.REQUEST,
            InteractionKind.ASYNC_ACCEPTANCE,
            SYNC_REQUEST_ADDRESS,
            Optional.of(SYNC_REPLY_ADDRESS),
            true),
        valid);
    invalidTransport(
        request,
        route,
        metadata(request, TransportBodyType.BYTES, 2, Optional.of(SYNC_REPLY_ADDRESS), 1, "wrong"));
    invalidTransport(
        request,
        route,
        metadata(
            request, TransportBodyType.BYTES, 2, Optional.of("wrong"), 1, SYNC_REQUEST_ADDRESS));
    invalidTransport(
        request,
        route,
        metadata(
            request,
            TransportBodyType.BYTES,
            2,
            Optional.of(SYNC_REPLY_ADDRESS),
            0,
            SYNC_REQUEST_ADDRESS));
  }

  @Test
  void metadataAndExpectedRouteEstablishNullAndRangeContracts() {
    CommonHeader request = regularRequestHeader();
    TransportMetadata valid =
        metadata(
            request,
            TransportBodyType.BYTES,
            2,
            Optional.of(REPLY_ADDRESS),
            1,
            DESTINATION_ADDRESS);
    assertEquals(1, valid.deliveryCount());
    assertThrows(
        IllegalArgumentException.class,
        () ->
            metadata(
                request,
                TransportBodyType.BYTES,
                2,
                Optional.of(REPLY_ADDRESS),
                -1,
                DESTINATION_ADDRESS));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                "ID",
                request.correlationId(),
                Optional.of(REPLY_ADDRESS),
                1,
                2,
                0,
                request.messageId(),
                request.layoutId(),
                LAYOUT_VERSION,
                DESTINATION_ADDRESS));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                " ",
                request.correlationId(),
                Optional.of(REPLY_ADDRESS),
                1,
                2,
                1,
                request.messageId(),
                request.layoutId(),
                LAYOUT_VERSION,
                DESTINATION_ADDRESS));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                "ID",
                request.correlationId(),
                Optional.of(" "),
                1,
                2,
                1,
                request.messageId(),
                request.layoutId(),
                LAYOUT_VERSION,
                DESTINATION_ADDRESS));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                "ID",
                request.correlationId(),
                Optional.of(REPLY_ADDRESS),
                1,
                2,
                1,
                request.messageId(),
                request.layoutId(),
                " ",
                DESTINATION_ADDRESS));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                "ID",
                request.correlationId(),
                Optional.of(REPLY_ADDRESS),
                1,
                2,
                1,
                request.messageId(),
                request.layoutId(),
                LAYOUT_VERSION,
                " "));

    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                " ",
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                DESTINATION_ADDRESS,
                Optional.of(" "),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.EVENT,
                InteractionKind.SYNCHRONOUS,
                DESTINATION_ADDRESS,
                Optional.empty(),
                false));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.REQUEST,
                InteractionKind.INTERNAL,
                DESTINATION_ADDRESS,
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                DESTINATION_ADDRESS,
                Optional.empty(),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.RESPONSE,
                InteractionKind.SYNCHRONOUS,
                DESTINATION_ADDRESS,
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.EVENT,
                InteractionKind.INTERNAL,
                DESTINATION_ADDRESS,
                Optional.empty(),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new ExpectedRoute(
                MessageKind.RESPONSE,
                InteractionKind.SYNCHRONOUS,
                DESTINATION_ADDRESS,
                Optional.empty(),
                false));
    ExpectedRoute event =
        new ExpectedRoute(
            MessageKind.EVENT, InteractionKind.INTERNAL, "nk.web.log", Optional.empty(), false);
    assertFalse(event.expirationRequired());
  }

  private static void corrupt(byte[] source, Consumer<byte[]> mutator) {
    byte[] copy = source.clone();
    mutator.accept(copy);
    assertThrows(PermanentProtocolException.class, () -> HeaderCodec.standard().peek(copy));
  }

  private static void invalidTransport(
      CommonHeader header, ExpectedRoute route, TransportMetadata metadata) {
    assertThrows(
        PermanentProtocolException.class,
        () -> ProtocolValidator.validateTransport(header, metadata, route));
  }

  private static CommonHeader requestHeader(String id, int dataLength) {
    return new CommonHeader(
        PROTOCOL_MAGIC,
        1,
        new LayoutId(id),
        1,
        MessageKind.REQUEST,
        InteractionKind.SYNCHRONOUS,
        MESSAGE_ID,
        MESSAGE_ID,
        SENT_AT,
        Optional.empty(),
        256,
        dataLength,
        0,
        0,
        256 + dataLength,
        Optional.empty());
  }

  private static CommonHeader regularRequestHeader() {
    return new CommonHeader(
        PROTOCOL_MAGIC,
        1,
        new LayoutId("LOGREQ01"),
        1,
        MessageKind.REQUEST,
        InteractionKind.SYNCHRONOUS,
        MESSAGE_ID,
        MESSAGE_ID,
        SENT_AT,
        Optional.of(CONTEXT),
        256,
        0,
        0,
        0,
        256,
        Optional.empty());
  }

  private static CommonHeader responseHeader(
      String id, int dataLength, int recordLength, int recordCount, ResultCode code) {
    return new CommonHeader(
        PROTOCOL_MAGIC,
        1,
        new LayoutId(id),
        1,
        MessageKind.RESPONSE,
        InteractionKind.SYNCHRONOUS,
        MESSAGE_ID,
        CORRELATION_ID,
        SENT_AT,
        Optional.of(CONTEXT),
        256,
        dataLength,
        recordLength,
        recordCount,
        256 + dataLength + recordLength * recordCount,
        Optional.of(code));
  }

  private static CommonHeader eventHeader() {
    return new CommonHeader(
        PROTOCOL_MAGIC,
        1,
        new LayoutId("WLGEVT01"),
        1,
        MessageKind.EVENT,
        InteractionKind.INTERNAL,
        MESSAGE_ID,
        CORRELATION_ID,
        SENT_AT,
        Optional.empty(),
        256,
        2_080,
        0,
        0,
        2_336,
        Optional.empty());
  }

  private static TransportMetadata metadata(
      CommonHeader header,
      TransportBodyType bodyType,
      int deliveryMode,
      Optional<String> replyTo,
      long expiration,
      String destination) {
    return new TransportMetadata(
        bodyType,
        "ID:test",
        header.correlationId(),
        replyTo,
        expiration,
        deliveryMode,
        1,
        header.messageId(),
        header.layoutId(),
        LAYOUT_VERSION,
        destination);
  }

  private static void ascii(byte[] target, int offset, String value) {
    byte[] source = value.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(source, 0, target, offset, source.length);
  }
}
