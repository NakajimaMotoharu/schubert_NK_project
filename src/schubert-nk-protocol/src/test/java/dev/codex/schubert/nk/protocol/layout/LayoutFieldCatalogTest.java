package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.InteractionKind;
import dev.codex.schubert.nk.protocol.header.MessageKind;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class LayoutFieldCatalogTest {
  private static final String LOGIN_REQUEST_LAYOUT = "LGNREQ01";
  private static final String DATA_AREA_TEXT = "DATA";
  private static final String FIELD_NAME_TEXT = "Name";
  private static final String FIELD_RULE_TEXT = "rule";

  @Test
  void catalogMatchesIndependentUi234To236Fixture() throws IOException {
    String fixture = fixture();
    List<String> expected =
        fixture.lines().filter(line -> !line.isBlank() && !line.startsWith("#")).toList();
    LayoutFieldCatalog catalog = LayoutFieldCatalog.standard();

    assertEquals(64, catalog.all().size());
    assertEquals(389, catalog.fieldCount());
    assertEquals(expected, catalog.tsvRows());
    assertEquals(
        expected, LayoutFieldCatalog.parse(" \n" + fixture, LayoutRegistry.standard()).tsvRows());
    assertEquals(
        4,
        catalog.all().stream()
            .filter(fields -> fields.dataFields().isEmpty() && fields.recordFields().isEmpty())
            .count());
    assertEquals(LOGIN_REQUEST_LAYOUT, catalog.require(LOGIN_REQUEST_LAYOUT).id().value());
    assertEquals("WLGEVT01", catalog.require(new LayoutId("WLGEVT01")).id().value());
    assertThrows(UnsupportedLayoutException.class, () -> catalog.require("ZZZREQ01"));
    assertThrows(NullPointerException.class, () -> catalog.require((String) null));
    assertThrows(NullPointerException.class, () -> catalog.require((LayoutId) null));
    assertThrows(UnsupportedOperationException.class, () -> catalog.all().clear());
    assertThrows(UnsupportedOperationException.class, () -> catalog.tsvRows().clear());

    List<FieldDefinition<?>> fields =
        catalog.all().stream()
            .flatMap(
                layout ->
                    java.util.stream.Stream.concat(
                        layout.dataFields().stream(), layout.recordFields().stream()))
            .toList();
    assertSame(
        String.class,
        fields.stream()
            .filter(field -> field.wireType() == WireType.TEXT)
            .findFirst()
            .orElseThrow()
            .javaType());
    assertSame(
        Long.class,
        fields.stream()
            .filter(field -> field.wireType() == WireType.NUMERIC)
            .findFirst()
            .orElseThrow()
            .javaType());
    assertSame(
        Boolean.class,
        fields.stream()
            .filter(field -> field.wireType() == WireType.BOOLEAN)
            .findFirst()
            .orElseThrow()
            .javaType());
  }

  @Test
  void parserRejectsMalformedUnknownAndDuplicateRows() throws IOException {
    LayoutRegistry registry = LayoutRegistry.standard();
    assertThrows(NullPointerException.class, () -> LayoutFieldCatalog.parse(null, registry));
    assertThrows(NullPointerException.class, () -> LayoutFieldCatalog.parse(fixture(), null));
    assertThrows(LayoutValidationException.class, () -> LayoutFieldCatalog.parse("", registry));
    assertThrows(
        LayoutValidationException.class,
        () -> LayoutFieldCatalog.parse("LGNREQ01\tDATA\ttoo-few", registry));
    assertThrows(
        UnsupportedLayoutException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    "ZZZREQ01",
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "1",
                    "1",
                    "X",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    "HEADER",
                    FIELD_NAME_TEXT,
                    "1",
                    "1",
                    "X",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "1",
                    "1",
                    "Z",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "1",
                    "1",
                    "X",
                    "Z",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "1",
                    "384",
                    "X",
                    "F",
                    "fixed"),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row("WLGEVT01", DATA_AREA_TEXT, "Other", "1", "2080", "X", "F", "fixed"),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "x",
                    "1",
                    "X",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "0",
                    "1",
                    "X",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "1",
                    "-1",
                    "X",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    "",
                    "1",
                    "384",
                    "X",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "1",
                    "384",
                    "X",
                    "M",
                    " "),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                        LOGIN_REQUEST_LAYOUT,
                        DATA_AREA_TEXT,
                        FIELD_NAME_TEXT,
                        "1",
                        "64",
                        "X",
                        "M",
                        FIELD_RULE_TEXT)
                    + row(
                        LOGIN_REQUEST_LAYOUT,
                        DATA_AREA_TEXT,
                        FIELD_NAME_TEXT,
                        "65",
                        "320",
                        "X",
                        "M",
                        FIELD_RULE_TEXT),
                registry));
    assertThrows(
        LayoutValidationException.class,
        () ->
            LayoutFieldCatalog.parse(
                row(
                    LOGIN_REQUEST_LAYOUT,
                    DATA_AREA_TEXT,
                    FIELD_NAME_TEXT,
                    "2",
                    "383",
                    "X",
                    "M",
                    FIELD_RULE_TEXT),
                registry));
  }

  @Test
  void layoutFieldsRejectWrongAreaGapLengthAndNull() {
    LayoutDefinition layout =
        new LayoutDefinition(
            new LayoutId("ABCREQ01"), 1, MessageKind.REQUEST, InteractionKind.SYNCHRONOUS, 1, 0, 0);
    FieldDefinition<String> valid = field(FieldArea.DATA, 1, 1);
    LayoutFields fields = new LayoutFields(layout, List.of(valid), List.of());
    assertEquals("ABCREQ01", fields.id().value());
    assertThrows(UnsupportedOperationException.class, () -> fields.dataFields().clear());
    assertThrows(NullPointerException.class, () -> new LayoutFields(null, List.of(), List.of()));
    assertThrows(NullPointerException.class, () -> new LayoutFields(layout, null, List.of()));
    assertThrows(NullPointerException.class, () -> new LayoutFields(layout, List.of(), null));
    ArrayList<FieldDefinition<?>> withNull = new ArrayList<>();
    withNull.add(null);
    assertThrows(NullPointerException.class, () -> new LayoutFields(layout, withNull, List.of()));
    assertThrows(
        LayoutValidationException.class,
        () -> new LayoutFields(layout, List.of(field(FieldArea.RECORD, 1, 1)), List.of()));
    assertThrows(
        LayoutValidationException.class,
        () -> new LayoutFields(layout, List.of(field(FieldArea.DATA, 2, 1)), List.of()));
    assertThrows(
        LayoutValidationException.class,
        () -> new LayoutFields(layout, List.of(field(FieldArea.DATA, 1, 2)), List.of()));
    assertThrows(
        LayoutValidationException.class,
        () -> new LayoutFields(layout, List.of(valid), List.of(field(FieldArea.RECORD, 1, 1))));
  }

  private static String fixture() throws IOException {
    try (var input =
        LayoutFieldCatalogTest.class.getResourceAsStream("/protocol/fields-ui234-236.tsv")) {
      if (input == null) {
        throw new AssertionError("field fixture missing");
      }
      try (var reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
        return reader.lines().collect(java.util.stream.Collectors.joining("\n", "", "\n"));
      }
    }
  }

  private static String row(
      String layout,
      String area,
      String name,
      String start,
      String length,
      String wire,
      String presence,
      String rule) {
    return String.join("\t", layout, area, name, start, length, wire, presence, rule) + '\n';
  }

  private static FieldDefinition<String> field(FieldArea area, int start, int length) {
    return new FieldDefinition<>(
        area,
        FIELD_NAME_TEXT,
        start,
        length,
        WireType.TEXT,
        Presence.MANDATORY,
        Padding.SPACE_RIGHT,
        String.class,
        FIELD_RULE_TEXT);
  }
}
