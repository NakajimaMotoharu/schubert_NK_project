package dev.codex.schubert.nk.storage;

import java.nio.file.Path;
import java.util.List;

/**
 * Lexical deployment roots only; does not grant access or certify actual inodes/mounts. NK-SCN-001;
 * RD FIL-001..009; UI243; SS333 §2/343 §2; PG-D-058; PT-SCN-008-A05.
 */
public record StorageRootLayout(
    Path asset, Path transfer, Path backup, Path log, Path artemis, Path staging) {
  public StorageRootLayout {
    List<Path> roots = List.of(asset, transfer, backup, log, artemis, staging);
    for (Path root : roots) {
      if (!root.isAbsolute() || root.getNameCount() == 0 || !root.equals(root.normalize())) {
        throw new IllegalArgumentException("invalid storage root layout");
      }
    }
    for (int left = 0; left < roots.size(); left++) {
      for (int right = left + 1; right < roots.size(); right++) {
        if (roots.get(left).startsWith(roots.get(right))
            || roots.get(right).startsWith(roots.get(left))) {
          throw new IllegalArgumentException("overlapping storage roots");
        }
      }
    }
  }

  @Override
  public String toString() {
    return "StorageRootLayout[REDACTED]";
  }
}
