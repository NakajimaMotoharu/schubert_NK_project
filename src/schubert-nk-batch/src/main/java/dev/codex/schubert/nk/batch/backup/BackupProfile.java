package dev.codex.schubert.nk.batch.backup;

import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;

/**
 * Nonsecret canonical claims only, NEVER release/tool authority. SS343/SSC110, BPROFILE001..004.
 */
@NullMarked
public record BackupProfile(BackupVersions versions, Map<String, String> toolHashes) {
  public static final int MAXIMUM_BYTES = 4096;
  private static final List<String> VERSION_KEYS =
      List.of("host", "app", "schema", "os", "jdk", "postgresql", "artemis", "age");
  public static final List<String> TOOL_KEYS =
      List.of(
          "pgDumpWrapperSha256",
          "pgRestoreWrapperSha256",
          "pgDumpSha256",
          "pgRestoreSha256",
          "tarSha256",
          "ageSha256",
          "artemisArtifactSha256");
  private static final Pattern GRAMMAR = grammar();

  public BackupProfile {
    Objects.requireNonNull(versions, "actual version claims");
    toolHashes = Map.copyOf(toolHashes);
    if (!toolHashes.keySet().equals(Set.copyOf(TOOL_KEYS))) throw invalid();
    for (String hash : toolHashes.values()) if (!hash.matches("[0-9a-f]{64}")) throw invalid();
  }

  @Override
  public Map<String, String> toolHashes() {
    return Map.copyOf(toolHashes);
  }

  public byte[] encode() {
    var values =
        List.of(
            versions.host(),
            versions.app(),
            versions.schema(),
            versions.os(),
            versions.jdk(),
            versions.postgresql(),
            versions.artemis(),
            versions.age());
    var text = new StringBuilder("{\"profile\":\"NKBACKUPPROFILE1\"");
    for (int i = 0; i < VERSION_KEYS.size(); i++) field(text, VERSION_KEYS.get(i), values.get(i));
    for (String key : TOOL_KEYS) field(text, key, Objects.requireNonNull(toolHashes.get(key)));
    return text.append("}\n").toString().getBytes(StandardCharsets.US_ASCII);
  }

  /** Wipes supplied bytes on every path, including malformed/noncanonical input. */
  public static BackupProfile consume(byte[] owned) {
    Objects.requireNonNull(owned, "owned profile bytes");
    try {
      if (owned.length < 1 || owned.length > MAXIMUM_BYTES) throw invalid();
      for (byte b : owned) if (b != 10 && (b < 32 || b > 126)) throw invalid();
      var match = GRAMMAR.matcher(new String(owned, StandardCharsets.US_ASCII));
      if (!match.matches()) throw invalid();
      var v =
          new BackupVersions(
              group(match, 1),
              group(match, 2),
              group(match, 3),
              group(match, 4),
              group(match, 5),
              group(match, 6),
              group(match, 7),
              group(match, 8));
      var hashes = new LinkedHashMap<String, String>();
      for (int i = 0; i < TOOL_KEYS.size(); i++) hashes.put(TOOL_KEYS.get(i), group(match, 9 + i));
      return new BackupProfile(v, hashes);
    } catch (IllegalArgumentException failure) {
      throw invalid();
    } finally {
      Arrays.fill(owned, (byte) 0);
    }
  }

  private static String group(java.util.regex.Matcher match, int number) {
    return Objects.requireNonNull(match.group(number), "required fixed profile group");
  }

  private static void field(StringBuilder out, String key, String value) {
    out.append(",\"").append(key).append("\":\"").append(value).append('"');
  }

  private static Pattern grammar() {
    var text = new StringBuilder("\\{\"profile\":\"NKBACKUPPROFILE1\"");
    for (String key : VERSION_KEYS)
      text.append(",\"").append(key).append("\":\"([A-Za-z0-9][A-Za-z0-9._+\\-]{0,127})\"");
    for (String key : TOOL_KEYS) text.append(",\"").append(key).append("\":\"([0-9a-f]{64})\"");
    return Pattern.compile(text.append("\\}\\n").toString());
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("backup profile invalid");
  }

  @Override
  public String toString() {
    return "BackupProfile[claims=<redacted>]";
  }
}
