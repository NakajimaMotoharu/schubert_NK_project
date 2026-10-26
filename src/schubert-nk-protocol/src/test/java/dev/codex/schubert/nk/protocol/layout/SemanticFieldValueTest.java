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
  private static final String SAFE_TEXT = "safe";
  private static final String RELATIVE_PATH_TEXT = "scenario/game/file.txt";
  private static final String DISPLAY_PATH_TEXT = "表示/台本";
  private static final String UNSET_FIELD_NAME = "unset";
  private static final String VALUE_FIELD_NAME = "value";
  private static final String INVALID_SEMANTIC_TEXT = "invalid";
  private static final String ABSOLUTE_PATH_TEXT = "/absolute";
  private static final String NFC_RELATIVE_PATH_TEXT = "scenario/é/file.txt";
  private static final String NFC_DISPLAY_PATH_TEXT = "表示/é";
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
                Map.entry("string", new FieldValue.Text(SAFE_TEXT)),
                Map.entry("number", new FieldValue.Numeric(42)),
                Map.entry("flag", new FieldValue.Flag(true)),
                Map.entry("instantNumeric", new FieldValue.Numeric(20260902123456789L)),
                Map.entry("instantText", new FieldValue.Text(WIRE_TIME)),
                Map.entry("uuid", new FieldValue.Text(UUID_TEXT)),
                Map.entry("authentication", new FieldValue.Text(HEX_A)),
                Map.entry("sha", new FieldValue.Text(HEX_A)),
                Map.entry("relative", new FieldValue.Text(RELATIVE_PATH_TEXT)),
                Map.entry("display", new FieldValue.Text(DISPLAY_PATH_TEXT)),
                Map.entry(UNSET_FIELD_NAME, FieldValue.Unset.INSTANCE)));

    assertEquals(SAFE_TEXT, TypedFieldValues.requiredString(fields, "string"));
    assertEquals(42, TypedFieldValues.requiredLong(fields, "number"));
    assertTrue(TypedFieldValues.requiredBoolean(fields, "flag"));
    assertEquals(Optional.of(SAFE_TEXT), TypedFieldValues.optionalString(fields, "string"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalString(fields, UNSET_FIELD_NAME));
    assertEquals(INSTANT, TypedFieldValues.requiredInstant(fields, "instantNumeric"));
    assertEquals(Optional.of(INSTANT), TypedFieldValues.optionalInstant(fields, "instantText"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalInstant(fields, UNSET_FIELD_NAME));
    assertEquals(UUID_VALUE, TypedFieldValues.requiredUuid(fields, "uuid"));
    assertEquals(Optional.of(UUID_VALUE), TypedFieldValues.optionalUuid(fields, "uuid"));
    assertEquals(Optional.empty(), TypedFieldValues.optionalUuid(fields, UNSET_FIELD_NAME));

    AuthenticationContext authentication = AuthenticationContext.of(HEX_A);
    assertEquals(
        Optional.of(HEX_A),
        TypedFieldValues.optionalAuthenticationContext(fields, "authentication")
            .map(AuthenticationContext::wireValue));
    assertEquals(
        Optional.empty(), TypedFieldValues.optionalAuthenticationContext(fields, UNSET_FIELD_NAME));

    Sha256Hex sha256 = Sha256Hex.of(HEX_A);
    RelativePath relativePath = RelativePath.of(RELATIVE_PATH_TEXT);
    DisplayPath displayPath = DisplayPath.of(DISPLAY_PATH_TEXT);
    assertEquals(HEX_A, TypedFieldValues.requiredSha256(fields, "sha").wireValue());
    assertEquals(
        Optional.of(HEX_A),
        TypedFieldValues.optionalSha256(fields, "sha").map(Sha256Hex::wireValue));
    assertEquals(Optional.empty(), TypedFieldValues.optionalSha256(fields, UNSET_FIELD_NAME));
    assertEquals(
        RELATIVE_PATH_TEXT, TypedFieldValues.requiredRelativePath(fields, "relative").wireValue());
    assertEquals(
        Optional.of(RELATIVE_PATH_TEXT),
        TypedFieldValues.optionalRelativePath(fields, "relative").map(RelativePath::wireValue));
    assertEquals(Optional.empty(), TypedFieldValues.optionalRelativePath(fields, UNSET_FIELD_NAME));
    assertEquals(
        DISPLAY_PATH_TEXT, TypedFieldValues.requiredDisplayPath(fields, "display").wireValue());
    assertEquals(
        Optional.of(DISPLAY_PATH_TEXT),
        TypedFieldValues.optionalDisplayPath(fields, "display").map(DisplayPath::wireValue));
    assertEquals(Optional.empty(), TypedFieldValues.optionalDisplayPath(fields, UNSET_FIELD_NAME));

    assertEquals(new FieldValue.Text(SAFE_TEXT), TypedFieldValues.text(SAFE_TEXT));
    assertEquals(new FieldValue.Numeric(42), TypedFieldValues.numeric(42));
    assertEquals(new FieldValue.Flag(true), TypedFieldValues.flag(true));
    assertEquals(
        new FieldValue.Text(SAFE_TEXT),
        TypedFieldValues.optionalStringValue(Optional.of(SAFE_TEXT)));
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
        new FieldValue.Text(RELATIVE_PATH_TEXT), TypedFieldValues.relativePath(relativePath));
    assertEquals(
        new FieldValue.Text(RELATIVE_PATH_TEXT),
        TypedFieldValues.optionalRelativePathValue(Optional.of(relativePath)));
    assertEquals(
        FieldValue.Unset.INSTANCE, TypedFieldValues.optionalRelativePathValue(Optional.empty()));
    assertEquals(new FieldValue.Text(DISPLAY_PATH_TEXT), TypedFieldValues.displayPath(displayPath));
    assertEquals(
        new FieldValue.Text(DISPLAY_PATH_TEXT),
        TypedFieldValues.optionalDisplayPathValue(Optional.of(displayPath)));
    assertEquals(
        FieldValue.Unset.INSTANCE, TypedFieldValues.optionalDisplayPathValue(Optional.empty()));
  }

  @Test
  void semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects() {
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredInstant(
                fields(new FieldValue.Numeric(20260230000000000L)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalInstant(
                fields(new FieldValue.Text(INVALID_SEMANTIC_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredUuid(
                fields(new FieldValue.Text(UUID_UPPERCASE_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalUuid(
                fields(new FieldValue.Text(INVALID_SEMANTIC_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalAuthenticationContext(
                fields(new FieldValue.Text(INVALID_SEMANTIC_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredSha256(
                fields(new FieldValue.Text(INVALID_SEMANTIC_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalSha256(
                fields(new FieldValue.Text(INVALID_SEMANTIC_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredRelativePath(
                fields(new FieldValue.Text(ABSOLUTE_PATH_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalRelativePath(
                fields(new FieldValue.Text(ABSOLUTE_PATH_TEXT)), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.requiredDisplayPath(
                fields(new FieldValue.Text("")), VALUE_FIELD_NAME));
    assertSemanticFailure(
        () ->
            TypedFieldValues.optionalDisplayPath(
                fields(new FieldValue.Text("")), VALUE_FIELD_NAME));
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
    assertEquals(NFC_RELATIVE_PATH_TEXT, normalized.wireValue());
    assertEquals(RelativePath.of(NFC_RELATIVE_PATH_TEXT), normalized);
    assertNotEquals(RelativePath.of("scenario/other/file.txt"), normalized);
    assertNotEquals(NFC_RELATIVE_PATH_TEXT, normalized);
    assertNotEquals(null, normalized);
    assertFalse(normalized.equals(NFC_RELATIVE_PATH_TEXT));
    assertEquals(RelativePath.of(NFC_RELATIVE_PATH_TEXT).hashCode(), normalized.hashCode());
    assertEquals("RelativePath[REDACTED]", normalized.toString());
    assertThrows(NullPointerException.class, () -> RelativePath.of(null));
    assertInvalidRelativePath("");
    assertInvalidRelativePath(ABSOLUTE_PATH_TEXT);
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
    assertEquals(NFC_DISPLAY_PATH_TEXT, display.wireValue());
    assertEquals(DisplayPath.of(NFC_DISPLAY_PATH_TEXT), display);
    assertNotEquals(DisplayPath.of("表示/別"), display);
    assertNotEquals(NFC_DISPLAY_PATH_TEXT, display);
    assertNotEquals(null, display);
    assertFalse(display.equals(NFC_DISPLAY_PATH_TEXT));
    assertEquals(DisplayPath.of(NFC_DISPLAY_PATH_TEXT).hashCode(), display.hashCode());
    assertEquals("DisplayPath[REDACTED]", display.toString());
    assertThrows(NullPointerException.class, () -> DisplayPath.of(null));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of(""));
    assertThrows(IllegalArgumentException.class, () -> DisplayPath.of(ABSOLUTE_PATH_TEXT));
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
    return new FieldValueSet(Map.of(VALUE_FIELD_NAME, value));
  }

  private static void assertSemanticFailure(ThrowingOperation operation) {
    LayoutValidationException exception =
        assertThrows(LayoutValidationException.class, operation::execute);
    assertTrue(exception.getMessage().contains("invalid semantic value: value"));
    assertTrue(exception.getCause() instanceof IllegalArgumentException);
    assertFalse(exception.getMessage().contains(UUID_TEXT));
    assertFalse(exception.getMessage().contains(UUID_UPPERCASE_TEXT));
  }

  private static void assertInvalidRelativePath(String value) {
    assertThrows(IllegalArgumentException.class, () -> RelativePath.of(value));
  }

  @FunctionalInterface
  private interface ThrowingOperation {
    void execute();
  }
}
