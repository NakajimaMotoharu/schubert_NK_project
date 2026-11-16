package dev.codex.schubert.nk.protocol.layout.semantic;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.function.Function;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

/** PT-PRO-WIREVALUE001..004; MSG001..011/UI232..236/SS323/333/351/354; no wire-table changes. */
final class WireEnumCatalogValueContractTest {
  private static final String ERROR_ROW = "ERROR=ERROR";
  private static final List<Catalog<?>> CATALOGS =
      List.of(
          catalog(
              "AnimationCategory",
              AnimationCategory::values,
              AnimationCategory::valueOf,
              "MAIN=MAIN",
              "SUBTRACK=SUBTRACK",
              "OVA=OVA"),
          catalog(
              "AnimationListCategory",
              AnimationListCategory::values,
              AnimationListCategory::valueOf,
              "MAIN=MAIN",
              "OVA=OVA"),
          catalog(
              "AnswerState",
              AnswerState::values,
              AnswerState::valueOf,
              "ANSWERED=ANSWERED",
              "UNANSWERED=UNANSWERED",
              ERROR_ROW),
          catalog(
              "ContentDisposition",
              ContentDisposition::values,
              ContentDisposition::valueOf,
              "INLINE=I",
              "ATTACHMENT=A"),
          catalog(
              "DeliveryMode", DeliveryMode::values, DeliveryMode::valueOf, "INLINE=I", "FILE=F"),
          catalog(
              "EntryType",
              EntryType::values,
              EntryType::valueOf,
              "DIALOGUE=dialogue",
              "NARRATION=narration"),
          catalog(
              "GameCode",
              GameCode::values,
              GameCode::valueOf,
              "NUKITASHI_1=NUKITASHI1",
              "NUKITASHI_2=NUKITASHI2"),
          catalog(
              "LogLevel", LogLevel::values, LogLevel::valueOf, "INFO=INFO", "WARN=WARN", ERROR_ROW),
          catalog(
              "LogType",
              LogType::values,
              LogType::valueOf,
              "ACTION=ACTION",
              "REQUEST=REQUEST",
              "SECURITY=SECURITY",
              "MQ=MQ",
              "SYSTEM=SYSTEM",
              "BATCH=BATCH"),
          catalog(
              "MediaMimeType",
              MediaMimeType::values,
              MediaMimeType::valueOf,
              "AUDIO_MP4=audio/mp4",
              "AUDIO_MPEG=audio/mpeg",
              "AUDIO_OGG=audio/ogg",
              "AUDIO_WAV=audio/wav",
              "AUDIO_FLAC=audio/flac",
              "VIDEO_MP4=video/mp4"),
          catalog(
              "NotificationErrorCode",
              NotificationErrorCode::values,
              NotificationErrorCode::valueOf,
              "PROCESS_FAILED=PROCESS_FAILED",
              "SYSTEM_UNAVAILABLE=SYSTEM_UNAVAIL",
              "RESOURCE_LIMIT=RESOURCE_LIMIT",
              "DATA_INTEGRITY=DATA_INTEGRITY",
              "PROTOCOL_ERROR=PROTOCOL_ERROR"),
          catalog(
              "NotificationState",
              NotificationState::values,
              NotificationState::valueOf,
              "RECEIVED=RECEIVED",
              "PROCESSING=PROCESSING",
              "COMPLETED=COMPLETED",
              ERROR_ROW,
              "CANCELLED=CANCELLED"),
          catalog(
              "NotificationType",
              NotificationType::values,
              NotificationType::valueOf,
              "ACCEPTED=ACCEPTED",
              "COMPLETED=COMPLETED",
              ERROR_ROW),
          catalog(
              "PairRole",
              PairRole::values,
              PairRole::valueOf,
              "MAIN=M",
              "INSTRUMENTAL=I",
              "NONE=N"),
          catalog("UserRole", UserRole::values, UserRole::valueOf, "USER=USER", "ADMIN=ADMIN"),
          catalog(
              "UserState",
              UserState::values,
              UserState::valueOf,
              "ACTIVE=ACTIVE",
              "DISABLED=DISABLED",
              "LOCKED=LOCKED"),
          catalog(
              "VideoCategory",
              VideoCategory::values,
              VideoCategory::valueOf,
              "MAIN=MAIN",
              "SUBTRACK=SUBTRACK",
              "OVA=OVA",
              "OPENING=OPENING"),
          catalog(
              "VoiceCondition",
              VoiceCondition::values,
              VoiceCondition::valueOf,
              "PRESENT=1",
              "ABSENT=0"));

  @Test
  void wireValue001ClosedNamesOrderOrdinalWireAndActualGeneratedFactoryMatchIndependentTables() {
    assertEquals(18, CATALOGS.size());
    int rows = 0;
    for (Catalog<?> catalog : CATALOGS) {
      var values = catalog.arrayFactory().get();
      assertEquals(catalog.rows().size(), values.length, catalog.label());
      for (int i = 0; i < values.length; i++) {
        String[] expected = catalog.rows().get(i).split("=", -1);
        assertEquals(2, expected.length);
        var value = values[i];
        assertEquals(catalog.label(), value.getDeclaringClass().getSimpleName());
        assertEquals(expected[0], value.name(), catalog.label());
        assertEquals(i, value.ordinal(), catalog.label());
        assertEquals(expected[1], value.wireValue(), catalog.label());
        assertEquals(expected[0], value.toString(), catalog.label());
        assertSame(value, catalog.nameLookup().apply(expected[0]), catalog.label());
        rows++;
      }
    }
    assertEquals(58, rows);
  }

  @Test
  void wireValue002GeneratedNameLookupRejectsUnknownEmptyCaseSpaceNullAndWireAliases() {
    for (Catalog<?> catalog : CATALOGS) {
      List<String> names = catalog.rows().stream().map(row -> row.split("=", -1)[0]).toList();
      String firstName = names.getFirst();
      for (String bad :
          List.of(
              "",
              "NOT_A_CONSTANT",
              " " + firstName,
              firstName + " ",
              firstName.toLowerCase(Locale.ROOT),
              "ＵＮＫＮＯＷＮ")) {
        assertThrows(
            IllegalArgumentException.class, () -> catalog.nameLookup().apply(bad), catalog.label());
      }
      assertThrows(
          NullPointerException.class, () -> catalog.nameLookup().apply(null), catalog.label());
      for (String row : catalog.rows()) {
        String wire = row.split("=", -1)[1];
        if (!names.contains(wire)) {
          assertThrows(
              IllegalArgumentException.class,
              () -> catalog.nameLookup().apply(wire),
              catalog.label());
        }
      }
    }
  }

  @Test
  void wireValue003ReturnedValueArraysAreIndependentCallerOwnedCopies() {
    for (Catalog<?> catalog : CATALOGS) {
      var first = catalog.arrayFactory().get();
      var second = catalog.arrayFactory().get();
      var originalFirst = second[0];
      assertNotSame(first, second, catalog.label());
      first[0] = null;
      assertSame(originalFirst, second[0], catalog.label());
      assertSame(originalFirst, catalog.arrayFactory().get()[0], catalog.label());
      String[] expectedNames =
          catalog.rows().stream().map(row -> row.split("=", -1)[0]).toArray(String[]::new);
      assertArrayEquals(
          expectedNames,
          Arrays.stream(second).map(Enum::name).toArray(String[]::new),
          catalog.label());
      assertArrayEquals(
          expectedNames,
          Arrays.stream(catalog.arrayFactory().get()).map(Enum::name).toArray(String[]::new),
          catalog.label());
    }
  }

  @Test
  void wireValue004RealHashCollectionKeepsAllFiftyEightTypedSingletonKeys() {
    Map<WireEnum, String> values = new HashMap<>();
    for (Catalog<?> catalog : CATALOGS) {
      for (String row : catalog.rows()) {
        String name = row.split("=", -1)[0];
        values.put(catalog.nameLookup().apply(name), catalog.label() + "/" + name);
      }
    }
    assertEquals(58, values.size());
    for (Catalog<?> catalog : CATALOGS) {
      for (String row : catalog.rows()) {
        String name = row.split("=", -1)[0];
        assertEquals(catalog.label() + "/" + name, values.get(catalog.nameLookup().apply(name)));
      }
    }
  }

  private static <E extends Enum<E> & WireEnum> Catalog<E> catalog(
      String label, Supplier<E[]> arrays, Function<String, E> lookup, String... rows) {
    return new Catalog<>(label, arrays, lookup, List.of(rows));
  }

  private record Catalog<E extends Enum<E> & WireEnum>(
      String label,
      Supplier<E[]> arrayFactory,
      Function<String, E> nameLookup,
      List<String> rows) {}
}
