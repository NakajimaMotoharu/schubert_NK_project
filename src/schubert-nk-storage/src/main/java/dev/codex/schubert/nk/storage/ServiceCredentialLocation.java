package dev.codex.schubert.nk.storage;

import java.nio.file.InvalidPathException;
import java.nio.file.Path;
import java.util.Map;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Non-secret systemd credential-directory admission before any private file IO. This does not
 * authenticate the inode, owner, ACL, readonly filesystem or credential bytes. NK-OPS-001;
 * SYS-002/004; UI243/253; SS342/343 §4/6; PG278/PT-OPS-CREDLOC-001..006; SSC-457.
 */
@NullMarked
public final class ServiceCredentialLocation {
  private static final String KEY = "CREDENTIALS_DIRECTORY";
  private static final String RETAINED_INVALID = "service credential location unavailable";
  private final Path retainedDirectory;

  private ServiceCredentialLocation(Path directory) {
    this.retainedDirectory = directory;
  }

  /**
   * Captures only the location; unrelated OS environment and credential bytes are never retained.
   */
  public static ServiceCredentialLocation read(Map<String, String> environment) {
    Objects.requireNonNull(environment, "environment");
    for (String key : environment.keySet()) {
      if (key == null || (key.equalsIgnoreCase(KEY) && !KEY.equals(key))) throw invalid();
    }
    String value = environment.get(KEY);
    if (value == null
        || value.isEmpty()
        || value.length() > 4096
        || value.indexOf('\0') >= 0
        || value.indexOf('\r') >= 0
        || value.indexOf('\n') >= 0) throw invalid();
    Path path;
    try {
      path = Path.of(value);
    } catch (InvalidPathException invalidPath) {
      // The platform exception can retain the input. Return only the fixed diagnostic.
      throw invalid();
    }
    if (!path.isAbsolute() || path.getNameCount() == 0 || !path.equals(path.normalize()))
      throw invalid();
    return new ServiceCredentialLocation(path);
  }

  /** The caller must still open and authenticate this exact directory as a held inode. */
  public Path directory() {
    return retainedDirectory;
  }

  @Override
  public String toString() {
    return "ServiceCredentialLocation[REDACTED]";
  }

  private static IllegalArgumentException invalid() {
    return new IllegalArgumentException(RETAINED_INVALID);
  }
}
