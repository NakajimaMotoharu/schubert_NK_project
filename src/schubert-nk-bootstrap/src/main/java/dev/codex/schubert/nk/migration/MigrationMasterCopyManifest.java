package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Map;
import javax.annotation.concurrent.Immutable;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Declared four-map SHA bound to six streamed COPY tuples, never actual data or authorization.
 * NK-MIG-001; MIG003005006/MIG-DAT005/TST; UI223242254; SS311343 SSC410; PT-MIG-COPYMAN001..012. No
 * FS/DB/asset/signature operations or retained wire payload.
 */
@NullMarked
@Immutable
public final class MigrationMasterCopyManifest {
  private final byte[] retainedBytes;
  private final String retainedSha256;
  private final String retainedMappingSha256;
  private final Map<String, Long> retainedCounts;

  public MigrationMasterCopyManifest(
      @Nullable CurrentMigrationMappingManifest mappings,
      @Nullable MigrationMasterCopyDataset declared)
      throws IOException, NoSuchAlgorithmException {
    if (mappings == null || declared == null) throw invalid();
    var counts = mappings.rowCounts();
    var content = declared.content();
    if (!Integer.valueOf(content.scenario().files().rows().size()).equals(counts.get("FILES"))
        || !Integer.valueOf(content.scenario().entries().rows().size())
            .equals(counts.get("ENTRIES"))
        || !Integer.valueOf(declared.speakers().rows().size()).equals(counts.get("SPEAKERS"))
        || !Integer.valueOf(content.audio().audioRows().size()).equals(counts.get("AUDIO")))
      throw invalid();
    var fingerprints = new MigrationMasterCopyFingerprint().fingerprint(declared);
    retainedMappingSha256 = mappings.sha256();
    var text =
        new StringBuilder("NKMIGCOPY1\nMAPPING\t").append(retainedMappingSha256).append('\n');
    for (var item : fingerprints)
      text.append(item.table())
          .append('\t')
          .append(item.rows())
          .append('\t')
          .append(item.bytes())
          .append('\t')
          .append(item.sha256())
          .append('\n');
    retainedBytes = text.toString().getBytes(StandardCharsets.US_ASCII);
    retainedSha256 =
        HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(retainedBytes));
    retainedCounts =
        Map.of(
            "speakers",
            fingerprints.get(0).rows(),
            "script_files",
            fingerprints.get(1).rows(),
            "script_entries",
            fingerprints.get(2).rows(),
            "audio_files",
            fingerprints.get(3).rows(),
            "media_assets",
            fingerprints.get(4).rows(),
            "entry_audio_links",
            fingerprints.get(5).rows());
  }

  public byte[] canonicalBytes() {
    return retainedBytes.clone();
  }

  public String sha256() {
    return retainedSha256;
  }

  public String mappingSha256() {
    return retainedMappingSha256;
  }

  public Map<String, Long> rowCounts() {
    return retainedCounts;
  }

  @Override
  public String toString() {
    return "MigrationMasterCopyManifest[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration COPY manifest input is invalid");
  }
}
