package dev.codex.schubert.nk.migration;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.text.Normalizer;
import java.util.HexFormat;
import org.jspecify.annotations.NullMarked;
import org.jspecify.annotations.Nullable;

/**
 * UI242's deterministic non-secret Music identity, never an asset or full migration witness.
 * NK-MIG-001; MIG-DAT-004/MIG-DAT-005/MIG-003/MIG-005/MIG-006/DAT-004; UI223/242/254; SS311/331/343
 * section10 SSC356; PT-MIG-MUSICID001..012.
 */
@NullMarked
public final class MusicLogicalId {
  private static final String PREFIX = "SCHUBERT-NK:MUSIC:";
  private static final int MINIMUM_PATH_BYTES = 1;
  private static final int MAXIMUM_PATH_BYTES = 512;

  /** Caller owns sanitization and Current-ID mapping; this method never resolves a file path. */
  public String fromDisplayPath(@Nullable String displayPath) throws NoSuchAlgorithmException {
    if (displayPath == null) throw invalid();
    if (!StandardCharsets.UTF_8.newEncoder().canEncode(displayPath)) throw invalid();
    String canonical = Normalizer.normalize(displayPath, Normalizer.Form.NFC);
    for (int index = 0; index < canonical.length(); index++) {
      if (Character.isISOControl(canonical.charAt(index))) throw invalid();
    }
    byte[] data = canonical.getBytes(StandardCharsets.UTF_8);
    if (data.length < MINIMUM_PATH_BYTES || data.length > MAXIMUM_PATH_BYTES) throw invalid();
    // Qualified Java25 supplies SHA-256. A broken provider environment propagates, never falls
    // back.
    var digest = MessageDigest.getInstance("SHA-256");
    digest.update(PREFIX.getBytes(StandardCharsets.UTF_8));
    return HexFormat.of().formatHex(digest.digest(data));
  }

  @Override
  public String toString() {
    return "MusicLogicalId[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("migration music logical ID input is invalid");
  }
}
