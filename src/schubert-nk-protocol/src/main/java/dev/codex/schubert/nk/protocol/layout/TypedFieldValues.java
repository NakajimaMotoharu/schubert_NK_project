package dev.codex.schubert.nk.protocol.layout;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.DisplayPath;
import dev.codex.schubert.nk.protocol.layout.semantic.ElapsedMilliseconds;
import dev.codex.schubert.nk.protocol.layout.semantic.HttpStatusCode;
import dev.codex.schubert.nk.protocol.layout.semantic.ProtocolId;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.protocol.layout.semantic.Sha256Hex;
import dev.codex.schubert.nk.protocol.layout.semantic.WireEnum;
import dev.codex.schubert.nk.protocol.time.JstWireTimestamp;
import java.time.Instant;
import java.util.Locale;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.LongFunction;
import java.util.regex.Pattern;

/**
 * Type-safe bridge used by generated named records; it never infers component order. Trace:
 * NK-PRO-001, SS 323 sections 2/10, PT-PRO-001-T02/T03.
 */
public final class TypedFieldValues {
  private static final java.lang.String LITERAL_VALUE = "value";

  private static final TypedFieldValues INSTANCE = new TypedFieldValues();
  private final Pattern retainedOptionalId;

  private TypedFieldValues() {
    retainedOptionalId = Pattern.compile("[0-9]{1,12}");
  }

  public static FieldValue.Text requiredText(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value instanceof FieldValue.Text text) {
      return text;
    }
    throw wrongType(name);
  }

  public static FieldValue.Numeric requiredNumeric(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value instanceof FieldValue.Numeric numeric) {
      return numeric;
    }
    throw wrongType(name);
  }

  public static FieldValue.Flag requiredFlag(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value instanceof FieldValue.Flag flag) {
      return flag;
    }
    throw wrongType(name);
  }

  public static Optional<FieldValue.Text> optionalText(FieldValueSet fields, String name) {
    FieldValue value = require(fields, name);
    if (value == FieldValue.Unset.INSTANCE) {
      return Optional.empty();
    }
    if (value instanceof FieldValue.Text text) {
      return Optional.of(text);
    }
    throw wrongType(name);
  }

  public static String requiredString(FieldValueSet fields, String name) {
    return requiredText(fields, name).value();
  }

  public static long requiredLong(FieldValueSet fields, String name) {
    return requiredNumeric(fields, name).value();
  }

  public static int requiredInt(FieldValueSet fields, String name) {
    try {
      return Math.toIntExact(requiredLong(fields, name));
    } catch (ArithmeticException exception) {
      throw new LayoutValidationException(
          "typed integer field is out of range: " + name, exception);
    }
  }

  public static void requireUnsignedRange(String name, long value, int digits) {
    Objects.requireNonNull(name, "name");
    if (digits < 1 || digits > 18) {
      throw new IllegalArgumentException("numeric digit count must be between 1 and 18");
    }
    long maximum = 0;
    for (int index = 0; index < digits; index++) {
      maximum = maximum * 10 + 9;
    }
    if (value < 0 || value > maximum) {
      throw new LayoutValidationException("typed numeric field is out of range: " + name);
    }
  }

  public static boolean requiredBoolean(FieldValueSet fields, String name) {
    return requiredFlag(fields, name).value();
  }

  public static Optional<String> optionalString(FieldValueSet fields, String name) {
    return optionalText(fields, name).map(FieldValue.Text::value);
  }

  public static <T extends ProtocolId> T requiredId(
      FieldValueSet fields, String name, LongFunction<T> factory) {
    Objects.requireNonNull(factory, "factory");
    return semanticId(name, requiredLong(fields, name), factory);
  }

  public static <T extends ProtocolId> Optional<T> optionalId(
      FieldValueSet fields, String name, LongFunction<T> factory) {
    Objects.requireNonNull(factory, "factory");
    return optionalString(fields, name)
        .map(value -> semantic(name, value, text -> factory.apply(parseOptionalId(text))));
  }

  public static <E extends Enum<E> & WireEnum> E requiredEnum(
      FieldValueSet fields, String name, Class<E> type) {
    Objects.requireNonNull(type, "type");
    return semantic(name, requiredString(fields, name), value -> enumConstant(type, value));
  }

  public static <E extends Enum<E> & WireEnum> Optional<E> optionalEnum(
      FieldValueSet fields, String name, Class<E> type) {
    Objects.requireNonNull(type, "type");
    return optionalString(fields, name)
        .map(value -> semantic(name, value, wire -> enumConstant(type, wire)));
  }

  public static HttpStatusCode requiredHttpStatusCode(FieldValueSet fields, String name) {
    return semantic(name, requiredString(fields, name), HttpStatusCode::parse);
  }

  public static Optional<HttpStatusCode> optionalHttpStatusCode(FieldValueSet fields, String name) {
    return optionalString(fields, name).map(value -> semantic(name, value, HttpStatusCode::parse));
  }

  public static ElapsedMilliseconds requiredElapsedMilliseconds(FieldValueSet fields, String name) {
    return semantic(name, requiredString(fields, name), ElapsedMilliseconds::parse);
  }

  public static Optional<ElapsedMilliseconds> optionalElapsedMilliseconds(
      FieldValueSet fields, String name) {
    return optionalString(fields, name)
        .map(value -> semantic(name, value, ElapsedMilliseconds::parse));
  }

  public static Instant requiredInstant(FieldValueSet fields, String name) {
    String wire = String.format(Locale.ROOT, "%017d", requiredLong(fields, name));
    return semantic(name, wire, JstWireTimestamp::parse);
  }

  public static Optional<Instant> optionalInstant(FieldValueSet fields, String name) {
    return optionalString(fields, name)
        .map(value -> semantic(name, value, JstWireTimestamp::parse));
  }

  public static UUID requiredUuid(FieldValueSet fields, String name) {
    return semantic(name, requiredString(fields, name), TypedFieldValues::canonicalUuid);
  }

  public static Optional<UUID> optionalUuid(FieldValueSet fields, String name) {
    return optionalString(fields, name)
        .map(value -> semantic(name, value, TypedFieldValues::canonicalUuid));
  }

  public static Optional<AuthenticationContext> optionalAuthenticationContext(
      FieldValueSet fields, String name) {
    return optionalString(fields, name)
        .map(value -> semantic(name, value, AuthenticationContext::of));
  }

  public static Sha256Hex requiredSha256(FieldValueSet fields, String name) {
    return semantic(name, requiredString(fields, name), Sha256Hex::of);
  }

  public static Optional<Sha256Hex> optionalSha256(FieldValueSet fields, String name) {
    return optionalString(fields, name).map(value -> semantic(name, value, Sha256Hex::of));
  }

  public static RelativePath requiredRelativePath(FieldValueSet fields, String name) {
    return semantic(name, requiredString(fields, name), RelativePath::of);
  }

  public static Optional<RelativePath> optionalRelativePath(FieldValueSet fields, String name) {
    return optionalString(fields, name).map(value -> semantic(name, value, RelativePath::of));
  }

  public static DisplayPath requiredDisplayPath(FieldValueSet fields, String name) {
    return semantic(name, requiredString(fields, name), DisplayPath::of);
  }

  public static Optional<DisplayPath> optionalDisplayPath(FieldValueSet fields, String name) {
    return optionalString(fields, name).map(value -> semantic(name, value, DisplayPath::of));
  }

  public static FieldValue orUnset(Optional<FieldValue.Text> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value.<FieldValue>map(text -> text).orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue text(String value) {
    return new FieldValue.Text(Objects.requireNonNull(value, LITERAL_VALUE));
  }

  public static FieldValue numeric(long value) {
    return new FieldValue.Numeric(value);
  }

  public static FieldValue flag(boolean value) {
    return new FieldValue.Flag(value);
  }

  public static FieldValue id(ProtocolId value) {
    return numeric(Objects.requireNonNull(value, LITERAL_VALUE).value());
  }

  public static FieldValue optionalIdValue(Optional<? extends ProtocolId> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(identifier -> new FieldValue.Text(Long.toString(identifier.value())))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue enumValue(WireEnum value) {
    return text(Objects.requireNonNull(value, LITERAL_VALUE).wireValue());
  }

  public static FieldValue optionalEnumValue(Optional<? extends WireEnum> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(item -> new FieldValue.Text(item.wireValue()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue httpStatusCode(HttpStatusCode value) {
    return text(Objects.requireNonNull(value, LITERAL_VALUE).wireValue());
  }

  public static FieldValue optionalHttpStatusCodeValue(Optional<HttpStatusCode> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(status -> new FieldValue.Text(status.wireValue()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue elapsedMilliseconds(ElapsedMilliseconds value) {
    return text(Objects.requireNonNull(value, LITERAL_VALUE).wireValue());
  }

  public static FieldValue optionalElapsedMillisecondsValue(Optional<ElapsedMilliseconds> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(elapsed -> new FieldValue.Text(elapsed.wireValue()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue optionalStringValue(Optional<String> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value.<FieldValue>map(FieldValue.Text::new).orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue instant(Instant value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return new FieldValue.Numeric(Long.parseLong(JstWireTimestamp.format(value)));
  }

  public static FieldValue optionalInstantValue(Optional<Instant> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(instant -> new FieldValue.Text(JstWireTimestamp.format(instant)))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue uuid(UUID value) {
    return text(Objects.requireNonNull(value, LITERAL_VALUE).toString());
  }

  public static FieldValue optionalUuidValue(Optional<UUID> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(uuid -> new FieldValue.Text(uuid.toString()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue optionalAuthenticationContextValue(
      Optional<AuthenticationContext> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(context -> new FieldValue.Text(context.wireValue()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue sha256(Sha256Hex value) {
    return text(Objects.requireNonNull(value, LITERAL_VALUE).wireValue());
  }

  public static FieldValue optionalSha256Value(Optional<Sha256Hex> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(sha -> new FieldValue.Text(sha.wireValue()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue relativePath(RelativePath value) {
    return text(Objects.requireNonNull(value, LITERAL_VALUE).wireValue());
  }

  public static FieldValue optionalRelativePathValue(Optional<RelativePath> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(path -> new FieldValue.Text(path.wireValue()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static FieldValue displayPath(DisplayPath value) {
    return text(Objects.requireNonNull(value, LITERAL_VALUE).wireValue());
  }

  public static FieldValue optionalDisplayPathValue(Optional<DisplayPath> value) {
    Objects.requireNonNull(value, LITERAL_VALUE);
    return value
        .<FieldValue>map(path -> new FieldValue.Text(path.wireValue()))
        .orElse(FieldValue.Unset.INSTANCE);
  }

  public static void requireEmpty(FieldValueSet fields) {
    Objects.requireNonNull(fields, "fields");
    if (fields.size() != 0) {
      throw new LayoutValidationException("empty data record contains fields");
    }
  }

  private static FieldValue require(FieldValueSet fields, String name) {
    Objects.requireNonNull(fields, "fields");
    Objects.requireNonNull(name, "name");
    return fields.getOrUnset(name);
  }

  private static LayoutValidationException wrongType(String name) {
    return new LayoutValidationException("typed field has the wrong value kind: " + name);
  }

  private static UUID canonicalUuid(String value) {
    UUID uuid = UUID.fromString(value);
    if (!uuid.toString().equals(value)) {
      throw new IllegalArgumentException("UUID is not lowercase canonical form");
    }
    return uuid;
  }

  private static long parseOptionalId(String value) {
    if (!INSTANCE.retainedOptionalId.matcher(value).matches()) {
      throw new IllegalArgumentException("optional protocol ID must contain 1 to 12 ASCII digits");
    }
    return Long.parseLong(value);
  }

  private static <E extends Enum<E> & WireEnum> E enumConstant(Class<E> type, String wire) {
    // E extends Enum<E>: null is impossible for the closed enum catalog (BUG-016/YKT-013).
    for (E candidate : Objects.requireNonNull(type.getEnumConstants(), "enum constants")) {
      if (candidate.wireValue().equals(wire)) {
        return candidate;
      }
    }
    throw new IllegalArgumentException("wire enum value is not allowlisted");
  }

  private static <T extends ProtocolId> T semanticId(
      String name, long value, LongFunction<T> factory) {
    try {
      return factory.apply(value);
    } catch (IllegalArgumentException exception) {
      throw new LayoutValidationException(
          "typed field has an invalid semantic value: " + name, exception);
    }
  }

  private static <T> T semantic(String name, String value, Function<String, T> factory) {
    try {
      return factory.apply(value);
    } catch (IllegalArgumentException exception) {
      throw new LayoutValidationException(
          "typed field has an invalid semantic value: " + name, exception);
    }
  }
}
