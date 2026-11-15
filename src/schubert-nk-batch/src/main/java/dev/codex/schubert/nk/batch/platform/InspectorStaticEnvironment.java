package dev.codex.schubert.nk.batch.platform;

import java.nio.charset.StandardCharsets;
import java.util.HashSet;
import java.util.Objects;
import java.util.regex.Pattern;
import org.jspecify.annotations.NullMarked;

/**
 * Map-before-loss validation of the rendered static file, not a shell parser or file admission.
 * NK-OPS-001; OPS-009/UI251/SS311/343 6.8; SSC-049/PG-D-151; PT-OPS-CFG-001..006. The caller owns
 * bounded IO, root/inode checks and continued source stability. The child still validates values
 * and credential permissions independently. No environment, URL or version is logged.
 */
@NullMarked
public interface InspectorStaticEnvironment {

  int MAXIMUM_BYTES = 65848;

  /** Exact ASCII source grammar; malformed content gets a fixed diagnostic without raw values. */
  static void requireValid(byte[] observed) {
    final int maximumInterfaceNamesCharacters = 65536;
    final int maximumTcpPort = 65535;
    final Pattern filePattern =
        Pattern.compile(
            "NK_INSPECTOR_DB_URL=jdbc:postgresql://127\\.0\\.0\\.1:([1-9][0-9]{0,4})/[a-z_][a-z0-9_]{0,62}\n"
                + "NK_INSPECTOR_FINGERPRINT_VERSIONS=([A-Za-z0-9,._-]+)\n");
    final Pattern versionPattern = Pattern.compile("[A-Za-z0-9][A-Za-z0-9._-]{0,15}");
    Objects.requireNonNull(observed, "static environment bytes");
    if (observed.length == 0 || observed.length > MAXIMUM_BYTES) throw invalid();
    // Non-ASCII bytes decode to replacement characters that the complete ASCII grammar rejects.
    var match = filePattern.matcher(new String(observed, StandardCharsets.US_ASCII));
    if (!match.matches()) throw invalid();
    if (Integer.parseInt(Objects.requireNonNull(match.group(1))) > maximumTcpPort) throw invalid();
    String names = Objects.requireNonNull(match.group(2));
    if (names.length() > maximumInterfaceNamesCharacters) throw invalid();
    var unique = new HashSet<String>();
    for (String version : names.split(",", -1)) {
      if (!versionPattern.matcher(version).matches() || !unique.add(version)) throw invalid();
    }
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException("inspector static environment is invalid");
  }
}
