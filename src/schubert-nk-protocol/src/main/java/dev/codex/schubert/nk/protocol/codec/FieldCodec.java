package dev.codex.schubert.nk.protocol.codec;

import static dev.codex.schubert.nk.protocol.codec.FieldCodecRules.ASCII_SPACE;
import static dev.codex.schubert.nk.protocol.codec.FieldCodecRules.ASCII_ZERO;
import static dev.codex.schubert.nk.protocol.codec.FieldCodecRules.BOOLEAN_FIELD_LENGTH;
import static dev.codex.schubert.nk.protocol.codec.FieldCodecRules.LITERAL_FIELD;
import static dev.codex.schubert.nk.protocol.codec.FieldCodecRules.MINIMUM_FIELD_LENGTH;

import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.Arrays;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import org.jspecify.annotations.Nullable;

/** Strict X/N/B field codec. Trace: NK-PRO-002, UI 232 §4, SS 322 §4～§6. */
public interface FieldCodec {

  public static byte[] encodeText(@Nullable String value, int length, boolean mandatory) {
    requirePositiveLength(length);
    if (value == null || value.isEmpty()) {
      if (mandatory) {
        throw new FieldEncodingException("mandatory text field is empty");
      }
      return filled(length, ASCII_SPACE);
    }
    String normalized = Normalizer.normalize(value, Normalizer.Form.NFC);
    validateTextCharactersForEncode(normalized);
    byte[] encoded;
    try {
      ByteBuffer buffer =
          StandardCharsets.UTF_8
              .newEncoder()
              .onMalformedInput(CodingErrorAction.REPORT)
              .onUnmappableCharacter(CodingErrorAction.REPORT)
              .encode(java.nio.CharBuffer.wrap(normalized));
      encoded = new byte[buffer.remaining()];
      buffer.get(encoded);
    } catch (CharacterCodingException exception) {
      throw new FieldEncodingException("text field is not strict UTF-8", exception);
    }
    if (encoded.length > length) {
      throw new FieldEncodingException("text field exceeds its UTF-8 byte length");
    }
    byte[] result = filled(length, ASCII_SPACE);
    System.arraycopy(encoded, 0, result, 0, encoded.length);
    return result;
  }

  public static Optional<String> decodeText(byte[] field, boolean mandatory) {
    Objects.requireNonNull(field, LITERAL_FIELD);
    requireNonEmptyField(field);
    int valueEnd = field.length;
    while (valueEnd > 0 && field[valueEnd - 1] == ASCII_SPACE) {
      valueEnd--;
    }
    if (valueEnd == 0) {
      if (mandatory) {
        throw new PermanentProtocolException("mandatory text field is empty");
      }
      return Optional.empty();
    }
    String decoded;
    try {
      decoded =
          StandardCharsets.UTF_8
              .newDecoder()
              .onMalformedInput(CodingErrorAction.REPORT)
              .onUnmappableCharacter(CodingErrorAction.REPORT)
              .decode(ByteBuffer.wrap(field, 0, valueEnd))
              .toString();
    } catch (CharacterCodingException exception) {
      throw new PermanentProtocolException("text field contains invalid UTF-8", exception);
    }
    validateTextCharactersForDecode(decoded);
    if (!Normalizer.isNormalized(decoded, Normalizer.Form.NFC)) {
      throw new PermanentProtocolException("text field is not NFC canonical");
    }
    return Optional.of(decoded);
  }

  public static byte[] encodeNumeric(long value, int length, long minimum, long maximum) {
    requirePositiveLength(length);
    if (minimum < 0 || maximum < minimum || value < minimum || value > maximum) {
      throw new FieldEncodingException("numeric field is outside its semantic range");
    }
    String digits = Long.toString(value);
    if (digits.length() > length) {
      throw new FieldEncodingException("numeric field exceeds its wire length");
    }
    byte[] result = filled(length, ASCII_ZERO);
    byte[] encoded = digits.getBytes(StandardCharsets.US_ASCII);
    System.arraycopy(encoded, 0, result, length - encoded.length, encoded.length);
    return result;
  }

  public static long decodeNumeric(byte[] field, long minimum, long maximum) {
    Objects.requireNonNull(field, LITERAL_FIELD);
    requireNonEmptyField(field);
    if (minimum < 0 || maximum < minimum) {
      throw new IllegalArgumentException("invalid numeric semantic range");
    }
    for (byte current : field) {
      if (current < '0' || current > '9') {
        throw new PermanentProtocolException("numeric field contains a non-digit byte");
      }
    }
    long value = 0;
    for (byte current : field) {
      try {
        value = Math.addExact(Math.multiplyExact(value, 10), current - '0');
      } catch (ArithmeticException exception) {
        throw new PermanentProtocolException("numeric field overflows signed long", exception);
      }
    }
    if (value < minimum || value > maximum) {
      throw new PermanentProtocolException("numeric field is outside its semantic range");
    }
    return value;
  }

  public static OptionalLong decodeNumericOrErrorFiller(
      byte[] field, long minimum, long maximum, boolean errorProfile) {
    Objects.requireNonNull(field, LITERAL_FIELD);
    requireNonEmptyField(field);
    if (errorProfile && allBytes(field, ASCII_ZERO)) {
      return OptionalLong.empty();
    }
    return OptionalLong.of(decodeNumeric(field, minimum, maximum));
  }

  public static byte[] encodeBoolean(@Nullable Boolean value, boolean allowUnset) {
    if (value == null) {
      if (!allowUnset) {
        throw new FieldEncodingException("boolean field is required");
      }
      return new byte[] {ASCII_SPACE};
    }
    return new byte[] {(byte) (value ? '1' : '0')};
  }

  public static Optional<Boolean> decodeBoolean(byte[] field, boolean allowUnset) {
    Objects.requireNonNull(field, LITERAL_FIELD);
    if (field.length != BOOLEAN_FIELD_LENGTH) {
      throw new PermanentProtocolException("boolean field must be exactly one byte");
    }
    return switch (field[0]) {
      case '0' -> Optional.of(Boolean.FALSE);
      case '1' -> Optional.of(Boolean.TRUE);
      case ASCII_SPACE -> {
        if (!allowUnset) {
          throw new PermanentProtocolException("boolean field is unexpectedly unset");
        }
        yield Optional.empty();
      }
      default -> throw new PermanentProtocolException("boolean field contains an unknown byte");
    };
  }

  public static void requireSpaces(byte[] field) {
    Objects.requireNonNull(field, LITERAL_FIELD);
    requireNonEmptyField(field);
    if (!allBytes(field, ASCII_SPACE)) {
      throw new PermanentProtocolException("reserved field is not ASCII-space filled");
    }
  }

  private static void validateTextCharactersForEncode(String value) {
    if (value.endsWith(" ")) {
      throw new FieldEncodingException("text field ends with an ambiguous ASCII space");
    }
    if (containsForbiddenControl(value)) {
      throw new FieldEncodingException("text field contains a forbidden control character");
    }
  }

  private static void validateTextCharactersForDecode(String value) {
    if (containsForbiddenControl(value)) {
      throw new PermanentProtocolException("text field contains a forbidden control character");
    }
  }

  private static boolean containsForbiddenControl(String value) {
    return value.indexOf('\r') >= 0
        || value.indexOf('\n') >= 0
        || value.indexOf('\t') >= 0
        || value.indexOf('\0') >= 0;
  }

  private static boolean allBytes(byte[] field, byte expected) {
    for (byte current : field) {
      if (current != expected) {
        return false;
      }
    }
    return true;
  }

  private static byte[] filled(int length, byte value) {
    byte[] result = new byte[length];
    Arrays.fill(result, value);
    return result;
  }

  private static void requirePositiveLength(int length) {
    if (length < MINIMUM_FIELD_LENGTH) {
      throw new IllegalArgumentException("field length must be positive");
    }
  }

  private static void requireNonEmptyField(byte[] field) {
    if (field.length == 0) {
      throw new IllegalArgumentException("field slice must not be empty");
    }
  }
}
