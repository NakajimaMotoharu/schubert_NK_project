package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Memory readback bound to a separately retained expected digest, never Current/FS/authority proof.
 * NK-MIG-001; MIG003005006/MIG-DAT005/TST; UI223242254; SS311331343 SSC409;
 * PT-MIG-MAPVERIFY001..016.
 */
@NullMarked
public final class CurrentMigrationMappingVerifier {
  private static final byte[] MAGIC = "NKMIGMAPPING1\n".getBytes(StandardCharsets.US_ASCII);
  private static final List<String> KINDS = List.of("FILES", "ENTRIES", "SPEAKERS", "AUDIO");
  private static final List<String> HEADERS =
      List.of(
          "NKMIGFILEORDER1",
          "NKMIGENTRYPLACEMENT1",
          "game_id\tcurrent_speaker_id\ttarget_speaker_id",
          "game_id\tcurrent_audio_id\ttarget_audio_id");
  private static final List<Integer> WIDTHS = List.of(4, 6, 3, 3);
  private static final int MAXIMUM_HEADER_LINE_BYTES = 95;
  private static final int MAXIMUM_BODY_LINE_BYTES = 125;
  private static final String HASH_PATTERN = "[0-9a-f]{64}";
  private static final String SIGNED_PATTERN = "0|-?[1-9][0-9]{0,18}";

  public Map<String, Integer> verify(byte @Nullable [] candidate, @Nullable String expectedSha256)
      throws NoSuchAlgorithmException {
    if (candidate == null || expectedSha256 == null || !expectedSha256.matches(HASH_PATTERN))
      throw invalid();
    byte[] data = candidate.clone();
    var digest = MessageDigest.getInstance("SHA-256");
    if (!HexFormat.of().formatHex(digest.digest(data)).equals(expectedSha256)) throw invalid();
    if (data.length < MAGIC.length || !Arrays.equals(data, 0, MAGIC.length, MAGIC, 0, MAGIC.length))
      throw invalid();
    int cursor = MAGIC.length;
    var bodies = new ArrayList<byte[]>();
    int[] counts = new int[KINDS.size()];
    for (int part = 0; part < KINDS.size(); part++) {
      int end = lineEnd(data, cursor);
      String[] header =
          new String(data, cursor, end - cursor, StandardCharsets.US_ASCII).split("\t", -1);
      if (header.length != 4
          || !header[0].equals(KINDS.get(part))
          || !header[3].matches(HASH_PATTERN)) throw invalid();
      counts[part] = unsigned(header[1]);
      int bytes = unsigned(header[2]);
      cursor = end + 1;
      if (bytes > data.length - cursor) throw invalid();
      byte[] body = Arrays.copyOfRange(data, cursor, cursor + bytes);
      if (!HexFormat.of().formatHex(digest.digest(body)).equals(header[3])) throw invalid();
      bodies.add(body);
      cursor += bytes;
    }
    if (cursor != data.length) throw invalid();
    try {
      validateModels(bodies, counts);
    } catch (IllegalArgumentException ignored) {
      // Erase child numeric/model diagnostics and causes; never turn failure into success.
      throw invalid();
    }
    return Map.of(
        KINDS.get(0),
        counts[0],
        KINDS.get(1),
        counts[1],
        KINDS.get(2),
        counts[2],
        KINDS.get(3),
        counts[3]);
  }

  private static int lineEnd(byte[] data, int first) {
    int end = first;
    while (end < data.length && data[end] != '\n') {
      if (end - first >= MAXIMUM_HEADER_LINE_BYTES
          || (data[end] < 0x20 && data[end] != '\t')
          || data[end] > 0x7e) throw invalid();
      end++;
    }
    if (end == data.length) throw invalid();
    return end;
  }

  private static List<String[]> rows(byte[] body, int part, int expectedCount) {
    int first = 0;
    for (int index = 0; index < body.length; index++) {
      if (body[index] == '\n') {
        if (index - first > MAXIMUM_BODY_LINE_BYTES) throw invalid();
        first = index + 1;
      } else if ((body[index] < 0x20 && body[index] != '\t') || body[index] > 0x7e) throw invalid();
    }
    if (first != body.length) throw invalid();
    String[] lines = new String(body, StandardCharsets.US_ASCII).split("\n", -1);
    if (lines.length - 2 != expectedCount || !lines[0].equals(HEADERS.get(part))) throw invalid();
    var result = new ArrayList<String[]>();
    for (int index = 1; index < lines.length - 1; index++) {
      String[] values = lines[index].split("\t", -1);
      if (values.length != WIDTHS.get(part)) throw invalid();
      result.add(values);
    }
    return result;
  }

  private static void validateModels(List<byte[]> bodies, int[] counts) {
    var files = new ArrayList<ScenarioFileMigrationMap.FilePair>();
    for (String[] row : rows(bodies.get(0), 0, counts[0]))
      files.add(
          new ScenarioFileMigrationMap.FilePair(unsigned(row[0]), signed(row[1]), signed(row[2])));
    var fileMap = new ScenarioFileMigrationMap(files);
    exact(bodies.get(0), fileMap.canonicalBytes());
    var byTarget = new HashMap<Long, ScenarioFileMigrationMap.MappedFile>();
    for (var file : fileMap.files()) byTarget.put(file.targetFileId(), file);
    var ids = new ArrayList<ScenarioEntryMigrationMap.IdPair>();
    var placements = new ArrayList<ScenarioEntryPlacementMap.Placement>();
    for (String[] row : rows(bodies.get(1), 1, counts[1])) {
      long currentId = signed(row[0]);
      ids.add(new ScenarioEntryMigrationMap.IdPair(currentId, signed(row[1])));
      int game = unsigned(row[3]);
      ScenarioFileMigrationMap.@Nullable MappedFile file = byTarget.get(signed(row[4]));
      if (file == null || file.gameId() != game) throw invalid();
      placements.add(
          new ScenarioEntryPlacementMap.Placement(
              game, file.currentFileId(), currentId, unsigned(row[5])));
    }
    var entryMap =
        new ScenarioEntryPlacementMap(fileMap, new ScenarioEntryMigrationMap(ids), placements);
    exact(bodies.get(1), entryMap.canonicalBytes());
    var speakers = new ArrayList<SpeakerMigrationMap.@Nullable SpeakerMapping>();
    for (String[] row : rows(bodies.get(2), 2, counts[2]))
      speakers.add(
          new SpeakerMigrationMap.SpeakerMapping(unsigned(row[0]), signed(row[1]), signed(row[2])));
    exact(bodies.get(2), new SpeakerMigrationMap(speakers).canonicalBytes());
    validateAudio(bodies.get(3), counts[3]);
  }

  private static void validateAudio(byte[] body, int count) {
    boolean first = true;
    long previousCurrent = 0;
    long previousTarget = 0;
    var canonical = new StringBuilder(HEADERS.get(3)).append('\n');
    for (String[] row : rows(body, 3, count)) {
      var value =
          new AudioMigrationMap.AudioMapping(unsigned(row[0]), signed(row[1]), signed(row[2]));
      if ((!first && value.currentAudioId() <= previousCurrent)
          || value.targetAudioId() <= previousTarget) throw invalid();
      first = false;
      previousCurrent = value.currentAudioId();
      previousTarget = value.targetAudioId();
      canonical
          .append(value.gameId())
          .append('\t')
          .append(value.currentAudioId())
          .append('\t')
          .append(value.targetAudioId())
          .append('\n');
    }
    exact(body, canonical.toString().getBytes(StandardCharsets.US_ASCII));
  }

  private static long signed(String value) {
    if (!value.matches(SIGNED_PATTERN)) throw invalid();
    try {
      return Long.parseLong(value);
    } catch (NumberFormatException ignored) {
      throw invalid();
    }
  }

  private static int unsigned(String text) {
    long value = signed(text);
    if (value < 0 || value > Integer.MAX_VALUE) throw invalid();
    return (int) value;
  }

  private static void exact(byte[] actual, byte[] expected) {
    if (!Arrays.equals(actual, expected)) throw invalid();
  }

  @Override
  public String toString() {
    return "CurrentMigrationMappingVerifier[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration mapping serialization is invalid");
  }
}
