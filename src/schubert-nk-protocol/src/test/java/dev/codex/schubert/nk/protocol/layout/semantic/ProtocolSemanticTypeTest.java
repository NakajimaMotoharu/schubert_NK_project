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
        new FieldValue.Text("42"),
        TypedFieldValues.optionalIdValue(Optional.of(new UserId(42))));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalIdValue(Optional.empty()));

    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredInt(values(new FieldValue.Numeric(Long.MAX_VALUE)), "value"));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.requiredId(values(new FieldValue.Numeric(0)), "value", UserId::new));
    assertThrows(
        LayoutValidationException.class,
        () -> TypedFieldValues.optionalId(values(new FieldValue.Text("ABC")), "value", UserId::new));
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
        NullPointerException.class,
        () -> TypedFieldValues.requiredId(identifier, "value", null));
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
        Optional.of(UserRole.USER),
        TypedFieldValues.optionalEnum(user, "value", UserRole.class));
    assertEquals(
        Optional.of(NotificationErrorCode.PROTOCOL_ERROR),
        TypedFieldValues.optionalEnum(
            values(new FieldValue.Text("PROTOCOL_ERROR")),
            "value",
            NotificationErrorCode.class));
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
        NullPointerException.class,
        () -> TypedFieldValues.requiredEnum(batch, "value", null));
    assertThrows(
        NullPointerException.class,
        () -> TypedFieldValues.optionalEnum(user, "value", null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.enumValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalEnumValue(null));
  }

  private static FieldValueSet values(FieldValue value) {
    return new FieldValueSet(Map.of("value", value));
  }

  private static void add(List<WireEnum> target, WireEnum[] values) {
    target.addAll(List.of(values));
  }
}
