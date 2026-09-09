package dev.codex.schubert.nk.api.maintenance;

import java.nio.file.Path;
import java.util.Objects;
import java.util.Set;
import org.jspecify.annotations.NullMarked;

/**
 * Non-secret immutable startup values, no IO. NK-DAT-001; DAT-009/OPS-009; UI212/251; SS343
 * 6.7/352; QA-046/SSC-049/PG-D-143; PT-DB-INBOX-209..211.
 */
@NullMarked
public record InspectorSettings(
    Path credentialRoot, String databaseUrl, Set<String> fingerprintVersions) {
  public InspectorSettings {
    Objects.requireNonNull(credentialRoot, "credential root");
    if (!credentialRoot.isAbsolute()
        || credentialRoot.getNameCount() == 0
        || !credentialRoot.equals(credentialRoot.normalize()))
      throw new IllegalArgumentException("inspector credential root is invalid");
    InspectorDatabaseConnections.databaseName(databaseUrl);
    fingerprintVersions = requireVersions(fingerprintVersions);
  }

  static Set<String> requireVersions(Set<String> versions) {
    Set<String> result = Set.copyOf(versions);
    if (result.isEmpty())
      throw new IllegalArgumentException("readable fingerprint versions are required");
    for (String version : result) {
      if (!version.matches("[A-Za-z0-9][A-Za-z0-9._-]{0,15}"))
        throw new IllegalArgumentException("fingerprint version is invalid");
    }
    return result;
  }

  @Override
  public Set<String> fingerprintVersions() {
    // BUG-135/YKT-106: keep the immutable copy contract explicit at the public boundary too.
    return Set.copyOf(fingerprintVersions);
  }

  @Override
  public String toString() {
    return "InspectorSettings[REDACTED]";
  }
}
