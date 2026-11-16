package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** Independent literal values and actual collection contracts; SS322/333/354, BUG3111. */
class WireMetadataValueContractTest {
  private static final String REQUEST_ADDRESS = "request";
  private static final String REPLY_ADDRESS = "reply";
  private static final String MESSAGE_ID = "message";
  private static final String PROTOCOL_VERSION = "001";
  private static final UUID ID = UUID.fromString("123e4567-e89b-12d3-a456-426614174000");
  private static final String DIGEST = "a".repeat(64);

  @Test // PT-PRO-WIREMETA001
  void expectedRouteRetainsValuesAndRejectsMissingOrInconsistentRoutes() {
    ExpectedRoute first =
        route(
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            REQUEST_ADDRESS,
            Optional.of(REPLY_ADDRESS),
            true);
    ExpectedRoute second =
        route(
            MessageKind.REQUEST,
            InteractionKind.SYNCHRONOUS,
            REQUEST_ADDRESS,
            Optional.of(REPLY_ADDRESS),
            true);
    ExpectedRoute different =
        route(
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            REPLY_ADDRESS,
            Optional.empty(),
            true);
    assertKeys(
        first,
        second,
        different,
        "ExpectedRoute[messageKind=REQUEST, interactionKind=SYNCHRONOUS, destinationAddress=request, requiredReplyToAddress=Optional[reply], expirationRequired=true]");
    assertEquals(MessageKind.REQUEST, first.messageKind());
    assertEquals(InteractionKind.SYNCHRONOUS, first.interactionKind());
    assertEquals(REQUEST_ADDRESS, first.destinationAddress());
    assertEquals(Optional.of(REPLY_ADDRESS), first.requiredReplyToAddress());
    assertTrue(first.expirationRequired());
    assertFalse(
        route(MessageKind.EVENT, InteractionKind.INTERNAL, "event", Optional.empty(), false)
            .expirationRequired());
    assertThrows(
        NullPointerException.class,
        () ->
            route(
                null,
                InteractionKind.SYNCHRONOUS,
                REQUEST_ADDRESS,
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        NullPointerException.class,
        () -> route(MessageKind.REQUEST, null, REQUEST_ADDRESS, Optional.of(REPLY_ADDRESS), true));
    assertThrows(
        NullPointerException.class,
        () ->
            route(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                null,
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        NullPointerException.class,
        () -> route(MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, REQUEST_ADDRESS, null, true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            route(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                " ",
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            route(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                REQUEST_ADDRESS,
                Optional.of(" "),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            route(
                MessageKind.EVENT, InteractionKind.SYNCHRONOUS, "event", Optional.empty(), false));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            route(
                MessageKind.REQUEST,
                InteractionKind.INTERNAL,
                REQUEST_ADDRESS,
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            route(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                REQUEST_ADDRESS,
                Optional.empty(),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            route(
                MessageKind.RESPONSE,
                InteractionKind.SYNCHRONOUS,
                REPLY_ADDRESS,
                Optional.of(REPLY_ADDRESS),
                true));
    assertThrows(
        IllegalArgumentException.class,
        () -> route(MessageKind.EVENT, InteractionKind.INTERNAL, "event", Optional.empty(), true));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            route(
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                REQUEST_ADDRESS,
                Optional.of(REPLY_ADDRESS),
                false));
  }

  @Test // PT-PRO-WIREMETA002
  void transportSnapshotRetainsEveryComponentAndRejectsInvalidBoundaries() {
    LayoutId layout = new LayoutId("LGNREQ01");
    TransportMetadata first = metadata(MESSAGE_ID, Optional.of(REPLY_ADDRESS), 1, 1);
    TransportMetadata second = metadata(MESSAGE_ID, Optional.of(REPLY_ADDRESS), 1, 1);
    TransportMetadata different = metadata("other", Optional.of(REPLY_ADDRESS), 1, 1);
    assertKeys(
        first,
        second,
        different,
        "TransportMetadata[bodyType=BYTES, transportMessageId=message, correlationId=123e4567-e89b-12d3-a456-426614174000, replyToAddress=Optional[reply], expirationEpochMillis=1, deliveryMode=2, deliveryCount=1, nkMessageId=123e4567-e89b-12d3-a456-426614174000, nkLayoutId=LGNREQ01, nkProtocolVersion=001, destinationAddress=request]");
    assertEquals(TransportBodyType.BYTES, first.bodyType());
    assertEquals(MESSAGE_ID, first.transportMessageId());
    assertEquals(ID, first.correlationId());
    assertEquals(Optional.of(REPLY_ADDRESS), first.replyToAddress());
    assertEquals(1, first.expirationEpochMillis());
    assertEquals(2, first.deliveryMode());
    assertEquals(1, first.deliveryCount());
    assertEquals(ID, first.nkMessageId());
    assertEquals(layout, first.nkLayoutId());
    assertEquals(PROTOCOL_VERSION, first.nkProtocolVersion());
    assertEquals(REQUEST_ADDRESS, first.destinationAddress());
    assertEquals(0, metadata(MESSAGE_ID, Optional.empty(), 0, 1).expirationEpochMillis());
    assertEquals(
        Long.MAX_VALUE,
        metadata(MESSAGE_ID, Optional.empty(), Long.MAX_VALUE, Integer.MAX_VALUE)
            .expirationEpochMillis());
    assertThrows(IllegalArgumentException.class, () -> metadata(" ", Optional.empty(), 0, 1));
    assertThrows(
        IllegalArgumentException.class, () -> metadata(MESSAGE_ID, Optional.of(" "), 0, 1));
    assertThrows(
        IllegalArgumentException.class, () -> metadata(MESSAGE_ID, Optional.empty(), -1, 1));
    assertThrows(
        IllegalArgumentException.class, () -> metadata(MESSAGE_ID, Optional.empty(), 0, 0));
    assertThrows(NullPointerException.class, () -> metadata(null, Optional.empty(), 0, 1));
    assertThrows(NullPointerException.class, () -> metadata(MESSAGE_ID, null, 0, 1));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransportMetadata(
                null,
                MESSAGE_ID,
                ID,
                Optional.empty(),
                0,
                2,
                1,
                ID,
                layout,
                PROTOCOL_VERSION,
                REQUEST_ADDRESS));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                MESSAGE_ID,
                null,
                Optional.empty(),
                0,
                2,
                1,
                ID,
                layout,
                PROTOCOL_VERSION,
                REQUEST_ADDRESS));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                MESSAGE_ID,
                ID,
                Optional.empty(),
                0,
                2,
                1,
                null,
                layout,
                PROTOCOL_VERSION,
                REQUEST_ADDRESS));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                MESSAGE_ID,
                ID,
                Optional.empty(),
                0,
                2,
                1,
                ID,
                null,
                PROTOCOL_VERSION,
                REQUEST_ADDRESS));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                MESSAGE_ID,
                ID,
                Optional.empty(),
                0,
                2,
                1,
                ID,
                layout,
                null,
                REQUEST_ADDRESS));
    assertThrows(
        NullPointerException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                MESSAGE_ID,
                ID,
                Optional.empty(),
                0,
                2,
                1,
                ID,
                layout,
                PROTOCOL_VERSION,
                null));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                MESSAGE_ID,
                ID,
                Optional.empty(),
                0,
                2,
                1,
                ID,
                layout,
                " ",
                REQUEST_ADDRESS));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new TransportMetadata(
                TransportBodyType.BYTES,
                MESSAGE_ID,
                ID,
                Optional.empty(),
                0,
                2,
                1,
                ID,
                layout,
                PROTOCOL_VERSION,
                " "));
  }

  @Test // PT-PRO-WIREMETA003
  void largeContentUsesIndependent4800ByteEquationAndValueKeys() {
    LargeResultContent first = new LargeResultContent(1, 4800, DIGEST);
    LargeResultContent second = new LargeResultContent(1, 4800, "a".repeat(64));
    LargeResultContent different = new LargeResultContent(2, 9600, DIGEST);
    assertKeys(
        first,
        second,
        different,
        "LargeResultContent[recordCount=1, byteLength=4800, sha256=" + "a".repeat(64) + "]");
    assertEquals(1, first.recordCount());
    assertEquals(4800, first.byteLength());
    assertEquals(DIGEST, first.sha256());
    assertEquals(48_000_000, new LargeResultContent(10_000, 48_000_000, DIGEST).byteLength());
    assertThrows(NullPointerException.class, () -> new LargeResultContent(1, 4800, null));
    assertThrows(IllegalArgumentException.class, () -> new LargeResultContent(0, 0, DIGEST));
    assertThrows(
        IllegalArgumentException.class, () -> new LargeResultContent(10_001, 48_004_800, DIGEST));
    assertThrows(IllegalArgumentException.class, () -> new LargeResultContent(1, 4799, DIGEST));
    assertThrows(
        IllegalArgumentException.class, () -> new LargeResultContent(1, 4800, "A".repeat(64)));
    assertThrows(
        IllegalArgumentException.class, () -> new LargeResultContent(1, 4800, "a".repeat(63)));
  }

  private static ExpectedRoute route(
      MessageKind kind,
      InteractionKind interaction,
      String address,
      Optional<String> reply,
      boolean expiration) {
    return new ExpectedRoute(kind, interaction, address, reply, expiration);
  }

  private static TransportMetadata metadata(
      String message, Optional<String> reply, long expiration, int count) {
    return new TransportMetadata(
        TransportBodyType.BYTES,
        message,
        ID,
        reply,
        expiration,
        2,
        count,
        ID,
        new LayoutId("LGNREQ01"),
        PROTOCOL_VERSION,
        REQUEST_ADDRESS);
  }

  private static <T> void assertKeys(T first, T same, T different, String expectedText) {
    // Method-local nonconcurrent map verifies actual key use, not a shared mutable cache.
    Map<T, String> keys = new HashMap<>();
    keys.put(first, "retained");
    assertEquals("retained", keys.get(same));
    assertNull(keys.get(different));
    assertEquals(first, same);
    assertNotEquals(first, different);
    assertFalse(first.equals(null));
    assertFalse(first.equals("other-type"));
    assertEquals(expectedText, first.toString());
  }
}
