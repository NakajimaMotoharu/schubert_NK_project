package dev.codex.schubert.nk.protocol.layout.semantic;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.layout.FieldValue;
import dev.codex.schubert.nk.protocol.layout.FieldValueSet;
import dev.codex.schubert.nk.protocol.layout.LayoutValidationException;
import dev.codex.schubert.nk.protocol.layout.TypedFieldValues;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.LongFunction;
import org.junit.jupiter.api.Test;

class ProtocolSemanticTypeTest {
  private static final String ERROR_ENUM_TEXT = "ERROR=ERROR";
  private static final String VALUE_FIELD_NAME = "value";

  /** YKT1010/PT-PRO-001-T04: independent UI234..236/SS333/351 enum tables. */
  @Test
  void approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTables() {
    // UI234: SRC voice/type, SCN delivery; UI235: disposition/category/pair;
    // UI236: user/log/question/notification; SS333 section8: MIME;
    // SS351 public notification failure-code projection table (PROCESS_FAILED..PROTOCOL_ERROR).
    assertApprovedEnum(ContentDisposition.class, "INLINE=I", "ATTACHMENT=A");
    assertApprovedEnum(DeliveryMode.class, "INLINE=I", "FILE=F");
    assertApprovedEnum(PairRole.class, "MAIN=M", "INSTRUMENTAL=I", "NONE=N");
    assertApprovedEnum(VoiceCondition.class, "PRESENT=1", "ABSENT=0");
    assertApprovedEnum(UserRole.class, "USER=USER", "ADMIN=ADMIN");
    assertApprovedEnum(LogLevel.class, "INFO=INFO", "WARN=WARN", ERROR_ENUM_TEXT);
    assertApprovedEnum(
        LogType.class,
        "ACTION=ACTION",
        "REQUEST=REQUEST",
        "SECURITY=SECURITY",
        "MQ=MQ",
        "SYSTEM=SYSTEM",
        "BATCH=BATCH");
    assertApprovedEnum(UserState.class, "ACTIVE=ACTIVE", "DISABLED=DISABLED", "LOCKED=LOCKED");
    assertApprovedEnum(
        NotificationState.class,
        "RECEIVED=RECEIVED",
        "PROCESSING=PROCESSING",
        "COMPLETED=COMPLETED",
        ERROR_ENUM_TEXT,
        "CANCELLED=CANCELLED");
    assertApprovedEnum(
        AnswerState.class, "ANSWERED=ANSWERED", "UNANSWERED=UNANSWERED", ERROR_ENUM_TEXT);
    assertApprovedEnum(
        NotificationType.class, "ACCEPTED=ACCEPTED", "COMPLETED=COMPLETED", ERROR_ENUM_TEXT);
    assertApprovedEnum(EntryType.class, "DIALOGUE=dialogue", "NARRATION=narration");
    assertApprovedEnum(GameCode.class, "NUKITASHI_1=NUKITASHI1", "NUKITASHI_2=NUKITASHI2");
    assertApprovedEnum(
        MediaMimeType.class,
        "AUDIO_MP4=audio/mp4",
        "AUDIO_MPEG=audio/mpeg",
        "AUDIO_OGG=audio/ogg",
        "AUDIO_WAV=audio/wav",
        "AUDIO_FLAC=audio/flac",
        "VIDEO_MP4=video/mp4");
    assertApprovedEnum(
        NotificationErrorCode.class,
        "PROCESS_FAILED=PROCESS_FAILED",
        "SYSTEM_UNAVAILABLE=SYSTEM_UNAVAIL",
        "RESOURCE_LIMIT=RESOURCE_LIMIT",
        "DATA_INTEGRITY=DATA_INTEGRITY",
        "PROTOCOL_ERROR=PROTOCOL_ERROR");
    assertApprovedEnum(AnimationListCategory.class, "MAIN=MAIN", "OVA=OVA");
    assertApprovedEnum(AnimationCategory.class, "MAIN=MAIN", "SUBTRACK=SUBTRACK", "OVA=OVA");
    assertApprovedEnum(
        VideoCategory.class, "MAIN=MAIN", "SUBTRACK=SUBTRACK", "OVA=OVA", "OPENING=OPENING");
  }

  private static <E extends Enum<E> & WireEnum> void assertApprovedEnum(
      Class<E> type, String... rows) {
    assertEquals(rows.length, type.getEnumConstants().length, type.getSimpleName());
    for (String row : rows) {
      String[] expected = row.split("=", -1);
      assertEquals(2, expected.length);
      E actual = Enum.valueOf(type, expected[0]);
      assertEquals(expected[1], actual.wireValue(), type.getSimpleName() + ":" + expected[0]);
      assertEquals(new FieldValue.Text(expected[1]), TypedFieldValues.enumValue(actual));
      assertEquals(
          expected[0],
          TypedFieldValues.requiredEnum(
                  values(new FieldValue.Text(expected[1])), VALUE_FIELD_NAME, type)
              .name());
      assertEquals(
          expected[0],
          TypedFieldValues.optionalEnum(
                  values(new FieldValue.Text(expected[1])), VALUE_FIELD_NAME, type)
              .orElseThrow()
              .name());
    }
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.requiredEnum(
                values(new FieldValue.Text("UNAPPROVED_CANARY")), VALUE_FIELD_NAME, type));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalEnum(
                values(new FieldValue.Text("UNAPPROVED_CANARY")), VALUE_FIELD_NAME, type));
  }

  @Test
  void allN12IdentifierTypesEnforceTheSharedPositiveRange() {
    List<LongFunction<? extends ProtocolId>> factories =
        List.of(
            AsyncJobId::new,
            AudioId::new,
            EntryId::new,
            LogId::new,
            NotificationId::new,
            QuestionId::new,
            ScriptFileId::new,
            SpeakerId::new,
            UserId::new);

    for (LongFunction<? extends ProtocolId> factory : factories) {
      assertEquals(1, factory.apply(1).value());
      assertEquals(999_999_999_999L, factory.apply(999_999_999_999L).value());
      assertThrows(IllegalArgumentException.class, () -> factory.apply(0));
      assertThrows(IllegalArgumentException.class, () -> factory.apply(1_000_000_000_000L));
    }
  }

  @Test
  void typedHelpersConvertIntAndIdentifiersWithoutLosingWireKinds() {
    FieldValueSet integer = values(new FieldValue.Numeric(123));
    FieldValueSet identifier = values(new FieldValue.Numeric(42));
    FieldValueSet optionalIdentifier = values(new FieldValue.Text("000000000042"));
    FieldValueSet unset = values(FieldValue.Unset.INSTANCE);

    assertEquals(123, TypedFieldValues.requiredInt(integer, VALUE_FIELD_NAME));
    assertEquals(
        new UserId(42), TypedFieldValues.requiredId(identifier, VALUE_FIELD_NAME, UserId::new));
    assertEquals(
        Optional.of(new UserId(42)),
        TypedFieldValues.optionalId(optionalIdentifier, VALUE_FIELD_NAME, UserId::new));
    assertEquals(
        Optional.empty(), TypedFieldValues.optionalId(unset, VALUE_FIELD_NAME, UserId::new));
    assertEquals(new FieldValue.Numeric(42), TypedFieldValues.id(new UserId(42)));
    assertEquals(
        new FieldValue.Text("42"), TypedFieldValues.optionalIdValue(Optional.of(new UserId(42))));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalIdValue(Optional.empty()));

    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.requiredInt(
                values(new FieldValue.Numeric(Long.MAX_VALUE)), VALUE_FIELD_NAME));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.requiredId(
                values(new FieldValue.Numeric(0)), VALUE_FIELD_NAME, UserId::new));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalId(
                values(new FieldValue.Text("ABC")), VALUE_FIELD_NAME, UserId::new));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalId(
                values(new FieldValue.Text("000000000000")), VALUE_FIELD_NAME, UserId::new));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalId(
                values(new FieldValue.Text("1234567890123")), VALUE_FIELD_NAME, UserId::new));
    assertThrows(
        NullPointerException.class,
        () -> TypedFieldValues.requiredId(identifier, VALUE_FIELD_NAME, null));
    assertThrows(
        NullPointerException.class,
        () -> TypedFieldValues.optionalId(optionalIdentifier, VALUE_FIELD_NAME, null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.id(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalIdValue(null));
  }

  @Test
  void allAllowlistedEnumsExposeExplicitWireValuesAndGenericConversion() {
    List<WireEnum> values = new ArrayList<>();
    add(values, ContentDisposition.values());
    add(values, DeliveryMode.values());
    add(values, PairRole.values());
    add(values, VoiceCondition.values());
    add(values, UserRole.values());
    add(values, LogLevel.values());
    add(values, LogType.values());
    add(values, UserState.values());
    add(values, NotificationState.values());
    add(values, AnswerState.values());
    add(values, NotificationType.values());
    add(values, EntryType.values());
    add(values, GameCode.values());
    add(values, MediaMimeType.values());
    add(values, NotificationErrorCode.values());
    add(values, AnimationListCategory.values());
    add(values, AnimationCategory.values());
    add(values, VideoCategory.values());

    for (WireEnum value : values) {
      assertFalse(value.wireValue().isBlank());
      assertEquals(new FieldValue.Text(value.wireValue()), TypedFieldValues.enumValue(value));
    }

    FieldValueSet batch = values(new FieldValue.Text("BATCH"));
    FieldValueSet user = values(new FieldValue.Text("USER"));
    FieldValueSet unset = values(FieldValue.Unset.INSTANCE);
    assertEquals(
        LogType.BATCH, TypedFieldValues.requiredEnum(batch, VALUE_FIELD_NAME, LogType.class));
    assertEquals(
        Optional.of(UserRole.USER),
        TypedFieldValues.optionalEnum(user, VALUE_FIELD_NAME, UserRole.class));
    assertEquals(
        Optional.of(NotificationErrorCode.PROTOCOL_ERROR),
        TypedFieldValues.optionalEnum(
            values(new FieldValue.Text("PROTOCOL_ERROR")),
            VALUE_FIELD_NAME,
            NotificationErrorCode.class));
    assertEquals(
        Optional.empty(), TypedFieldValues.optionalEnum(unset, VALUE_FIELD_NAME, UserRole.class));
    assertEquals(
        new FieldValue.Text("ADMIN"),
        TypedFieldValues.optionalEnumValue(Optional.of(UserRole.ADMIN)));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalEnumValue(Optional.empty()));

    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.requiredEnum(
                values(new FieldValue.Text("UNKNOWN")), VALUE_FIELD_NAME, LogType.class));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalEnum(
                values(new FieldValue.Text("UNKNOWN")), VALUE_FIELD_NAME, UserRole.class));
    assertThrows(
        NullPointerException.class,
        () -> TypedFieldValues.requiredEnum(batch, VALUE_FIELD_NAME, null));
    assertThrows(
        NullPointerException.class,
        () -> TypedFieldValues.optionalEnum(user, VALUE_FIELD_NAME, null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.enumValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalEnumValue(null));
  }

  @Test
  void xNumericWrappersAndGeneratedNumericRangesRejectNonCanonicalValues() {
    FieldValueSet status = values(new FieldValue.Text("200"));
    FieldValueSet elapsed = values(new FieldValue.Text("999999999"));
    FieldValueSet unset = values(FieldValue.Unset.INSTANCE);

    assertEquals(
        new HttpStatusCode(200), TypedFieldValues.requiredHttpStatusCode(status, VALUE_FIELD_NAME));
    assertEquals(
        Optional.of(new HttpStatusCode(200)),
        TypedFieldValues.optionalHttpStatusCode(status, VALUE_FIELD_NAME));
    assertEquals(
        Optional.empty(), TypedFieldValues.optionalHttpStatusCode(unset, VALUE_FIELD_NAME));
    assertEquals(
        new ElapsedMilliseconds(999_999_999),
        TypedFieldValues.requiredElapsedMilliseconds(elapsed, VALUE_FIELD_NAME));
    assertEquals(
        Optional.of(new ElapsedMilliseconds(999_999_999)),
        TypedFieldValues.optionalElapsedMilliseconds(elapsed, VALUE_FIELD_NAME));
    assertEquals(
        Optional.empty(), TypedFieldValues.optionalElapsedMilliseconds(unset, VALUE_FIELD_NAME));
    assertEquals(
        new FieldValue.Text("200"), TypedFieldValues.httpStatusCode(new HttpStatusCode(200)));
    assertEquals(
        new FieldValue.Text("200"),
        TypedFieldValues.optionalHttpStatusCodeValue(Optional.of(new HttpStatusCode(200))));
    assertEquals(
        FieldValue.Unset.INSTANCE, TypedFieldValues.optionalHttpStatusCodeValue(Optional.empty()));
    assertEquals(
        new FieldValue.Text("0"), TypedFieldValues.elapsedMilliseconds(new ElapsedMilliseconds(0)));
    assertEquals(
        new FieldValue.Text("0"),
        TypedFieldValues.optionalElapsedMillisecondsValue(Optional.of(new ElapsedMilliseconds(0))));
    assertEquals(
        FieldValue.Unset.INSTANCE,
        TypedFieldValues.optionalElapsedMillisecondsValue(Optional.empty()));

    TypedFieldValues.requireUnsignedRange(VALUE_FIELD_NAME, 0, 1);
    TypedFieldValues.requireUnsignedRange(VALUE_FIELD_NAME, 999_999_999_999L, 12);
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requireUnsignedRange(VALUE_FIELD_NAME, -1, 1));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requireUnsignedRange(VALUE_FIELD_NAME, 1_000, 3));
    assertThrows(
        IllegalArgumentException.class,
        () -> TypedFieldValues.requireUnsignedRange(VALUE_FIELD_NAME, 0, 0));
    assertThrows(
        IllegalArgumentException.class,
        () -> TypedFieldValues.requireUnsignedRange(VALUE_FIELD_NAME, 0, 19));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.requireUnsignedRange(null, 0, 1));

    assertThrows(IllegalArgumentException.class, () -> new HttpStatusCode(99));
    assertThrows(IllegalArgumentException.class, () -> new HttpStatusCode(600));
    assertThrows(IllegalArgumentException.class, () -> HttpStatusCode.parse("20A"));
    assertThrows(NullPointerException.class, () -> HttpStatusCode.parse(null));
    assertThrows(IllegalArgumentException.class, () -> new ElapsedMilliseconds(-1));
    assertThrows(IllegalArgumentException.class, () -> new ElapsedMilliseconds(1_000_000_000));
    assertThrows(IllegalArgumentException.class, () -> ElapsedMilliseconds.parse("0000000000"));
    assertThrows(NullPointerException.class, () -> ElapsedMilliseconds.parse(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.httpStatusCode(null));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.optionalHttpStatusCodeValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.elapsedMilliseconds(null));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.optionalElapsedMillisecondsValue(null));
  }

  private static FieldValueSet values(FieldValue value) {
    return new FieldValueSet(Map.of(VALUE_FIELD_NAME, value));
  }

  private static void add(List<WireEnum> target, WireEnum[] values) {
    target.addAll(List.of(values));
  }
}
