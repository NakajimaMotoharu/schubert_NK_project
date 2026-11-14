package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;
import java.text.Normalizer;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared media_assets row under V002+V029, not a catalogue, real asset or full migration witness.
 * NK-MIG-001; MIG-DAT-003/MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004;
 * UI223/242/243/254; SS311/331/333/343 SSC357; PT-MIG-MEDIAROW001..020.
 */
@NullMarked
public final class MediaAssetCopyRow {
  private static final int MINIMUM_TEXT_BYTES = 1;
  private static final int NANOSECONDS_PER_MICROSECOND = 1000;
  private static final List<String> COLUMN_ORDER =
      List.of(
          "id",
          "logical_id",
          "media_type",
          "title",
          "category",
          "section",
          "storage_relative_path",
          "display_path",
          "file_name",
          "byte_size",
          "sha256",
          "mime_type",
          "parent_logical_id",
          "pair_key",
          "pair_role",
          "display_order",
          "created_at");
  private static final Map<String, String> MUSIC_MIMES =
      Map.of(
          ".m4a",
          "audio/mp4",
          ".mp3",
          "audio/mpeg",
          ".ogg",
          "audio/ogg",
          ".wav",
          "audio/wav",
          ".flac",
          "audio/flac");
  private static final Instant EARLIEST = Instant.parse("0001-01-01T00:00:00Z");
  private static final Instant LATEST = Instant.parse("9999-12-31T23:59:59.999999Z");
  private final List<@Nullable String> retainedFields;

  public MediaAssetCopyRow(@Nullable List<@Nullable String> input) throws NoSuchAlgorithmException {
    if (input == null) throw invalid();
    var fields = new ArrayList<@Nullable String>(input);
    if (fields.size() != COLUMN_ORDER.size()) throw invalid();
    positiveN12(required(fields, 0));
    String logicalId = required(fields, 1);
    boundedText(logicalId, 64);
    String type = required(fields, 2);
    if (!type.equals("VIDEO") && !type.equals("MUSIC")) throw invalid();
    boundedText(required(fields, 3), 256);
    boundedText(required(fields, 4), 64);
    @Nullable String section = fields.get(5);
    if (section != null && textBytes(section) > 128) throw invalid();
    String storage = required(fields, 6);
    boundedText(storage, 512);
    storagePath(storage);
    String display = required(fields, 7);
    boundedText(display, 512);
    boundedText(required(fields, 8), 256);
    positiveN12(required(fields, 9));
    if (!required(fields, 10).matches("[0-9a-f]{64}")) throw invalid();
    String mime = required(fields, 11);
    mime(type, storage, mime);
    @Nullable String parent = fields.get(12);
    if (parent != null) boundedText(parent, 64);
    pair(type, fields.get(13), fields.get(14));
    if (!required(fields, 15).matches("[1-9][0-9]{0,3}")) throw invalid();
    timestamp(required(fields, 16));
    if (type.equals("MUSIC") && !logicalId.equals(new MusicLogicalId().fromDisplayPath(display)))
      throw invalid();
    retainedFields = Collections.unmodifiableList(fields);
  }

  public String id() {
    return required(retainedFields, 0);
  }

  public String logicalId() {
    return required(retainedFields, 1);
  }

  public String mediaType() {
    return required(retainedFields, 2);
  }

  public String storageRelativePath() {
    return required(retainedFields, 6);
  }

  public String displayPath() {
    return required(retainedFields, 7);
  }

  public String byteSize() {
    return required(retainedFields, 9);
  }

  public String sha256() {
    return required(retainedFields, 10);
  }

  public String createdAt() {
    return required(retainedFields, 16);
  }

  public Optional<String> parentLogicalId() {
    return Optional.ofNullable(retainedFields.get(12));
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
    return "MediaAssetCopyRow[REDACTED]";
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

  private static void mime(String type, String path, String value) {
    if (type.equals("VIDEO")) {
      if (!path.endsWith(".mp4") || !value.equals("video/mp4")) throw invalid();
    } else {
      int dot = path.lastIndexOf('.');
      if (dot < 0) throw invalid();
      @Nullable String expected = MUSIC_MIMES.get(path.substring(dot));
      if (expected == null || !expected.equals(value)) throw invalid();
    }
  }

  private static void pair(String type, @Nullable String key, @Nullable String role) {
    if (type.equals("VIDEO")) {
      if (key != null || role != null) throw invalid();
    } else {
      if (role == null) throw invalid();
      if (role.equals("N")) {
        if (key != null) throw invalid();
      } else if (role.equals("M") || role.equals("I")) {
        if (key == null) throw invalid();
        boundedText(key, 256);
      } else {
        throw invalid();
      }
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
    return new IllegalArgumentException("migration media asset COPY row is invalid");
  }
}
