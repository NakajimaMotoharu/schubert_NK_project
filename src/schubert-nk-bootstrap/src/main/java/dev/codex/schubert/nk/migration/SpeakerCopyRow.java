package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared speakers COPY row, never extraction, normalization derivation or FK/DB acceptance.
 * NK-MIG-001; MIG003005006/MIG-DAT005/FUN004/DAT004/TST; UI223233242254; SS311/331/V002/343 SSC367;
 * PT-MIG-SPEAKERROW001..016.
 */
@NullMarked
@Immutable
public final class SpeakerCopyRow {
  private static final int MAXIMUM_NAME_BYTES = 128;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final List<String> COLUMN_ORDER =
      List.of("id", "game_id", "name", "normalized_name", "is_protagonist", "notes", "created_at");
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final List<@Nullable String> retainedFields;

  public SpeakerCopyRow(@Nullable List<@Nullable String> input) {
    if (input == null) throw invalid();
    var fields = new ArrayList<@Nullable String>(input);
    if (fields.size() != COLUMN_ORDER.size()) throw invalid();
    if (!required(fields, 0).matches("[1-9][0-9]{0,11}")) throw invalid();
    String game = required(fields, 1);
    if (!game.equals("1") && !game.equals("2")) throw invalid();
    name(required(fields, 2));
    name(required(fields, 3));
    String protagonist = required(fields, 4);
    if (!protagonist.equals("true") && !protagonist.equals("false")) throw invalid();
    @Nullable String notes = fields.get(5);
    if (notes != null) text(notes);
    timestamp(required(fields, 6));
    retainedFields = Collections.unmodifiableList(fields);
  }

  public List<String> columnNames() {
    return COLUMN_ORDER;
  }

  public List<@Nullable String> fields() {
    return retainedFields;
  }

  public byte[] copyBytes(@Nullable PostgresCopyTextEncoder encoder) {
    if (encoder == null) throw invalid();
    return encoder.encodeRow(retainedFields);
  }

  @Override
  public String toString() {
    return "SpeakerCopyRow[REDACTED]";
  }

  private static String required(List<@Nullable String> fields, int index) {
    @Nullable String value = fields.get(index);
    if (value == null) throw invalid();
    return value;
  }

  private static void name(String value) {
    text(value);
    int bytes = value.getBytes(StandardCharsets.UTF_8).length;
    if (bytes < 1 || bytes > MAXIMUM_NAME_BYTES) throw invalid();
  }

  private static void text(String value) {
    if (!StandardCharsets.UTF_8.newEncoder().canEncode(value)
        || !Normalizer.isNormalized(value, Normalizer.Form.NFC)
        || value.indexOf('\0') >= 0) throw invalid();
  }

  private static void timestamp(String text) {
    Instant value;
    try {
      value = Instant.parse(text);
    } catch (DateTimeParseException failure) {
      throw invalid();
    }
    if (value.isBefore(EARLIEST) || value.isAfter(LATEST)) throw invalid();
    if (value.getNano() % NANOSECONDS_PER_MICROSECOND != 0 || !value.toString().equals(text))
      throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration speaker COPY row is invalid");
  }
}
