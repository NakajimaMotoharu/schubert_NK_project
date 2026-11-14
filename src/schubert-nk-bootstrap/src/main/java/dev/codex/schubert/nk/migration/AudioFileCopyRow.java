package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared audio_files COPY row, never an actual asset, FK, DB or full migration witness.
 * NK-MIG-001; MIG-DAT-002/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004; UI227/242/254;
 * SS311/331/V002/343 section10 SSC354; PT-MIG-AUDIOROW001..016.
 */
@NullMarked
public final class AudioFileCopyRow {
  private static final int MINIMUM_TEXT_BYTES = 1;
  private static final int MAXIMUM_CONTAINER_CHARACTERS = 16;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final List<String> COLUMN_ORDER =
      List.of(
          "id",
          "game_id",
          "storage_relative_path",
          "display_path",
          "file_name",
          "basename",
          "audio_role",
          "container",
          "duration_ms",
          "byte_size",
          "sha256",
          "created_at");
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final List<@Nullable String> retainedFields;

  public AudioFileCopyRow(@Nullable List<@Nullable String> input) {
    if (input == null) throw invalid();
    var fields = new ArrayList<@Nullable String>(input);
    if (fields.size() != COLUMN_ORDER.size()) throw invalid();
    positiveN12(required(fields, 0));
    String game = required(fields, 1);
    if (!game.equals("1") && !game.equals("2")) throw invalid();
    String path = required(fields, 2);
    boundedText(path, 512);
    storagePath(path);
    boundedText(required(fields, 3), 512);
    boundedText(required(fields, 4), 256);
    boundedText(required(fields, 5), 255);
    boundedText(required(fields, 6), 8);
    @Nullable String container = fields.get(7);
    if (container != null) {
      textBytes(container);
      if (container.codePointCount(0, container.length()) > MAXIMUM_CONTAINER_CHARACTERS)
        throw invalid();
    }
    @Nullable String duration = fields.get(8);
    if (duration != null && !duration.matches("0|[1-9][0-9]{0,11}")) throw invalid();
    positiveN12(required(fields, 9));
    if (!required(fields, 10).matches("[0-9a-f]{64}")) throw invalid();
    timestamp(required(fields, 11));
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
    return "AudioFileCopyRow[REDACTED]";
  }

  private static String required(List<@Nullable String> fields, int index) {
    @Nullable String value = fields.get(index);
    if (value == null) throw invalid();
    return value;
  }

  private static void positiveN12(String value) {
    if (!value.matches("[1-9][0-9]{0,11}")) throw invalid();
  }

  private static void boundedText(String value, int maximumBytes) {
    int size = textBytes(value);
    if (size < MINIMUM_TEXT_BYTES || size > maximumBytes) throw invalid();
  }

  private static int textBytes(String value) {
    if (!StandardCharsets.UTF_8.newEncoder().canEncode(value)) throw invalid();
    if (!Normalizer.isNormalized(value, Normalizer.Form.NFC)) throw invalid();
    for (int index = 0; index < value.length(); index++) {
      if (Character.isISOControl(value.charAt(index))) throw invalid();
    }
    return value.getBytes(StandardCharsets.UTF_8).length;
  }

  private static void storagePath(String value) {
    if (value.startsWith("/") || value.endsWith("/") || value.contains("\\")) throw invalid();
    for (String segment : value.split("/", -1)) {
      if (segment.isEmpty() || segment.equals(".") || segment.equals("..")) throw invalid();
    }
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
    return new IllegalArgumentException("migration audio COPY row is invalid");
  }
}
