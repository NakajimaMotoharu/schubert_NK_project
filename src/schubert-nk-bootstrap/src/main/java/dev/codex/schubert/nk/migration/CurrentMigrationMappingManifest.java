package dev.codex.schubert.nk.migration;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.HexFormat;
import java.util.Map;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Bound declared ID correspondence, never actual Current data, persistence or authority proof.
 * NK-MIG-001; MIG003005006/MIG-DAT005/TST; UI223242254; SS311331343 SSC408; PT-MIG-MAPMAN001..008.
 * Existing canonical part bytes retain their original ID/order contracts.
 */
@NullMarked
@Immutable
public final class CurrentMigrationMappingManifest {
  private final byte[] retainedBytes;
  private final String retainedSha256;
  private final Map<String, Integer> retainedCounts;

  public CurrentMigrationMappingManifest(
      @Nullable ScenarioFileMigrationMap files,
      @Nullable ScenarioEntryPlacementMap entries,
      @Nullable SpeakerMigrationMap speakers,
      @Nullable AudioMigrationMap audio)
      throws NoSuchAlgorithmException {
    if (files == null || entries == null || speakers == null || audio == null) throw invalid();
    var gamesByTargetFile = new HashMap<Long, Integer>();
    for (var file : files.files()) gamesByTargetFile.put(file.targetFileId(), file.gameId());
    for (var entry : entries.entries()) {
      @Nullable Integer game = gamesByTargetFile.get(entry.targetFileId());
      if (game == null || game.intValue() != entry.gameId()) throw invalid();
    }
    var digest = MessageDigest.getInstance("SHA-256");
    var output = new ByteArrayOutputStream();
    output.writeBytes("NKMIGMAPPING1\n".getBytes(StandardCharsets.US_ASCII));
    append(output, digest, "FILES", files.files().size(), files.canonicalBytes());
    append(output, digest, "ENTRIES", entries.entries().size(), entries.canonicalBytes());
    append(output, digest, "SPEAKERS", speakers.mappings().size(), speakers.canonicalBytes());
    append(output, digest, "AUDIO", audio.mappings().size(), audio.canonicalBytes());
    retainedBytes = output.toByteArray();
    retainedSha256 = HexFormat.of().formatHex(digest.digest(retainedBytes));
    retainedCounts =
        Map.copyOf(
            Map.of(
                "FILES", files.files().size(),
                "ENTRIES", entries.entries().size(),
                "SPEAKERS", speakers.mappings().size(),
                "AUDIO", audio.mappings().size()));
  }

  public byte[] canonicalBytes() {
    return retainedBytes.clone();
  }

  public String sha256() {
    return retainedSha256;
  }

  public Map<String, Integer> rowCounts() {
    return retainedCounts;
  }

  private static void append(
      ByteArrayOutputStream output, MessageDigest digest, String kind, int rows, byte[] data) {
    String header =
        kind
            + "\t"
            + rows
            + "\t"
            + data.length
            + "\t"
            + HexFormat.of().formatHex(digest.digest(data))
            + "\n";
    output.writeBytes(header.getBytes(StandardCharsets.US_ASCII));
    output.writeBytes(data);
  }

  @Override
  public String toString() {
    return "CurrentMigrationMappingManifest[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration mapping manifest input is invalid");
  }
}
