package dev.codex.schubert.nk.protocol.codec;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.MessageKind;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FieldDefinition;
import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
import dev.codex.schubert.nk.protocol.layout.LayoutFieldCatalog;
import dev.codex.schubert.nk.protocol.layout.LayoutFields;
import dev.codex.schubert.nk.protocol.layout.LayoutId;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.PayloadValues;
import dev.codex.schubert.nk.protocol.layout.Presence;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class PayloadCodecTest {
  @Test
  void allSixtyFourLayoutsRoundTripMinimumSuccessValues() {
    PayloadCodec codec = PayloadCodec.standard();
    assertSame(codec, PayloadCodec.standard());
    for (LayoutFields layout : LayoutFieldCatalog.standard().all()) {
      FieldValueSet data = minimumValues(layout.dataFields());
      List<FieldValueSet> records =
          layout.recordFields().isEmpty()
              ? List.of()
              : List.of(minimumValues(layout.recordFields()));
      PayloadValues input = new PayloadValues(layout.id(), data, records);

      FixedPayload encoded = codec.encode(input, false);
      assertEquals(layout.layout().dataLength(), encoded.dataLength(), layout.id().value());
      assertEquals(layout.layout().recordLength(), encoded.recordLength(), layout.id().value());
      assertEquals(records.size(), encoded.recordCount(), layout.id().value());
      assertEquals(
          input,
          codec.decode(layout.id(), encoded.copyData(), encoded.copyRecords(), false),
          layout.id().value());
    }
  }

  @Test
  void everyResponseLayoutUsesExactErrorFillersAndNoRecords() {
    PayloadCodec codec = PayloadCodec.standard();
    long responses = 0;
    for (LayoutFields layout : LayoutFieldCatalog.standard().all()) {
      if (layout.layout().messageKind() != MessageKind.RESPONSE) {
        continue;
      }
      responses++;
      FixedPayload encoded =
          codec.encode(new PayloadValues(layout.id(), FieldValueSet.empty(), List.of()), true);
      PayloadValues decoded =
          codec.decode(layout.id(), encoded.copyData(), encoded.copyRecords(), true);
      assertEquals(0, decoded.records().size());
      assertTrue(
          layout.dataFields().stream()
              .filter(field -> field.presence() != Presence.FIXED)
              .allMatch(
                  field -> decoded.data().getOrUnset(field.name()) == FieldValue.Unset.INSTANCE));
    }
    assertEquals(31, responses);
  }

  @Test
  void resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState() {
    PayloadCodec codec = PayloadCodec.standard();
    LayoutId layoutId = new LayoutId("NTCRSP01");
    PayloadValues conflict =
        new PayloadValues(
            layoutId,
            new FieldValueSet(
                Map.of(
                    "更新後状態", new FieldValue.Text("PROCESSING"), "取消日時", FieldValue.Unset.INSTANCE)),
            List.of());

    FixedPayload encoded = codec.encode(conflict, ResultCode.NOT_CANCELLABLE);
    assertArrayEquals(
        "PROCESSING                      ".getBytes(StandardCharsets.US_ASCII), encoded.copyData());
    assertEquals(
        conflict,
        codec.decode(
            layoutId, encoded.copyData(), encoded.copyRecords(), ResultCode.NOT_CANCELLABLE));
    for (String state : List.of("COMPLETED", "ERROR")) {
      PayloadValues stateValue =
          new PayloadValues(
              layoutId,
              new FieldValueSet(
                  Map.of("更新後状態", new FieldValue.Text(state), "取消日時", FieldValue.Unset.INSTANCE)),
              List.of());
      FixedPayload statePayload = codec.encode(stateValue, ResultCode.NOT_CANCELLABLE);
      // UI236 section10.2: independent 12-byte status, 17-byte absent time, 3 spaces.
      byte[] conflictGolden = new byte[32];
      Arrays.fill(conflictGolden, (byte) ' ');
      byte[] stateBytes = state.getBytes(StandardCharsets.US_ASCII);
      System.arraycopy(stateBytes, 0, conflictGolden, 0, stateBytes.length);
      assertArrayEquals(conflictGolden, statePayload.copyData());
      assertEquals(
          stateValue,
          codec.decode(layoutId, conflictGolden, List.of(), ResultCode.NOT_CANCELLABLE));
      assertEquals(
          stateValue,
          codec.decode(layoutId, statePayload.copyData(), List.of(), ResultCode.NOT_CANCELLABLE));
    }

    PayloadValues blank = new PayloadValues(layoutId, FieldValueSet.empty(), List.of());
    assertTrue(
        codec
            .decode(
                layoutId,
                codec.encode(blank, ResultCode.NOT_FOUND).copyData(),
                List.of(),
                ResultCode.NOT_FOUND)
            .data()
            .names()
            .stream()
            .allMatch(
                name ->
                    codec
                            .decode(
                                layoutId,
                                codec.encode(blank, ResultCode.NOT_FOUND).copyData(),
                                List.of(),
                                ResultCode.NOT_FOUND)
                            .data()
                            .getOrUnset(name)
                        == FieldValue.Unset.INSTANCE));
    PayloadValues success =
        new PayloadValues(
            layoutId,
            new FieldValueSet(
                Map.of(
                    "更新後状態", new FieldValue.Text("CANCELLED"),
                    "取消日時", new FieldValue.Text("20260902123456789"))),
            List.of());
    assertEquals(
        success,
        codec.decode(
            layoutId,
            codec.encode(success, ResultCode.SUCCESS).copyData(),
            List.of(),
            ResultCode.SUCCESS));

    // UI236 section10.2: literal wire, not an encoder-generated expected value.
    byte[] cancelledGolden =
        "CANCELLED   20260902123456789   ".getBytes(StandardCharsets.US_ASCII);
    for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS)) {
      assertArrayEquals(cancelledGolden, codec.encode(success, code).copyData());
      assertEquals(success, codec.decode(layoutId, cancelledGolden, List.of(), code));
    }

    assertThrows(NullPointerException.class, () -> codec.encode(conflict, (ResultCode) null));
    assertThrows(
        NullPointerException.class,
        () -> codec.decode(layoutId, encoded.copyData(), List.of(), (ResultCode) null));
    assertThrows(
        MessageEncodingException.class, () -> codec.encode(blank, ResultCode.NOT_CANCELLABLE));
    codec.encode(
        new PayloadValues(new LayoutId("LGNRSP01"), FieldValueSet.empty(), List.of()),
        ResultCode.NOT_CANCELLABLE);
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(
                    layoutId,
                    new FieldValueSet(Map.of("更新後状態", new FieldValue.Text("RECEIVED"))),
                    List.of()),
                ResultCode.NOT_CANCELLABLE));
    for (String invalid : List.of("RECEIVED", "CANCELLED", "UNKNOWN")) {
      byte[] corrupted = encoded.copyData();
      Arrays.fill(corrupted, 0, 12, (byte) ' ');
      System.arraycopy(
          invalid.getBytes(StandardCharsets.US_ASCII), 0, corrupted, 0, invalid.length());
      assertThrows(
          PermanentProtocolException.class,
          () -> codec.decode(layoutId, corrupted, List.of(), ResultCode.NOT_CANCELLABLE));
    }
    byte[] missingState = encoded.copyData();
    Arrays.fill(missingState, 0, 12, (byte) ' ');
    assertThrows(
        PermanentProtocolException.class,
        () -> codec.decode(layoutId, missingState, List.of(), ResultCode.NOT_CANCELLABLE));
  }

  @Test
  void fixedAndIndependentGoldenFieldsEncodeAtExactOffsets() {
    PayloadCodec codec = PayloadCodec.standard();
    FieldValueSet login =
        new FieldValueSet(
            Map.of(
                "Username", new FieldValue.Text("user"),
                "Password", new FieldValue.Text("PublicTestPassword"),
                "Client address", new FieldValue.Text("127.0.0.1")));
    byte[] loginData =
        codec
            .encode(new PayloadValues(new LayoutId("LGNREQ01"), login, List.of()), false)
            .copyData();
    byte[] expected = new byte[384];
    Arrays.fill(expected, (byte) ' ');
    System.arraycopy("user".getBytes(StandardCharsets.UTF_8), 0, expected, 0, 4);
    System.arraycopy("PublicTestPassword".getBytes(StandardCharsets.UTF_8), 0, expected, 64, 18);
    System.arraycopy("127.0.0.1".getBytes(StandardCharsets.US_ASCII), 0, expected, 320, 9);
    assertArrayEquals(expected, loginData);

    LayoutFields event = LayoutFieldCatalog.standard().require("WLGEVT01");
    byte[] eventData =
        codec
            .encode(
                new PayloadValues(event.id(), minimumValues(event.dataFields()), List.of()), false)
            .copyData();
    byte[] fixed = Arrays.copyOfRange(eventData, 17, 33);
    byte[] expectedFixed = new byte[16];
    Arrays.fill(expectedFixed, (byte) ' ');
    System.arraycopy("REQUEST".getBytes(StandardCharsets.US_ASCII), 0, expectedFixed, 0, 7);
    assertArrayEquals(expectedFixed, fixed);
  }

  @Test
  void encodeRejectsUnknownMissingWrongTypeAndRecordViolations() {
    PayloadCodec codec = PayloadCodec.standard();
    assertThrows(NullPointerException.class, () -> codec.encode(null, false));
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(
                    new LayoutId("LGNREQ01"),
                    new FieldValueSet(Map.of("Unknown", new FieldValue.Text("x"))),
                    List.of()),
                false));
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(
                    new LayoutId("LGNREQ01"),
                    new FieldValueSet(Map.of("Reserved", new FieldValue.Text("x"))),
                    List.of()),
                false));
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(new LayoutId("LGNREQ01"), FieldValueSet.empty(), List.of()),
                false));
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(
                    new LayoutId("LGNREQ01"),
                    new FieldValueSet(
                        Map.of(
                            "Username", FieldValue.Unset.INSTANCE,
                            "Password", new FieldValue.Text("p"),
                            "Client address", new FieldValue.Text("127.0.0.1"))),
                    List.of()),
                false));
    assertWrongType(codec, "LGNREQ01", "Username", new FieldValue.Numeric(1));
    assertWrongType(codec, "GAMRSP01", "Total count", new FieldValue.Text("1"));
    assertWrongType(codec, "ANMRSP01", "Opening有無", new FieldValue.Text("1"));

    LayoutFields game = LayoutFieldCatalog.standard().require("GAMRSP01");
    FieldValueSet gameRecord = minimumValues(game.recordFields());
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(
                    game.id(),
                    minimumValues(game.dataFields()),
                    Collections.nCopies(11, gameRecord)),
                false));
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(game.id(), minimumValues(game.dataFields()), List.of(gameRecord)),
                true));

    FixedPayload optional =
        codec.encode(
            new PayloadValues(
                new LayoutId("SPKREQ01"),
                new FieldValueSet(Map.of("Game code", FieldValue.Unset.INSTANCE)),
                List.of()),
            false);
    assertArrayEquals("            ".getBytes(StandardCharsets.US_ASCII), optional.copyData());
    FixedPayload optionalValue =
        codec.encode(
            new PayloadValues(
                new LayoutId("SPKREQ01"),
                new FieldValueSet(Map.of("Game code", new FieldValue.Text("NUKITASHI1"))),
                List.of()),
            false);
    assertEquals("NUKITASHI1  ", new String(optionalValue.copyData(), StandardCharsets.US_ASCII));
  }

  @Test
  void decodeRejectsLengthsNullsFixedValuesAndBadErrorFillers() {
    PayloadCodec codec = PayloadCodec.standard();
    assertThrows(
        NullPointerException.class, () -> codec.decode(null, new byte[0], List.of(), false));
    assertThrows(
        NullPointerException.class,
        () -> codec.decode(new LayoutId("LOGREQ01"), null, List.of(), false));
    assertThrows(
        NullPointerException.class,
        () -> codec.decode(new LayoutId("LOGREQ01"), new byte[0], null, false));
    assertThrows(
        PermanentProtocolException.class,
        () -> codec.decode(new LayoutId("LGNREQ01"), new byte[383], List.of(), false));
    assertThrows(
        PermanentProtocolException.class,
        () -> codec.decode(new LayoutId("GAMRSP01"), new byte[9], List.of(new byte[272]), true));
    assertThrows(
        PermanentProtocolException.class,
        () ->
            codec.decode(
                new LayoutId("GAMRSP01"),
                new byte[9],
                Collections.nCopies(11, new byte[272]),
                false));
    assertThrows(
        NullPointerException.class,
        () ->
            codec.decode(
                new LayoutId("GAMRSP01"),
                "000000000".getBytes(StandardCharsets.US_ASCII),
                Arrays.asList((byte[]) null),
                false));
    assertThrows(
        PermanentProtocolException.class,
        () ->
            codec.decode(
                new LayoutId("GAMRSP01"),
                "000000000".getBytes(StandardCharsets.US_ASCII),
                List.of(new byte[271]),
                false));

    byte[] login =
        codec
            .encode(
                new PayloadValues(
                    new LayoutId("LGNREQ01"),
                    new FieldValueSet(
                        Map.of(
                            "Username", new FieldValue.Text("user"),
                            "Password", new FieldValue.Text("p"),
                            "Client address", new FieldValue.Text("127.0.0.1"))),
                    List.of()),
                false)
            .copyData();
    login[365] = 'X';
    assertThrows(
        PermanentProtocolException.class,
        () -> codec.decode(new LayoutId("LGNREQ01"), login, List.of(), false));

    LayoutFields event = LayoutFieldCatalog.standard().require("WLGEVT01");
    byte[] eventData =
        codec
            .encode(
                new PayloadValues(event.id(), minimumValues(event.dataFields()), List.of()), false)
            .copyData();
    eventData[17] = 'X';
    assertThrows(
        PermanentProtocolException.class,
        () -> codec.decode(event.id(), eventData, List.of(), false));

    assertBadErrorFiller(codec, "LGNRSP01", 0, (byte) 'A');
    assertBadErrorFiller(codec, "LGNRSP01", 167, (byte) '1');
    assertBadErrorFiller(codec, "ANMRSP01", 6, (byte) '0');
  }

  @Test
  void valuesAreImmutableNullSafeAndRedacted() {
    assertThrows(NullPointerException.class, () -> new FieldValue.Text(null));
    FieldValue.Text secret = new FieldValue.Text("NeverPrintThisValue");
    assertFalse(secret.toString().contains(secret.value()));
    assertEquals(1, new FieldValue.Numeric(1).value());
    assertTrue(new FieldValue.Flag(true).value());
    assertEquals("INSTANCE", FieldValue.Unset.INSTANCE.toString());

    assertThrows(NullPointerException.class, () -> new FieldValueSet(null));
    LinkedHashMap<String, FieldValue> nullName = new LinkedHashMap<>();
    nullName.put(null, secret);
    assertThrows(NullPointerException.class, () -> new FieldValueSet(nullName));
    LinkedHashMap<String, FieldValue> nullValue = new LinkedHashMap<>();
    nullValue.put("name", null);
    assertThrows(NullPointerException.class, () -> new FieldValueSet(nullValue));
    assertThrows(LayoutValidationException.class, () -> new FieldValueSet(Map.of(" ", secret)));

    FieldValueSet values = new FieldValueSet(Map.of("safeName", secret));
    assertEquals(1, values.size());
    assertSame(secret, values.getOrUnset("safeName"));
    assertSame(FieldValue.Unset.INSTANCE, values.getOrUnset("missing"));
    assertThrows(NullPointerException.class, () -> values.getOrUnset(null));
    assertThrows(UnsupportedOperationException.class, () -> values.names().clear());
    assertTrue(values.toString().contains("safeName"));
    assertFalse(values.toString().contains(secret.value()));
    assertEquals(values, values);
    assertEquals(values, new FieldValueSet(Map.of("safeName", secret)));
    assertNotEquals(values, FieldValueSet.empty());
    assertNotEquals(values, "not-values");
    assertEquals(values.hashCode(), new FieldValueSet(Map.of("safeName", secret)).hashCode());

    assertThrows(NullPointerException.class, () -> new PayloadValues(null, values, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new PayloadValues(new LayoutId("LOGREQ01"), null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new PayloadValues(new LayoutId("LOGREQ01"), values, null));
    ArrayList<FieldValueSet> nullRecord = new ArrayList<>();
    nullRecord.add(null);
    assertThrows(
        NullPointerException.class,
        () -> new PayloadValues(new LayoutId("LOGREQ01"), values, nullRecord));
    PayloadValues payload = new PayloadValues(new LayoutId("LOGREQ01"), values, List.of());
    assertThrows(UnsupportedOperationException.class, () -> payload.records().clear());
    assertFalse(payload.toString().contains(secret.value()));
  }

  @Test
  void numericDigitLimitIsCheckedWithoutOverflow() {
    assertEquals(9, PayloadCodec.maximumForDigits(1));
    assertEquals(999_999_999_999_999_999L, PayloadCodec.maximumForDigits(18));
    assertThrows(LayoutValidationException.class, () -> PayloadCodec.maximumForDigits(0));
    assertThrows(LayoutValidationException.class, () -> PayloadCodec.maximumForDigits(19));
  }

  private static FieldValueSet minimumValues(List<FieldDefinition<?>> fields) {
    LinkedHashMap<String, FieldValue> values = new LinkedHashMap<>();
    for (FieldDefinition<?> field : fields) {
      if (field.presence() == Presence.FIXED) {
        continue;
      }
      FieldValue value =
          field.presence() == Presence.MANDATORY
              ? switch (field.wireType()) {
                case TEXT -> new FieldValue.Text("A");
                case NUMERIC -> new FieldValue.Numeric(0);
                case BOOLEAN -> new FieldValue.Flag(false);
              }
              : FieldValue.Unset.INSTANCE;
      values.put(field.name(), value);
    }
    return new FieldValueSet(values);
  }

  private static void assertWrongType(
      PayloadCodec codec, String layoutId, String fieldName, FieldValue wrongValue) {
    LayoutFields layout = LayoutFieldCatalog.standard().require(layoutId);
    LinkedHashMap<String, FieldValue> values = new LinkedHashMap<>();
    for (String name : minimumValues(layout.dataFields()).names()) {
      values.put(name, minimumValues(layout.dataFields()).getOrUnset(name));
    }
    values.put(fieldName, wrongValue);
    assertThrows(
        MessageEncodingException.class,
        () ->
            codec.encode(
                new PayloadValues(layout.id(), new FieldValueSet(values), List.of()), false));
  }

  private static void assertBadErrorFiller(
      PayloadCodec codec, String layoutId, int offset, byte badValue) {
    LayoutId id = new LayoutId(layoutId);
    byte[] data =
        codec.encode(new PayloadValues(id, FieldValueSet.empty(), List.of()), true).copyData();
    data[offset] = badValue;
    assertThrows(PermanentProtocolException.class, () -> codec.decode(id, data, List.of(), true));
  }
}
