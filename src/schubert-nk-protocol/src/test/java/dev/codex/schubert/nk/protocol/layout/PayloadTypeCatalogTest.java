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
  private static final int UUID_TEXT_LENGTH = 36;
  private static final String VALUE_FIELD_NAME = "value";
  private static final String SAFE_TEXT = "safe";

  @Test
  void allNamedTypesHaveIndependentDirectionalFieldMeaning() throws Exception {
    IndependentNamedFieldOracle.verifyAll();
  }

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
      for (String line = reader.readLine(); line != null; line = reader.readLine()) {
        if (line.startsWith("#")) {
          continue;
        }
        String[] columns = line.split("\\t", -1);
        assertEquals(3, columns.length, line);
        LayoutId layoutId = new LayoutId(columns[0]);
        assertEquals(columns[1], PayloadTypeCatalog.dataType(layoutId).getSimpleName(), columns[0]);
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
      int recordCount = layout.recordFields().isEmpty() ? 0 : 1;
      List<FieldValueSet> records =
          layout.recordFields().isEmpty()
              ? List.of()
              : List.of(minimumValues(layout, true, recordCount));
      PayloadValues values =
          new PayloadValues(layout.id(), minimumValues(layout, false, recordCount), records);

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
    PayloadValues unknownValues = new PayloadValues(unknown, FieldValueSet.empty(), List.of());
    assertThrows(UnsupportedLayoutException.class, () -> PayloadTypeCatalog.decode(unknownValues));
    assertThrows(UnsupportedLayoutException.class, () -> PayloadTypeCatalog.dataType(unknown));
    assertThrows(UnsupportedLayoutException.class, () -> PayloadTypeCatalog.recordType(unknown));

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
                    logout.layoutId(),
                    logout.data().fields(),
                    List.of(game.records().getFirst().fields()))));
  }

  @Test
  void typedModelsAndHelpersRejectNullMissingAndWrongKinds() {
    FieldValueSet text =
        new FieldValueSet(Map.of(VALUE_FIELD_NAME, new FieldValue.Text(SAFE_TEXT)));
    FieldValueSet numeric = new FieldValueSet(Map.of(VALUE_FIELD_NAME, new FieldValue.Numeric(7)));
    FieldValueSet flag = new FieldValueSet(Map.of(VALUE_FIELD_NAME, new FieldValue.Flag(true)));
    assertEquals(SAFE_TEXT, TypedFieldValues.requiredText(text, VALUE_FIELD_NAME).value());
    assertEquals(7, TypedFieldValues.requiredNumeric(numeric, VALUE_FIELD_NAME).value());
    assertTrue(TypedFieldValues.requiredFlag(flag, VALUE_FIELD_NAME).value());
    assertEquals(
        Optional.empty(), TypedFieldValues.optionalText(FieldValueSet.empty(), VALUE_FIELD_NAME));
    assertEquals(
        Optional.of(new FieldValue.Text(SAFE_TEXT)),
        TypedFieldValues.optionalText(text, VALUE_FIELD_NAME));
    assertSame(FieldValue.Unset.INSTANCE, TypedFieldValues.orUnset(Optional.empty()));
    assertEquals(
        new FieldValue.Text(SAFE_TEXT),
        TypedFieldValues.orUnset(Optional.of(new FieldValue.Text(SAFE_TEXT))));

    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredText(numeric, VALUE_FIELD_NAME));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredNumeric(flag, VALUE_FIELD_NAME));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredFlag(text, VALUE_FIELD_NAME));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.optionalText(numeric, VALUE_FIELD_NAME));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.requiredText(null, VALUE_FIELD_NAME));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.requiredText(text, null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.orUnset(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.requireEmpty(null));
    assertThrows(LayoutValidationException.class, () -> TypedFieldValues.requireEmpty(text));
    TypedFieldValues.requireEmpty(FieldValueSet.empty());

    TypedPayloadValues logout = typedMinimum("LOGREQ01", false);
    assertThrows(
        NullPointerException.class, () -> new TypedPayloadValues(null, logout.data(), List.of()));
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
    List<FieldValueSet> records = withRecord ? List.of(minimumValues(layout, true, 1)) : List.of();
    return PayloadTypeCatalog.decode(
        new PayloadValues(layout.id(), minimumValues(layout, false, records.size()), records));
  }

  static PayloadValues validPayload(String layoutId, int recordCount) {
    LayoutFields layout = LayoutFieldCatalog.standard().require(layoutId);
    if (recordCount < 0 || (recordCount > 0 && layout.recordFields().isEmpty())) {
      throw new IllegalArgumentException("invalid fixture record count");
    }
    List<FieldValueSet> records =
        java.util.stream.IntStream.range(0, recordCount)
            .mapToObj(index -> minimumValues(layout, true, recordCount))
            .toList();
    return new PayloadValues(layout.id(), minimumValues(layout, false, recordCount), records);
  }

  private static FieldValueSet minimumValues(
      LayoutFields layout, boolean recordArea, int recordCount) {
    List<FieldDefinition<?>> fields = recordArea ? layout.recordFields() : layout.dataFields();
    LinkedHashMap<String, FieldValue> values = new LinkedHashMap<>();
    for (FieldDefinition<?> field : fields) {
      if (field.presence() == Presence.FIXED) {
        continue;
      }
      FieldValue value =
          field.presence() == Presence.MANDATORY
              ? minimumRequiredValue(layout.id().value(), field, recordCount)
              : conditionalValue(layout.id().value(), field);
      values.put(field.name(), value);
    }
    return new FieldValueSet(values);
  }

  private static FieldValue minimumRequiredValue(
      String layoutId, FieldDefinition<?> field, int recordCount) {
    return switch (field.wireType()) {
      case TEXT -> new FieldValue.Text(minimumText(layoutId, field));
      case NUMERIC -> new FieldValue.Numeric(minimumNumeric(layoutId, field, recordCount));
      case BOOLEAN -> new FieldValue.Flag(false);
    };
  }

  private static long minimumNumeric(String layoutId, FieldDefinition<?> field, int recordCount) {
    if (field.length() == JstWireTimestamp.WIRE_LENGTH) {
      return 20260902123456789L;
    }
    if (field.length() == 12 && N12_ID_FIELDS.contains(field.name())) {
      return 1;
    }
    return switch (field.name()) {
      case "Page", "Effective page", "Line番号", "Entry sequence", "File件数", "出現件数" -> 1;
      case "File byte長" -> layoutId.equals("SCNRSP01") ? 0 : 1;
      case "Page size" ->
          Set.of("USRREQ01", "USRRSP01", "NTSREQ01", "NTSRSP01", "QSSREQ01", "QSSRSP01")
                  .contains(layoutId)
              ? 50
              : 100;
      case "Total count" -> recordCount;
      case "Total pages" -> 1;
      case "First result", "Last result" -> recordCount;
      default -> 0;
    };
  }

  private static FieldValue conditionalValue(String layoutId, FieldDefinition<?> field) {
    String name = field.name();
    if (layoutId.equals("LGNRSP01")) {
      return switch (name) {
        case "Username" -> new FieldValue.Text("user");
        case "Role" -> new FieldValue.Text("USER");
        case "認証context ID" -> new FieldValue.Text("a".repeat(64));
        case "発行日時" -> new FieldValue.Text("20260902123456789");
        case "期限日時" -> new FieldValue.Text("20260902133456789");
        default -> FieldValue.Unset.INSTANCE;
      };
    }
    if (layoutId.equals("NTDRSP01")) {
      return switch (name) {
        case "質問本文" -> new FieldValue.Text("A");
        case "Question ID" -> new FieldValue.Text("1");
        default -> FieldValue.Unset.INSTANCE;
      };
    }
    if (layoutId.equals("NTCRSP01")) {
      return switch (name) {
        case "更新後状態" -> new FieldValue.Text("CANCELLED");
        case "取消日時" -> new FieldValue.Text("20260902123456789");
        default -> FieldValue.Unset.INSTANCE;
      };
    }
    return FieldValue.Unset.INSTANCE;
  }

  private static String minimumText(String layoutId, FieldDefinition<?> field) {
    if (field.name().contains("SHA-256")) {
      return "a".repeat(64);
    }
    if (field.length() == UUID_TEXT_LENGTH) {
      return "123e4567-e89b-12d3-a456-426614174000";
    }
    return switch (field.name()) {
      case "Username" -> "user";
      case "Password" -> "PublicTestPassword";
      case "Initial Password", "New Password" -> "PublicTest12";
      case "Client address", "Remote address" -> "127.0.0.1";
      case "受付ID" -> "01HABCDEFGJKMNPQRSTVWXYZ01";
      case "Content disposition", "Disposition", "Delivery mode" -> "I";
      case "Pair role" -> "N";
      case "Role", "New role" -> "USER";
      case "Level" -> "INFO";
      case "Log type" -> layoutId.equals("WLGEVT01") ? "REQUEST" : "ACTION";
      case "State" -> "ACTIVE";
      case "内部状態" -> "RECEIVED";
      case "回答状態" -> "UNANSWERED";
      case "通知区分" -> "ACCEPTED";
      case "Entry type" -> "dialogue";
      case "Game code" -> "NUKITASHI1";
      case "MIME type" -> "audio/ogg";
      case "HTTP status" -> "200";
      case "Elapsed ms" -> "0";
      case "HTTP method" -> "GET";
      case "Path" -> "/safe";
      case "Category" -> field.semanticRule().replace("`", "").startsWith("MAIN/") ? "MAIN" : "A";
      default -> layoutId.equals("WLGEVT01") && field.name().equals("Message") ? SAFE_TEXT : "A";
    };
  }
}
