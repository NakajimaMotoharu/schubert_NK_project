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

    assertEquals(123, TypedFieldValues.requiredInt(integer, "value"));
    assertEquals(new UserId(42), TypedFieldValues.requiredId(identifier, "value", UserId::new));
    assertEquals(
        Optional.of(new UserId(42)),
        TypedFieldValues.optionalId(optionalIdentifier, "value", UserId::new));
    assertEquals(Optional.empty(), TypedFieldValues.optionalId(unset, "value", UserId::new));
    assertEquals(new FieldValue.Numeric(42), TypedFieldValues.id(new UserId(42)));
    assertEquals(
        new FieldValue.Text("42"), TypedFieldValues.optionalIdValue(Optional.of(new UserId(42))));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalIdValue(Optional.empty()));

    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.requiredInt(values(new FieldValue.Numeric(Long.MAX_VALUE)), "value"));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredId(values(new FieldValue.Numeric(0)), "value", UserId::new));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalId(values(new FieldValue.Text("ABC")), "value", UserId::new));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalId(
                values(new FieldValue.Text("000000000000")), "value", UserId::new));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalId(
                values(new FieldValue.Text("1234567890123")), "value", UserId::new));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.requiredId(identifier, "value", null));
    assertThrows(
        NullPointerException.class,
        () -> TypedFieldValues.optionalId(optionalIdentifier, "value", null));
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
    assertEquals(LogType.BATCH, TypedFieldValues.requiredEnum(batch, "value", LogType.class));
    assertEquals(
        Optional.of(UserRole.USER), TypedFieldValues.optionalEnum(user, "value", UserRole.class));
    assertEquals(
        Optional.of(NotificationErrorCode.PROTOCOL_ERROR),
        TypedFieldValues.optionalEnum(
            values(new FieldValue.Text("PROTOCOL_ERROR")), "value", NotificationErrorCode.class));
    assertEquals(Optional.empty(), TypedFieldValues.optionalEnum(unset, "value", UserRole.class));
    assertEquals(
        new FieldValue.Text("ADMIN"),
        TypedFieldValues.optionalEnumValue(Optional.of(UserRole.ADMIN)));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalEnumValue(Optional.empty()));

    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.requiredEnum(
                values(new FieldValue.Text("UNKNOWN")), "value", LogType.class));
    assertThrows(
        LayoutValidationException.class,
        () ->
            TypedFieldValues.optionalEnum(
                values(new FieldValue.Text("UNKNOWN")), "value", UserRole.class));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.requiredEnum(batch, "value", null));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.optionalEnum(user, "value", null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.enumValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalEnumValue(null));
  }

  @Test
  void xNumericWrappersAndGeneratedNumericRangesRejectNonCanonicalValues() {
    FieldValueSet status = values(new FieldValue.Text("200"));
    FieldValueSet elapsed = values(new FieldValue.Text("999999999"));
    FieldValueSet unset = values(FieldValue.Unset.INSTANCE);

    assertEquals(new HttpStatusCode(200), TypedFieldValues.requiredHttpStatusCode(status, "value"));
    assertEquals(
        Optional.of(new HttpStatusCode(200)),
        TypedFieldValues.optionalHttpStatusCode(status, "value"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalHttpStatusCode(unset, "value"));
    assertEquals(
        new ElapsedMilliseconds(999_999_999),
        TypedFieldValues.requiredElapsedMilliseconds(elapsed, "value"));
    assertEquals(
        Optional.of(new ElapsedMilliseconds(999_999_999)),
        TypedFieldValues.optionalElapsedMilliseconds(elapsed, "value"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalElapsedMilliseconds(unset, "value"));
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

    TypedFieldValues.requireUnsignedRange("value", 0, 1);
    TypedFieldValues.requireUnsignedRange("value", 999_999_999_999L, 12);
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requireUnsignedRange("value", -1, 1));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requireUnsignedRange("value", 1_000, 3));
    assertThrows(
        IllegalArgumentException.class, () -> TypedFieldValues.requireUnsignedRange("value", 0, 0));
    assertThrows(
        IllegalArgumentException.class,
        () -> TypedFieldValues.requireUnsignedRange("value", 0, 19));
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
    return new FieldValueSet(Map.of("value", value));
  }

  private static void add(List<WireEnum> target, WireEnum[] values) {
    target.addAll(List.of(values));
  }
}
