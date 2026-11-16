package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.CommonHeader;
import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SS322/323/354 immutable aggregate contracts, independent literals, BUG3111/YKT2583. */
class ProtocolAggregateValueContractTest {
  private static final String LAYOUT_IDENTIFIER = "LGNREQ01";
  private static final String FIELD_NAME = "field";
  private static final String RULE = "rule";
  private static final String FIELD_TEXT = "fixture";
  private static final String ID_TEXT = "123e4567-e89b-12d3-a456-426614174000";
  private static final String HEADER_TEXT =
      "CommonHeader[layoutId=LGNREQ01, messageKind=REQUEST, interactionKind=SYNCHRONOUS, messageId=123e4567-e89b-12d3-a456-426614174000, correlationId=123e4567-e89b-12d3-a456-426614174000, totalLength=258, resultCode=Optional.empty, authenticationContext=REDACTED]";
  private static final String FIELD_RENDERING =
      "FieldDefinition[area=DATA, name=field, start=1, end=2, length=2, wireType=TEXT, presence=MANDATORY, padding=SPACE_RIGHT, javaType=class java.lang.String, semanticRule=rule]";

  @Test // PT-PRO-AGGREGATE001
  void fieldMetadataRetainsIndependentOneBasedOffsetsAndActualValueKeys() {
    FieldDefinition<String> first = field(FIELD_NAME);
    FieldDefinition<String> second = field(FIELD_NAME);
    assertKeys(first, second, field("different"), FIELD_RENDERING);
    assertEquals(1, first.start());
    assertEquals(2, first.end());
    assertEquals(2, first.length());
    assertEquals(Padding.SPACE_RIGHT, first.padding());
    assertEquals(String.class, first.javaType());
  }

  @Test // PT-PRO-AGGREGATE002
  void layoutCatalogCopiesItsInputAndUsesStructuralValueKeys() {
    LayoutDefinition first = layout();
    LayoutDefinition same = layout();
    LayoutDefinition different =
        new LayoutDefinition(
            new LayoutId("LGNRSP01"),
            1,
            MessageKind.RESPONSE,
            InteractionKind.SYNCHRONOUS,
            2,
            0,
            0,
            258);
    assertKeys(
        first,
        same,
        different,
        "LayoutDefinition[id=LGNREQ01, version=1, messageKind=REQUEST, interactionKind=SYNCHRONOUS, dataLength=2, recordLength=0, maximumRecordCount=0, maximumTotalLength=258]");
    List<FieldDefinition<?>> input = new ArrayList<>();
    input.add(field(FIELD_NAME));
    LayoutFields fields = new LayoutFields(first, input, List.of());
    input.clear();
    LayoutFields equivalent = new LayoutFields(same, List.of(field(FIELD_NAME)), List.of());
    LayoutFields unequal = new LayoutFields(first, List.of(field("different")), List.of());
    assertKeys(
        fields,
        equivalent,
        unequal,
        "LayoutFields[layout=LayoutDefinition[id=LGNREQ01, version=1, messageKind=REQUEST, interactionKind=SYNCHRONOUS, dataLength=2, recordLength=0, maximumRecordCount=0, maximumTotalLength=258], dataFields=["
            + FIELD_RENDERING
            + "], recordFields=[]]");
    assertEquals(new LayoutId(LAYOUT_IDENTIFIER), fields.id());
    assertEquals(1, fields.dataFields().size());
    assertEquals(first, fields.layout());
    assertEquals(List.of(), fields.recordFields());
    assertThrows(UnsupportedOperationException.class, () -> fields.dataFields().clear());
  }

  @Test // PT-PRO-AGGREGATE003
  void fieldAndTypedPayloadWrappersKeepValueKeysAndDefensiveLists() {
    FieldValueSet value = values(FIELD_TEXT);
    List<FieldValueSet> input = new ArrayList<>();
    input.add(values(FIELD_TEXT));
    PayloadValues first = new PayloadValues(new LayoutId(LAYOUT_IDENTIFIER), value, input);
    input.clear();
    PayloadValues same =
        new PayloadValues(
            new LayoutId(LAYOUT_IDENTIFIER), values(FIELD_TEXT), List.of(values(FIELD_TEXT)));
    PayloadValues different =
        new PayloadValues(
            new LayoutId(LAYOUT_IDENTIFIER), values("other"), List.of(values(FIELD_TEXT)));
    assertKeys(first, same, different, "PayloadValues[layoutId=LGNREQ01, recordCount=1]");
    assertEquals(1, first.records().size());
    assertEquals(new LayoutId(LAYOUT_IDENTIFIER), first.layoutId());
    assertEquals(values(FIELD_TEXT), first.data());
    assertThrows(UnsupportedOperationException.class, () -> first.records().clear());
    // Retained components are immutable identity values; wrappers are constructed separately.
    PayloadData data = () -> value;
    PayloadRecord record = () -> value;
    List<PayloadRecord> typedInput = new ArrayList<>();
    typedInput.add(record);
    TypedPayloadValues typed =
        new TypedPayloadValues(new LayoutId(LAYOUT_IDENTIFIER), data, typedInput);
    typedInput.clear();
    TypedPayloadValues typedSame =
        new TypedPayloadValues(new LayoutId(LAYOUT_IDENTIFIER), data, List.of(record));
    TypedPayloadValues typedDifferent =
        new TypedPayloadValues(new LayoutId(LAYOUT_IDENTIFIER), data, List.of());
    assertKeys(
        typed, typedSame, typedDifferent, "TypedPayloadValues[layoutId=LGNREQ01, recordCount=1]");
    assertEquals(value, typed.data().fields());
    assertEquals(new LayoutId(LAYOUT_IDENTIFIER), typed.layoutId());
    assertEquals(1, typed.records().size());
    assertThrows(UnsupportedOperationException.class, () -> typed.records().clear());
  }

  @Test // PT-PRO-AGGREGATE004
  void headerAndWireWrappersRetainTheirDeclaredComponentIdentity() {
    CommonHeader first = header(ID_TEXT);
    CommonHeader same = header(ID_TEXT);
    CommonHeader different = header("123e4567-e89b-12d3-a456-426614174001");
    assertKeys(first, same, different, HEADER_TEXT);
    assertEquals("SCHBNK01", first.protocolIdentifier());
    assertEquals(1, first.headerVersion());
    assertEquals(1, first.layoutVersion());
    assertEquals(MessageKind.REQUEST, first.messageKind());
    assertEquals(InteractionKind.SYNCHRONOUS, first.interactionKind());
    assertEquals(UUID.fromString(ID_TEXT), first.messageId());
    assertEquals(Instant.parse("2026-09-01T00:00:00Z"), first.sentAt());
    assertEquals(Optional.empty(), first.authenticationContext());
    assertEquals(256, first.headerLength());
    assertEquals(Optional.empty(), first.resultCode());
    FixedPayload immutable = new FixedPayload(new byte[] {0x41, 0x42}, 0, List.of());
    WireMessage<FixedPayload> message = new WireMessage<>(first, immutable);
    WireMessage<FixedPayload> equalMessage = new WireMessage<>(same, immutable);
    WireMessage<FixedPayload> unequalMessage = new WireMessage<>(different, immutable);
    assertKeys(
        message,
        equalMessage,
        unequalMessage,
        "WireMessage[header="
            + HEADER_TEXT
            + ", payload=FixedPayload[dataLength=2, recordLength=0, recordCount=0]]");
    assertEquals(immutable, message.payload());
    assertEquals(first, message.header());
    assertThrows(NullPointerException.class, () -> new WireMessage<FixedPayload>(null, immutable));
    assertThrows(NullPointerException.class, () -> new WireMessage<FixedPayload>(first, null));
    assertThrows(
        LayoutValidationException.class,
        () -> new WireMessage<>(first, new FixedPayload(new byte[1], 0, List.of())));
    assertThrows(
        LayoutValidationException.class,
        () -> new WireMessage<>(first, new FixedPayload(new byte[2], 1, List.of())));
    assertThrows(
        LayoutValidationException.class,
        () -> new WireMessage<>(first, new FixedPayload(new byte[2], 0, List.of(new byte[0]))));
  }

  private static FieldDefinition<String> field(String name) {
    return new FieldDefinition<>(
        FieldArea.DATA,
        name,
        1,
        2,
        2,
        WireType.TEXT,
        Presence.MANDATORY,
        Padding.SPACE_RIGHT,
        String.class,
        RULE);
  }

  private static LayoutDefinition layout() {
    return new LayoutDefinition(
        new LayoutId(LAYOUT_IDENTIFIER),
        1,
        MessageKind.REQUEST,
        InteractionKind.SYNCHRONOUS,
        2,
        0,
        0,
        258);
  }

  private static FieldValueSet values(String text) {
    return new FieldValueSet(Map.of(FIELD_NAME, new FieldValue.Text(text)));
  }

  private static CommonHeader header(String id) {
    UUID message = UUID.fromString(id);
    return new CommonHeader(
        "SCHBNK01",
        1,
        new LayoutId(LAYOUT_IDENTIFIER),
        1,
        MessageKind.REQUEST,
        InteractionKind.SYNCHRONOUS,
        message,
        message,
        Instant.parse("2026-09-01T00:00:00Z"),
        Optional.empty(),
        256,
        2,
        0,
        0,
        258,
        Optional.empty());
  }

  private static <T> void assertKeys(T first, T same, T different, String expectedText) {
    // Invocation-local map is never shared; independent wrappers exercise real hash/equality keys.
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
