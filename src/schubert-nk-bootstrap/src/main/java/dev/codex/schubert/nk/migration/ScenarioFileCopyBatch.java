package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared script_files COPY batch, never an actual source/asset/DB qualification. NK-MIG-001;
 * MIG003005006/MIG-DAT004005/DAT004/FUN004; UI223/242/254; SS331/V002/343 section10 SSC349;
 * PT-MIG-FCOPY001..014.
 */
@NullMarked
public final class ScenarioFileCopyBatch {
  private static final int MAXIMUM_TRANSACTION_TIMESTAMPS = 1;
  private static final int MAXIMUM_SECTION_CODEPOINTS = 64;
  private static final int MICROSECOND_NANOS = 1000;
  private static final List<String> COLUMN_ORDER =
      List.of(
          "id",
          "game_id",
          "display_order",
          "storage_relative_path",
          "display_path",
          "file_name",
          "section_code",
          "chapter_title",
          "sha256",
          "byte_size",
          "created_at");
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final List<List<@Nullable String>> retainedRows;

  public ScenarioFileCopyBatch(
      @Nullable ScenarioFileMigrationMap mapping, @Nullable List<List<@Nullable String>> input) {
    if (mapping == null || input == null) throw invalid();
    if (input.size() != mapping.files().size()) throw invalid();
    var byTarget = new HashMap<Long, List<@Nullable String>>();
    var storagePaths = new HashSet<String>();
    var timestamps = new HashSet<String>();
    for (List<@Nullable String> row : input) {
      if (row == null) throw invalid();
      var snapshot = new ArrayList<@Nullable String>(row);
      validateRow(snapshot);
      long id = Long.parseLong(required(snapshot, 0));
      if (byTarget.put(id, Collections.unmodifiableList(snapshot)) != null) throw invalid();
      // Validated game is one ASCII digit; validated storage path cannot contain a tab.
      if (!storagePaths.add(required(snapshot, 1) + '\t' + required(snapshot, 3))) throw invalid();
      timestamps.add(required(snapshot, 10));
    }
    if (timestamps.size() > MAXIMUM_TRANSACTION_TIMESTAMPS) throw invalid();
    var ordered = new ArrayList<List<@Nullable String>>();
    for (var file : mapping.files()) {
      @Nullable List<@Nullable String> row = byTarget.get(file.targetFileId());
      if (row == null) throw invalid();
      var expected =
          List.of(
              Long.toString(file.targetFileId()),
              Integer.toString(file.gameId()),
              Long.toString(file.displayOrder()));
      if (!row.subList(0, 3).equals(expected)) throw invalid();
      ordered.add(row);
    }
    retainedRows = List.copyOf(ordered);
  }

  public List<String> columnNames() {
    return COLUMN_ORDER;
  }

  public List<List<@Nullable String>> rows() {
    return retainedRows;
  }

  public byte[] copyBytes(@Nullable PostgresCopyTextEncoder encoder) {
    if (encoder == null) throw invalid();
    return encoder.encodeRows(retainedRows);
  }

  @Override
  public String toString() {
    return "ScenarioFileCopyBatch[REDACTED]";
  }

  private static void validateRow(List<@Nullable String> row) {
    if (row.size() != COLUMN_ORDER.size()) throw invalid();
    n12(required(row, 0), false);
    if (!required(row, 1).matches("[12]")) throw invalid();
    n12(required(row, 2), false);
    String storage = required(row, 3);
    text(storage, 1, 512);
    if (storage.startsWith("/") || storage.indexOf('\\') >= 0) throw invalid();
    for (String segment : storage.split("/", -1)) {
      if (segment.isEmpty() || segment.equals(".") || segment.equals("..")) throw invalid();
    }
    text(required(row, 4), 1, 512);
    text(required(row, 5), 1, 256);
    @Nullable String section = row.get(6);
    if (section != null) {
      text(section, 0, Integer.MAX_VALUE);
      if (section.codePointCount(0, section.length()) > MAXIMUM_SECTION_CODEPOINTS) throw invalid();
    }
    @Nullable String chapter = row.get(7);
    if (chapter != null) text(chapter, 0, 256);
    if (!required(row, 8).matches("[0-9a-f]{64}")) throw invalid();
    n12(required(row, 9), true);
    String stamp = required(row, 10);
    Instant instant;
    try {
      instant = Instant.parse(stamp);
    } catch (DateTimeParseException failure) {
      throw invalid();
    }
    if (instant.isBefore(EARLIEST) || instant.isAfter(LATEST)) throw invalid();
    if (instant.getNano() % MICROSECOND_NANOS != 0 || !instant.toString().equals(stamp))
      throw invalid();
  }

  private static String required(List<@Nullable String> row, int index) {
    @Nullable String value = row.get(index);
    if (value == null) throw invalid();
    return value;
  }

  private static void n12(String value, boolean zero) {
    if (!(zero && value.equals("0")) && !value.matches("[1-9][0-9]{0,11}")) throw invalid();
  }

  private static void text(String value, int minimumBytes, int maximumBytes) {
    if (!StandardCharsets.UTF_8.newEncoder().canEncode(value)) throw invalid();
    if (!Normalizer.isNormalized(value, Normalizer.Form.NFC)) throw invalid();
    for (int offset = 0; offset < value.length(); offset++) {
      if (Character.isISOControl(value.charAt(offset))) throw invalid();
    }
    int bytes = value.getBytes(StandardCharsets.UTF_8).length;
    if (bytes < minimumBytes || bytes > maximumBytes) throw invalid();
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration file COPY batch is invalid");
  }
}
