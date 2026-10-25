package dev.codex.schubert.nk.storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;

/** Independent six-root, all-pair lexical matrix. PT-SCN-008-A05. */
class StorageRootLayoutTest {
  @Test
  void a05AllSixPathsRemainDistinctAndNeverLeakInDisplay() {
    Path[] roots = roots();
    StorageRootLayout layout = layout(roots);
    assertEquals(roots[0], layout.asset());
    assertEquals(roots[1], layout.transfer());
    assertEquals(roots[2], layout.backup());
    assertEquals(roots[3], layout.log());
    assertEquals(roots[4], layout.artemis());
    assertEquals(roots[5], layout.staging());
    assertEquals("StorageRootLayout[REDACTED]", layout.toString());
    roots[0] = Path.of("/synthetic/transfer-other");
    assertEquals(roots[0], layout(roots).asset());
  }

  @Test
  void a05EveryPairRejectsEqualAndBothAncestorDirectionsWithoutStringPrefixConfusion() {
    for (int left = 0; left < 6; left++) {
      for (int right = left + 1; right < 6; right++) {
        Path[] equal = roots();
        equal[right] = equal[left];
        reject(equal);
        Path[] child = roots();
        child[right] = child[left].resolve("child");
        reject(child);
        Path[] parent = roots();
        parent[left] = parent[right].resolve("child");
        reject(parent);
      }
    }
    for (int index = 0; index < 6; index++) {
      Path[] missing = roots();
      missing[index] = null;
      assertThrows(NullPointerException.class, () -> layout(missing));
      for (String invalid :
          List.of("", "relative/root", "/", "/synthetic/./a", "/synthetic/x/../a")) {
        Path[] bad = roots();
        bad[index] = Path.of(invalid);
        reject(bad);
      }
    }
  }

  private static void reject(Path[] paths) {
    IllegalArgumentException failure =
        assertThrows(IllegalArgumentException.class, () -> layout(paths));
    assertFalse(failure.getMessage().contains("synthetic"));
    assertNull(failure.getCause());
  }

  private static Path[] roots() {
    return new Path[] {
      Path.of("/synthetic/asset"), Path.of("/synthetic/transfer"), Path.of("/synthetic/backup"),
      Path.of("/synthetic/log"), Path.of("/synthetic/artemis"), Path.of("/synthetic/staging")
    };
  }

  private static StorageRootLayout layout(Path[] paths) {
    return new StorageRootLayout(paths[0], paths[1], paths[2], paths[3], paths[4], paths[5]);
  }
}
