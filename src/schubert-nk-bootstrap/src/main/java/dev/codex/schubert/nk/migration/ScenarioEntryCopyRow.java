package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared script_entries COPY row; no actual DB, FK, source extraction or migration witness.
 * NK-MIG-001; MIG003005006/MIG-DAT004005/DAT004/FUN004; UI223/242 section4.4/254; SS331
 * section2/V002/343 section10 SSC347; PT-MIG-ROW001..012.
 */
@NullMarked
public final class ScenarioEntryCopyRow {
  private static final List<String> COLUMN_ORDER =
      List.of(
          "id",
          "game_id",
          "script_file_id",
          "display_order",
          "entry_index",
          "line_number",
          "entry_type",
          "speaker_id",
          "speaker_label",
          "body",
          "raw_block",
          "created_at");
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final List<@Nullable String> retainedFields;

  public ScenarioEntryCopyRow(List<@Nullable String> input) {
    var fields = new ArrayList<@Nullable String>(input);
    if (fields.size() != COLUMN_ORDER.size()) throw invalid();
    n12(required(fields, 0));
    String game = required(fields, 1);
    if (!game.equals("1") && !game.equals("2")) throw invalid();
    n12(required(fields, 2));
    n12(required(fields, 3));
    integer(required(fields, 4), false);
    @Nullable String line = fields.get(5);
    if (line != null) integer(line, true);
    String type = required(fields, 6);
    @Nullable String speaker = fields.get(7);
    if (type.equals("dialogue")) {
      if (speaker == null) throw invalid();
      n12(speaker);
    } else if (type.equals("narration")) {
      if (speaker != null) throw invalid();
    } else {
      throw invalid();
    }
    @Nullable String label = fields.get(8);
    if (label != null && textBytes(label, false) > 128) throw invalid();
    int bodyBytes = textBytes(required(fields, 9), true);
    if (bodyBytes < 1 || bodyBytes > 4096) throw invalid();
    // raw_block is nonnull text without the body's byte ceiling in the existing DDL.
    textBytes(required(fields, 10), true);
    timestamp(required(fields, 11));
    retainedFields = Collections.unmodifiableList(fields);
  }

  public List<String> columnNames() {
    return COLUMN_ORDER;
  }

  public List<@Nullable String> fields() {
    return retainedFields;
  }

  public byte[] copyBytes(PostgresCopyTextEncoder encoder) {
    return Objects.requireNonNull(encoder, "COPY text encoder").encodeRow(retainedFields);
  }

  @Override
  public String toString() {
    return "ScenarioEntryCopyRow[REDACTED]";
  }

  private static String required(List<@Nullable String> fields, int index) {
    return Objects.requireNonNull(fields.get(index), "required migration field");
  }

  private static void n12(String value) {
    if (!value.matches("[1-9][0-9]{0,11}")) throw invalid();
  }

  private static void integer(String text, boolean positive) {
    if (!text.matches("0|[1-9][0-9]{0,9}")) throw invalid();
    // The grammar bounds the parse to ten digits, safely within long before the int check.
    long value = Long.parseLong(text);
    if (value > Integer.MAX_VALUE || (positive && value == 0)) throw invalid();
  }

  private static int textBytes(String value, boolean multiline) {
    if (!StandardCharsets.UTF_8.newEncoder().canEncode(value)) throw invalid();
    if (!Normalizer.isNormalized(value, Normalizer.Form.NFC)) throw invalid();
    for (int index = 0; index < value.length(); index++) {
      char current = value.charAt(index);
      if (Character.isISOControl(current)
          && !(multiline && (current == '\t' || current == '\n' || current == '\r')))
        throw invalid();
    }
    return value.getBytes(StandardCharsets.UTF_8).length;
  }

  private static void timestamp(String text) {
    Instant value;
    try {
      value = Instant.parse(text);
    } catch (DateTimeParseException failure) {
      throw invalid();
    }
    if (value.isBefore(EARLIEST) || value.isAfter(LATEST)) throw invalid();
    if (value.getNano() % 1000 != 0 || !value.toString().equals(text)) throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration scenario COPY row is invalid");
  }
}
