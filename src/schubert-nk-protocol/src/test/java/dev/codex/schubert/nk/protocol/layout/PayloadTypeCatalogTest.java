package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.time.JstWireTimestamp;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.Test;

class PayloadTypeCatalogTest {
  private static final Set<String> N12_ID_FIELDS =
      Set.of(
          "Async job ID",
          "Audio ID",
          "Entry ID",
          "Log ID",
          "Notification ID",
          "Question ID",
          "Script file ID",
          "Speaker ID",
          "User ID");

  @Test
  void explicitCatalogMatchesIndependentSs323NamedTypeFixture() throws IOException {
    int rowCount = 0;
    try (BufferedReader reader =
        new BufferedReader(
            new InputStreamReader(
                Objects.requireNonNull(
                    getClass().getResourceAsStream("/protocol/named-types-ss323.tsv")),
                StandardCharsets.UTF_8))) {
      for (String line; (line = reader.readLine()) != null; ) {
        if (line.startsWith("#")) {
          continue;
        }
        String[] columns = line.split("\\t", -1);
        assertEquals(3, columns.length, line);
        LayoutId layoutId = new LayoutId(columns[0]);
        assertEquals(
            columns[1], PayloadTypeCatalog.dataType(layoutId).getSimpleName(), columns[0]);
        Optional<Class<? extends PayloadRecord>> recordType =
            PayloadTypeCatalog.recordType(layoutId);
        if (columns[2].equals("-")) {
          assertTrue(recordType.isEmpty(), columns[0]);
        } else {
          assertEquals(columns[2], recordType.orElseThrow().getSimpleName(), columns[0]);
        }
        rowCount++;
      }
    }
    assertEquals(64, rowCount);
  }

  @Test
  void allSixtyFourLayoutsRoundTripThroughSixtyNineExplicitNamedTypes() {
    Set<Class<?>> namedTypes = new HashSet<>();
    int layoutsWithRecords = 0;

    for (LayoutFields layout : LayoutFieldCatalog.standard().all()) {
      List<FieldValueSet> records =
          layout.recordFields().isEmpty()
              ? List.of()
              : List.of(minimumValues(layout.recordFields()));
      PayloadValues values =
          new PayloadValues(layout.id(), minimumValues(layout.dataFields()), records);

      TypedPayloadValues typed = PayloadTypeCatalog.decode(values);
      assertEquals(values, PayloadTypeCatalog.encode(typed), layout.id().value());
      assertSame(PayloadTypeCatalog.dataType(layout.id()), typed.data().getClass());
      assertEquals(
          typed.data().getClass().getSimpleName() + "[REDACTED]",
          typed.data().toString(),
          layout.id().value());
      namedTypes.add(typed.data().getClass());

      Optional<Class<? extends PayloadRecord>> recordType =
          PayloadTypeCatalog.recordType(layout.id());
      if (layout.recordFields().isEmpty()) {
        assertTrue(recordType.isEmpty(), layout.id().value());
        assertTrue(typed.records().isEmpty(), layout.id().value());
      } else {
        layoutsWithRecords++;
        assertTrue(recordType.isPresent(), layout.id().value());
        assertSame(recordType.orElseThrow(), typed.records().getFirst().getClass());
        assertEquals(
            typed.records().getFirst().getClass().getSimpleName() + "[REDACTED]",
            typed.records().getFirst().toString(),
            layout.id().value());
        namedTypes.add(typed.records().getFirst().getClass());
      }
      assertFalse(typed.toString().contains("FieldValue"));
    }

    assertEquals(14, layoutsWithRecords);
    assertEquals(69, namedTypes.size());
  }

  @Test
  void optionalFieldsSupportUnsetAndPresentValuesWithoutLosingWireNames() {
    LayoutFields speaker = LayoutFieldCatalog.standard().require("SPKREQ01");
    PayloadValues unset =
        new PayloadValues(
            speaker.id(),
            new FieldValueSet(Map.of("Game code", FieldValue.Unset.INSTANCE)),
            List.of());
    assertEquals(unset, PayloadTypeCatalog.encode(PayloadTypeCatalog.decode(unset)));

    PayloadValues present =
        new PayloadValues(
            speaker.id(),
            new FieldValueSet(Map.of("Game code", new FieldValue.Text("NUKITASHI1"))),
            List.of());
    TypedPayloadValues typed = PayloadTypeCatalog.decode(present);
    assertEquals(present, PayloadTypeCatalog.encode(typed));
    assertFalse(typed.data().toString().contains("NUKITASHI1"));
  }

  @Test
  void catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes() {
    LayoutId unknown = new LayoutId("ZZZREQ01");
    PayloadValues unknownValues =
        new PayloadValues(unknown, FieldValueSet.empty(), List.of());
    assertThrows(UnsupportedLayoutException.class, () -> PayloadTypeCatalog.decode(unknownValues));
    assertThrows(
        UnsupportedLayoutException.class,
        () -> PayloadTypeCatalog.dataType(unknown));
    assertThrows(
        UnsupportedLayoutException.class,
        () -> PayloadTypeCatalog.recordType(unknown));

    TypedPayloadValues logout = typedMinimum("LOGREQ01", false);
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadTypeCatalog.encode(
                new TypedPayloadValues(new LayoutId("LGNREQ01"), logout.data(), List.of())));

    TypedPayloadValues game = typedMinimum("GAMRSP01", true);
    TypedPayloadValues speaker = typedMinimum("SPKRSP01", false);
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadTypeCatalog.encode(
                new TypedPayloadValues(speaker.layoutId(), speaker.data(), game.records())));

    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadTypeCatalog.encode(
                new TypedPayloadValues(logout.layoutId(), logout.data(), game.records())));
    assertThrows(
        LayoutValidationException.class,
        () ->
            PayloadTypeCatalog.decode(
                new PayloadValues(
                    logout.layoutId(), logout.data().fields(), List.of(game.records().getFirst().fields()))));
  }

  @Test
  void typedModelsAndHelpersRejectNullMissingAndWrongKinds() {
    FieldValueSet text = new FieldValueSet(Map.of("value", new FieldValue.Text("safe")));
    FieldValueSet numeric = new FieldValueSet(Map.of("value", new FieldValue.Numeric(7)));
    FieldValueSet flag = new FieldValueSet(Map.of("value", new FieldValue.Flag(true)));
    assertEquals("safe", TypedFieldValues.requiredText(text, "value").value());
    assertEquals(7, TypedFieldValues.requiredNumeric(numeric, "value").value());
    assertTrue(TypedFieldValues.requiredFlag(flag, "value").value());
    assertEquals(Optional.empty(), TypedFieldValues.optionalText(FieldValueSet.empty(), "value"));
    assertEquals(
        Optional.of(new FieldValue.Text("safe")), TypedFieldValues.optionalText(text, "value"));
    assertSame(FieldValue.Unset.INSTANCE, TypedFieldValues.orUnset(Optional.empty()));
    assertEquals(new FieldValue.Text("safe"), TypedFieldValues.orUnset(Optional.of(new FieldValue.Text("safe"))));

    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredText(numeric, "value"));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredNumeric(flag, "value"));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredFlag(text, "value"));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.optionalText(numeric, "value"));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.requiredText(null, "value"));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.requiredText(text, null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.orUnset(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.requireEmpty(null));
    assertThrows(LayoutValidationException.class, () -> TypedFieldValues.requireEmpty(text));
    TypedFieldValues.requireEmpty(FieldValueSet.empty());

    TypedPayloadValues logout = typedMinimum("LOGREQ01", false);
    assertThrows(
        NullPointerException.class,
        () -> new TypedPayloadValues(null, logout.data(), List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new TypedPayloadValues(logout.layoutId(), null, List.of()));
    assertThrows(
        NullPointerException.class,
        () -> new TypedPayloadValues(logout.layoutId(), logout.data(), null));
    List<PayloadRecord> nullRecord = new ArrayList<>();
    nullRecord.add(null);
    assertThrows(
        NullPointerException.class,
        () -> new TypedPayloadValues(logout.layoutId(), logout.data(), nullRecord));
    assertThrows(UnsupportedOperationException.class, () -> logout.records().clear());
    assertThrows(NullPointerException.class, () -> PayloadTypeCatalog.decode(null));
    assertThrows(NullPointerException.class, () -> PayloadTypeCatalog.encode(null));
    assertThrows(NullPointerException.class, () -> PayloadTypeCatalog.dataType(null));
  }

  private static TypedPayloadValues typedMinimum(String layoutId, boolean withRecord) {
    LayoutFields layout = LayoutFieldCatalog.standard().require(layoutId);
    List<FieldValueSet> records =
        withRecord ? List.of(minimumValues(layout.recordFields())) : List.of();
    return PayloadTypeCatalog.decode(
        new PayloadValues(layout.id(), minimumValues(layout.dataFields()), records));
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
                case TEXT -> new FieldValue.Text(minimumText(field));
                case NUMERIC ->
                    new FieldValue.Numeric(
                        field.length() == JstWireTimestamp.WIRE_LENGTH
                            ? 20260902123456789L
                            : field.length() == 12 && N12_ID_FIELDS.contains(field.name())
                                ? 1
                                : 0);
                case BOOLEAN -> new FieldValue.Flag(false);
              }
              : FieldValue.Unset.INSTANCE;
      values.put(field.name(), value);
    }
    return new FieldValueSet(values);
  }

  private static String minimumText(FieldDefinition<?> field) {
    if (field.name().contains("SHA-256")) {
      return "a".repeat(64);
    }
    if (field.length() == 36) {
      return "123e4567-e89b-12d3-a456-426614174000";
    }
    return switch (field.name()) {
      case "Content disposition", "Disposition", "Delivery mode" -> "I";
      case "Pair role" -> "N";
      case "Role", "New role" -> "USER";
      case "Level" -> "INFO";
      case "Log type" -> "ACTION";
      case "State" -> "ACTIVE";
      case "内部状態" -> "RECEIVED";
      case "回答状態" -> "ANSWERED";
      case "通知区分" -> "ACCEPTED";
      case "Entry type" -> "dialogue";
      case "Game code" -> "NUKITASHI1";
      case "MIME type" -> "audio/ogg";
      case "HTTP status" -> "200";
      case "Elapsed ms" -> "0";
      case "Category" ->
          field.semanticRule().replace("`", "").startsWith("MAIN/") ? "MAIN" : "A";
      default -> "A";
    };
  }
}
