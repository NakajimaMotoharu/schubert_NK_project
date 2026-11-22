package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class LayoutMetadataTest {
  private static final String LOGIN_REQUEST_LAYOUT = "LGNREQ01";
  private static final String CUSTOM_REQUEST_LAYOUT = "ABCREQ01";
  private static final String CUSTOM_RESPONSE_LAYOUT = "ABCRSP01";
  private static final String SAMPLE_FIELD_NAME = "name";
  private static final String FIELD_RULE_TEXT = "rule";

  @Test
  void registryMatchesIndependentUi233Catalog() throws IOException {
    List<String> expected;
    try (var input = getClass().getResourceAsStream("/protocol/layouts-ui233.tsv")) {
      if (input == null) {
        throw new AssertionError("layout fixture missing");
      }
      try (var reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
        expected = reader.lines().filter(line -> !line.startsWith("#")).toList();
      }
    }
    List<String> actual =
        LayoutRegistry.standard().all().stream()
            .map(
                definition ->
                    String.join(
                        "\t",
                        definition.id().value(),
                        Character.toString(definition.messageKind().wireValue()),
                        Character.toString(definition.interactionKind().wireValue()),
                        Integer.toString(definition.dataLength()),
                        Integer.toString(definition.recordLength()),
                        Integer.toString(definition.maximumRecordCount()),
                        Integer.toString(definition.maximumTotalLength())))
            .toList();

    assertEquals(64, actual.size());
    assertEquals(expected, actual);
    assertEquals(
        LOGIN_REQUEST_LAYOUT,
        LayoutRegistry.standard().require(LOGIN_REQUEST_LAYOUT, 1).id().value());
    assertEquals(
        LOGIN_REQUEST_LAYOUT,
        LayoutRegistry.standard().require(new LayoutId(LOGIN_REQUEST_LAYOUT), 1).id().value());
    assertThrows(
        UnsupportedLayoutException.class,
        () -> LayoutRegistry.standard().require(LOGIN_REQUEST_LAYOUT, 2));
    assertThrows(
        NullPointerException.class, () -> LayoutRegistry.standard().require((String) null, 1));
    assertThrows(
        NullPointerException.class, () -> LayoutRegistry.standard().require((LayoutId) null, 1));
    assertThrows(
        UnsupportedOperationException.class, () -> LayoutRegistry.standard().all().clear());
  }

  @Test
  void registryRejectsEmptyNullDuplicateAndKindMismatches() {
    LayoutDefinition request =
        d(CUSTOM_REQUEST_LAYOUT, MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0);
    assertThrows(NullPointerException.class, () -> LayoutRegistry.validateDefinitions(null));
    assertThrows(
        LayoutValidationException.class, () -> LayoutRegistry.validateDefinitions(List.of()));
    ArrayList<LayoutDefinition> nullDefinition = new ArrayList<>();
    nullDefinition.add(null);
    assertThrows(
        NullPointerException.class, () -> LayoutRegistry.validateDefinitions(nullDefinition));
    assertThrows(
        LayoutValidationException.class,
        () -> LayoutRegistry.validateDefinitions(List.of(request, request)));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutRegistry.validateDefinitions(
                List.of(
                    d(
                        CUSTOM_REQUEST_LAYOUT,
                        MessageKind.RESPONSE,
                        InteractionKind.SYNCHRONOUS,
                        0,
                        0,
                        0))));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutRegistry.validateDefinitions(
                List.of(
                    d(
                        CUSTOM_RESPONSE_LAYOUT,
                        MessageKind.REQUEST,
                        InteractionKind.SYNCHRONOUS,
                        0,
                        0,
                        0))));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutRegistry.validateDefinitions(
                List.of(d("ABCXXX01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0))));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutRegistry.validateDefinitions(
                List.of(
                    d("QWKREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 64, 0, 0))));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutRegistry.validateDefinitions(
                List.of(
                    d(
                        CUSTOM_REQUEST_LAYOUT,
                        MessageKind.REQUEST,
                        InteractionKind.ASYNC_ACCEPTANCE,
                        0,
                        0,
                        0))));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutRegistry.validateDefinitions(
                List.of(
                    d("QSBREQ01", MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 4_144, 0, 0))));
    LayoutRegistry.validateDefinitions(List.of(request));
  }

  @Test
  void layoutDefinitionChecksEveryLengthAndKindInvariant() {
    LayoutDefinition definition =
        d(CUSTOM_RESPONSE_LAYOUT, MessageKind.RESPONSE, InteractionKind.SYNCHRONOUS, 8, 10, 2);
    assertEquals(284, definition.maximumTotalLength());
    assertEquals(264, definition.totalLengthFor(0));
    assertEquals(274, definition.totalLengthFor(1));
    assertEquals(284, definition.totalLengthFor(2));
    assertThrows(LayoutValidationException.class, () -> definition.totalLengthFor(-1));
    assertThrows(LayoutValidationException.class, () -> definition.totalLengthFor(3));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT),
                2,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                0,
                0,
                0));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT),
                1,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                -1,
                0,
                0));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT),
                1,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                1_000_000,
                0,
                0));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_RESPONSE_LAYOUT),
                1,
                MessageKind.RESPONSE,
                InteractionKind.SYNCHRONOUS,
                0,
                1,
                0));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_RESPONSE_LAYOUT),
                1,
                MessageKind.RESPONSE,
                InteractionKind.SYNCHRONOUS,
                0,
                0,
                1));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT),
                1,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                999_999,
                0,
                0));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_RESPONSE_LAYOUT),
                1,
                MessageKind.RESPONSE,
                InteractionKind.SYNCHRONOUS,
                0,
                999_999,
                999_999));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT),
                1,
                MessageKind.REQUEST,
                InteractionKind.SYNCHRONOUS,
                0,
                0,
                0,
                257));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId("ABCEVT01"),
                1,
                MessageKind.EVENT,
                InteractionKind.SYNCHRONOUS,
                0,
                0,
                0));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT),
                1,
                MessageKind.REQUEST,
                InteractionKind.INTERNAL,
                0,
                0,
                0));
    assertEquals(
        256,
        new LayoutDefinition(
                new LayoutId("ABCEVT01"), 1, MessageKind.EVENT, InteractionKind.INTERNAL, 0, 0, 0)
            .maximumTotalLength());
    assertThrows(
        NullPointerException.class,
        () ->
            new LayoutDefinition(
                null, 1, MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 0, 0, 0));
    assertThrows(
        NullPointerException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT),
                1,
                null,
                InteractionKind.SYNCHRONOUS,
                0,
                0,
                0));
    assertThrows(
        NullPointerException.class,
        () ->
            new LayoutDefinition(
                new LayoutId(CUSTOM_REQUEST_LAYOUT), 1, MessageKind.REQUEST, null, 0, 0, 0));
  }

  @Test
  void layoutIdAndFieldDefinitionAreStrictAndOneBased() {
    LayoutId first = new LayoutId(CUSTOM_REQUEST_LAYOUT);
    LayoutId second = new LayoutId(CUSTOM_RESPONSE_LAYOUT);
    assertTrue(first.compareTo(second) < 0);
    assertEquals(CUSTOM_REQUEST_LAYOUT, first.toString());
    assertThrows(NullPointerException.class, () -> first.compareTo(null));
    assertThrows(NullPointerException.class, () -> new LayoutId(null));
    assertThrows(LayoutValidationException.class, () -> new LayoutId("short"));
    assertThrows(LayoutValidationException.class, () -> new LayoutId("abcREQ01"));

    FieldDefinition<String> text =
        new FieldDefinition<>(
            FieldArea.DATA,
            SAMPLE_FIELD_NAME,
            1,
            8,
            WireType.TEXT,
            Presence.MANDATORY,
            Padding.SPACE_RIGHT,
            String.class,
            "NFC");
    FieldDefinition<Long> numeric =
        new FieldDefinition<>(
            FieldArea.RECORD,
            "count",
            9,
            3,
            WireType.NUMERIC,
            Presence.OPTIONAL,
            Padding.ZERO_LEFT,
            Long.class,
            "0..999");
    FieldDefinition<Boolean> bool =
        new FieldDefinition<>(
            FieldArea.HEADER,
            "flag",
            12,
            1,
            WireType.BOOLEAN,
            Presence.CONDITIONAL,
            Padding.NONE,
            Boolean.class,
            "0/1");
    assertEquals(8, text.end());
    assertEquals(11, numeric.end());
    assertEquals(12, bool.end());
    assertEquals(3, FieldArea.values().length);
    assertEquals(3, WireType.values().length);
    assertEquals(4, Presence.values().length);
    assertEquals(3, Padding.values().length);
    assertThrows(
        LayoutValidationException.class,
        () -> field("", 1, 1, WireType.TEXT, Padding.SPACE_RIGHT, FIELD_RULE_TEXT));
    assertThrows(
        LayoutValidationException.class,
        () -> field(SAMPLE_FIELD_NAME, 1, 1, WireType.TEXT, Padding.SPACE_RIGHT, " "));
    assertThrows(
        LayoutValidationException.class,
        () -> field(SAMPLE_FIELD_NAME, 0, 1, WireType.TEXT, Padding.SPACE_RIGHT, FIELD_RULE_TEXT));
    assertThrows(
        LayoutValidationException.class,
        () -> field(SAMPLE_FIELD_NAME, 1, 0, WireType.TEXT, Padding.SPACE_RIGHT, FIELD_RULE_TEXT));
    assertThrows(
        LayoutValidationException.class,
        () ->
            field(
                SAMPLE_FIELD_NAME,
                Integer.MAX_VALUE,
                2,
                WireType.TEXT,
                Padding.SPACE_RIGHT,
                FIELD_RULE_TEXT));
    assertThrows(
        LayoutValidationException.class,
        () ->
            new FieldDefinition<>(
                FieldArea.DATA,
                SAMPLE_FIELD_NAME,
                1,
                99,
                1,
                WireType.TEXT,
                Presence.FIXED,
                Padding.SPACE_RIGHT,
                String.class,
                FIELD_RULE_TEXT));
    assertThrows(
        LayoutValidationException.class,
        () -> field(SAMPLE_FIELD_NAME, 1, 1, WireType.TEXT, Padding.NONE, FIELD_RULE_TEXT));
    assertThrows(
        LayoutValidationException.class,
        () -> field(SAMPLE_FIELD_NAME, 1, 1, WireType.NUMERIC, Padding.NONE, FIELD_RULE_TEXT));
    assertThrows(
        LayoutValidationException.class,
        () ->
            field(SAMPLE_FIELD_NAME, 1, 1, WireType.BOOLEAN, Padding.SPACE_RIGHT, FIELD_RULE_TEXT));
    assertThrows(
        NullPointerException.class,
        () ->
            new FieldDefinition<>(
                null,
                "n",
                1,
                1,
                WireType.TEXT,
                Presence.MANDATORY,
                Padding.SPACE_RIGHT,
                String.class,
                "r"));
    assertThrows(
        NullPointerException.class,
        () ->
            new FieldDefinition<>(
                FieldArea.DATA,
                null,
                1,
                1,
                WireType.TEXT,
                Presence.MANDATORY,
                Padding.SPACE_RIGHT,
                String.class,
                "r"));
  }

  private static FieldDefinition<String> field(
      String name, int start, int length, WireType type, Padding padding, String rule) {
    return new FieldDefinition<>(
        FieldArea.DATA, name, start, length, type, Presence.FIXED, padding, String.class, rule);
  }

  private static LayoutDefinition d(
      String id,
      MessageKind kind,
      InteractionKind interaction,
      int dataLength,
      int recordLength,
      int count) {
    return new LayoutDefinition(
        new LayoutId(id), 1, kind, interaction, dataLength, recordLength, count);
  }
}
