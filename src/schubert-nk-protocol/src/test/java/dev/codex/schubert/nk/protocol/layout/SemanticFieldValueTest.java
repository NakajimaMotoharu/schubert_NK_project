package dev.codex.schubert.nk.protocol.layout;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

class SemanticFieldValueTest {
  private static final String HEX_A = "a".repeat(64);
  private static final String HEX_B = "b".repeat(64);
  private static final String UUID_TEXT = "123e4567-e89b-12d3-a456-426614174000";
  private static final String UUID_UPPERCASE_TEXT = "123E4567-E89B-12D3-A456-426614174000";
  private static final UUID UUID_VALUE = UUID.fromString(UUID_TEXT);
  private static final String WIRE_TIME = "20260902123456789";
  private static final Instant INSTANT = Instant.parse("2026-09-02T03:34:56.789Z");

  @Test
  void semanticHelpersDecodeAndEncodeEverySupportedShape() {
    FieldValueSet fields =
        new FieldValueSet(
            Map.ofEntries(
                Map.entry("string", new FieldValue.Text("safe")),
                Map.entry("number", new FieldValue.Numeric(42)),
                Map.entry("flag", new FieldValue.Flag(true)),
                Map.entry("instantNumeric", new FieldValue.Numeric(20260902123456789L)),
                Map.entry("instantText", new FieldValue.Text(WIRE_TIME)),
                Map.entry("uuid", new FieldValue.Text(UUID_TEXT)),
                Map.entry("authentication", new FieldValue.Text(HEX_A)),
                Map.entry("sha", new FieldValue.Text(HEX_A)),
                Map.entry("relative", new FieldValue.Text("scenario/game/file.txt")),
                Map.entry("display", new FieldValue.Text("表示/台本")),
                Map.entry("unset", FieldValue.Unset.INSTANCE)));

    assertEquals("safe", TypedFieldValues.requiredString(fields, "string"));
    assertEquals(42, TypedFieldValues.requiredLong(fields, "number"));
    assertTrue(TypedFieldValues.requiredBoolean(fields, "flag"));
    assertEquals(Optional.of("safe"), TypedFieldValues.optionalString(fields, "string"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalString(fields, "unset"));
    assertEquals(INSTANT, TypedFieldValues.requiredInstant(fields, "instantNumeric"));
    assertEquals(Optional.of(INSTANT), TypedFieldValues.optionalInstant(fields, "instantText"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalInstant(fields, "unset"));
    assertEquals(UUID_VALUE, TypedFieldValues.requiredUuid(fields, "uuid"));
    assertEquals(Optional.of(UUID_VALUE), TypedFieldValues.optionalUuid(fields, "uuid"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalUuid(fields, "unset"));

    AuthenticationContext authentication = AuthenticationContext.of(HEX_A);
    assertEquals(
        Optional.of(authentication),
        TypedFieldValues.optionalAuthenticationContext(fields, "authentication"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalAuthenticationContext(fields, "unset"));

    Sha256Hex sha256 = Sha256Hex.of(HEX_A);
    RelativePath relativePath = RelativePath.of("scenario/game/file.txt");
    DisplayPath displayPath = DisplayPath.of("表示/台本");
    assertEquals(sha256, TypedFieldValues.requiredSha256(fields, "sha"));
    assertEquals(Optional.of(sha256), TypedFieldValues.optionalSha256(fields, "sha"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalSha256(fields, "unset"));
    assertEquals(relativePath, TypedFieldValues.requiredRelativePath(fields, "relative"));
    assertEquals(
        Optional.of(relativePath), TypedFieldValues.optionalRelativePath(fields, "relative"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalRelativePath(fields, "unset"));
    assertEquals(displayPath, TypedFieldValues.requiredDisplayPath(fields, "display"));
    assertEquals(Optional.of(displayPath), TypedFieldValues.optionalDisplayPath(fields, "display"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalDisplayPath(fields, "unset"));

    assertEquals(new FieldValue.Text("safe"), TypedFieldValues.text("safe"));
    assertEquals(new FieldValue.Numeric(42), TypedFieldValues.numeric(42));
    assertEquals(new FieldValue.Flag(true), TypedFieldValues.flag(true));
    assertEquals(
        new FieldValue.Text("safe"), TypedFieldValues.optionalStringValue(Optional.of("safe")));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalStringValue(Optional.empty()));
    assertEquals(new FieldValue.Numeric(20260902123456789L), TypedFieldValues.instant(INSTANT));
    assertEquals(
        new FieldValue.Text(WIRE_TIME),
        TypedFieldValues.optionalInstantValue(Optional.of(INSTANT)));
    assertEquals(
        FieldValue.Unset.INSTANCE, TypedFieldValues.optionalInstantValue(Optional.empty()));
    assertEquals(new FieldValue.Text(UUID_TEXT), TypedFieldValues.uuid(UUID_VALUE));
    assertEquals(
        new FieldValue.Text(UUID_TEXT),
        TypedFieldValues.optionalUuidValue(Optional.of(UUID_VALUE)));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalUuidValue(Optional.empty()));
    assertEquals(
        new FieldValue.Text(HEX_A),
        TypedFieldValues.optionalAuthenticationContextValue(Optional.of(authentication)));
    assertEquals(
        FieldValue.Unset.INSTANCE,
        TypedFieldValues.optionalAuthenticationContextValue(Optional.empty()));
    assertEquals(new FieldValue.Text(HEX_A), TypedFieldValues.sha256(sha256));
    assertEquals(
        new FieldValue.Text(HEX_A), TypedFieldValues.optionalSha256Value(Optional.of(sha256)));
    assertEquals(FieldValue.Unset.INSTANCE, TypedFieldValues.optionalSha256Value(Optional.empty()));
    assertEquals(
        new FieldValue.Text("scenario/game/file.txt"), TypedFieldValues.relativePath(relativePath));
    assertEquals(
        new FieldValue.Text("scenario/game/file.txt"),
        TypedFieldValues.optionalRelativePathValue(Optional.of(relativePath)));
    assertEquals(
        FieldValue.Unset.INSTANCE, TypedFieldValues.optionalRelativePathValue(Optional.empty()));
    assertEquals(new FieldValue.Text("表示/台本"), TypedFieldValues.displayPath(displayPath));
    assertEquals(
        new FieldValue.Text("表示/台本"),
        TypedFieldValues.optionalDisplayPathValue(Optional.of(displayPath)));
    assertEquals(
        FieldValue.Unset.INSTANCE, TypedFieldValues.optionalDisplayPathValue(Optional.empty()));
  }

  @Test
  void semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects() {
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredInstant(
                fields(new FieldValue.Numeric(20260230000000000L)), "value"));
    assertSemanticFailure(
        () -> TypedFieldValues.optionalInstant(fields(new FieldValue.Text("invalid")), "value"));
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredUuid(
                fields(new FieldValue.Text(UUID_UPPERCASE_TEXT)), "value"));
    assertSemanticFailure(
        () -> TypedFieldValues.optionalUuid(fields(new FieldValue.Text("invalid")), "value"));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalAuthenticationContext(
                fields(new FieldValue.Text("invalid")), "value"));
    assertSemanticFailure(
        () -> TypedFieldValues.requiredSha256(fields(new FieldValue.Text("invalid")), "value"));
    assertSemanticFailure(
        () -> TypedFieldValues.optionalSha256(fields(new FieldValue.Text("invalid")), "value"));
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredRelativePath(
                fields(new FieldValue.Text("/absolute")), "value"));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalRelativePath(
                fields(new FieldValue.Text("/absolute")), "value"));
    assertSemanticFailure(
        () -> TypedFieldValues.requiredDisplayPath(fields(new FieldValue.Text("")), "value"));
    assertSemanticFailure(
        () -> TypedFieldValues.optionalDisplayPath(fields(new FieldValue.Text("")), "value"));
  }

  @Test
  void semanticValueObjectsNormalizeValidateCompareAndRedact() {
    Sha256Hex sha = Sha256Hex.of(HEX_A);
    assertEquals(HEX_A, sha.wireValue());
    assertEquals(Sha256Hex.of(HEX_A), sha);
    assertNotEquals(Sha256Hex.of(HEX_B), sha);
    assertNotEquals("not-a-sha", sha);
    assertNotEquals(null, sha);
    assertFalse(sha.equals("not-a-sha"));
    assertEquals(Sha256Hex.of(HEX_A).hashCode(), sha.hashCode());
    assertEquals("Sha256Hex[REDACTED]", sha.toString());
    assertThrows(NullPointerException.class, () -> Sha256Hex.of(null));
    assertThrows(IllegalArgumentException.class, () -> Sha256Hex.of("A".repeat(64)));

    RelativePath normalized = RelativePath.of("scenario/e\u0301/file.txt");
    assertEquals("scenario/é/file.txt", normalized.wireValue());
    assertEquals(RelativePath.of("scenario/é/file.txt"), normalized);
    assertNotEquals(RelativePath.of("scenario/other/file.txt"), normalized);
    assertNotEquals("scenario/é/file.txt", normalized);
    assertNotEquals(null, normalized);
    assertFalse(normalized.equals("scenario/é/file.txt"));
    assertEquals(RelativePath.of("scenario/é/file.txt").hashCode(), normalized.hashCode());
    assertEquals("RelativePath[REDACTED]", normalized.toString());
    assertThrows(NullPointerException.class, () -> RelativePath.of(null));
    assertInvalidRelativePath("");
    assertInvalidRelativePath("/absolute");
    assertInvalidRelativePath("C:/absolute");
    assertInvalidRelativePath("C:drive-relative");
    assertInvalidRelativePath("\\\\server\\share");
    assertInvalidRelativePath("trailing/");
    assertInvalidRelativePath("bad\\path");
    assertInvalidRelativePath("a".repeat(513));
    assertInvalidRelativePath("a//b");
    assertInvalidRelativePath("./a");
    assertInvalidRelativePath("../a");
    assertInvalidRelativePath("a".repeat(256));
    assertInvalidRelativePath("a/\n");

    DisplayPath display = DisplayPath.of("表示/e\u0301");
    assertEquals("表示/é", display.wireValue());
    assertEquals(DisplayPath.of("表示/é"), display);
    assertNotEquals(DisplayPath.of("表示/別"), display);
    assertNotEquals("表示/é", display);
    assertNotEquals(null, display);
    assertFalse(display.equals("表示/é"));
    assertEquals(DisplayPath.of("表示/é").hashCode(), display.hashCode());
    assertEquals("DisplayPath[REDACTED]", display.toString());
    assertThrows(NullPointerException.class, () -> DisplayPath.of(null));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of(""));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of("/absolute"));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of("C:\\absolute"));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of("\\\\server\\share"));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of("safe/../outside"));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of("safe\\..\\outside"));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of("a".repeat(513)));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of("表示\npath"));
  }

  @Test
  void semanticEncodingHelpersRejectNullReferences() {
    assertThrows(NullPointerException.class, () -> TypedFieldValues.text(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalStringValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.instant(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalInstantValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.uuid(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalUuidValue(null));
    assertThrows(
        NullPointerException.class,
        () -> TypedFieldValues.optionalAuthenticationContextValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.sha256(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalSha256Value(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.relativePath(null));
    assertThrows(
        NullPointerException.class, () -> TypedFieldValues.optionalRelativePathValue(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.displayPath(null));
    assertThrows(NullPointerException.class, () -> TypedFieldValues.optionalDisplayPathValue(null));
  }

  private static FieldValueSet fields(FieldValue value) {
    return new FieldValueSet(Map.of("value", value));
  }

  private static void assertSemanticFailure(ThrowingOperation operation) {
    LayoutValidationException exception =
        assertThrows(LayoutValidationException.class, operation::execute);
    assertTrue(exception.getMessage().contains("invalid semantic value: value"));
    assertTrue(exception.getCause() instanceof IllegalArgumentException);
    assertFalse(exception.getMessage().contains(UUID_TEXT));
  }

  private static void assertInvalidRelativePath(String value) {
    assertThrows(IllegalArgumentException.class, () -> RelativePath.of(value));
  }

  @FunctionalInterface
  private interface ThrowingOperation {
    void execute();
  }
}
