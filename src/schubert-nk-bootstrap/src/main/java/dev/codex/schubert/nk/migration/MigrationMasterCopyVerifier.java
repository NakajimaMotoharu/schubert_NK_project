package dev.codex.schubert.nk.migration;

import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * Retained byte declaration verification, never file, signature, authority or migration admission.
 * NK-MIG-001; MIG003005006/MIG-DAT005/TST; UI223242254; SS311343 SSC416; PT-MIG-COPYVERIFY001..020.
 * Caller authenticates the expected SHA and the original byte source.
 */
@NullMarked
public final class MigrationMasterCopyVerifier {
  public MigrationMasterCopyManifest verify(
      byte @Nullable [] retained,
      @Nullable String expectedSha,
      @Nullable CurrentMigrationMappingManifest mappings,
      @Nullable MigrationMasterCopyDataset declared)
      throws IOException, NoSuchAlgorithmException {
    if (retained == null
        || expectedSha == null
        || mappings == null
        || declared == null
        || !expectedSha.matches("[0-9a-f]{64}")) throw invalid();
    byte[] stable = retained.clone();
    String actual = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(stable));
    if (!actual.equals(expectedSha)) throw invalid();
    var manifest = new MigrationMasterCopyManifest(mappings, declared);
    if (!MessageDigest.isEqual(stable, manifest.canonicalBytes())) throw invalid();
    return manifest;
  }

  @Override
  public String toString() {
    return "MigrationMasterCopyVerifier[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration retained COPY declaration is invalid");
  }
}
