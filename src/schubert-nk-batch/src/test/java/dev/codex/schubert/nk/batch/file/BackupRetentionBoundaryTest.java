package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.StorageIoException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.FileTime;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-BAK-2120-001..004; SS341343; WBS-P017-05; synthetic public archives, actual held FD reads. */
final class BackupRetentionBoundaryTest {
  @TempDir Path temporary;

  private static EnvironmentInodePolicy.Metadata inode(
      int mode, long uid, long gid, long device, long number) {
    return new EnvironmentInodePolicy.Metadata(
        mode, uid, gid, 2, 128, device, number, FileTime.fromMillis(0), FileTime.fromMillis(0));
  }

  /** PT-BAK-2736-001: current missed admission predicates264/282/314; real held FD. */
  @Test
  void backup2736001RetentionRejectsNonrootCrossDeviceAndParentDrift() throws Exception {
    for (String bad : List.of("nonroot", "crossDevice", "parentDrift", "lateNonroot")) {
      try (var f = new BackupArtifactFixture(temporary)) {
        var parentReads = new java.util.concurrent.atomic.AtomicInteger();
        if (bad.equals("nonroot")) f.effective = 1;
        f.metadata =
            (role, values) -> {
              if (bad.equals("crossDevice") && role.equals("child"))
                values.put("dev", (Long) values.get("dev") + 1);
              if (role.equals("parent") && parentReads.incrementAndGet() == 2) {
                if (bad.equals("parentDrift")) values.put("ino", (Long) values.get("ino") + 1);
                if (bad.equals("lateNonroot")) f.effective = 1;
              }
            };
        var error =
            assertThrows(
                StorageIoException.class, () -> f.verifier().inspectRetention(f.expected, 100));
        assertEquals(StorageIoException.Reason.UNAVAILABLE, error.reason(), bad);
        assertNull(error.getCause(), bad);
        if (bad.equals("nonroot")) assertEquals(0, f.counts.getOrDefault("openEntry", 0));
        if (bad.equals("parentDrift") || bad.equals("lateNonroot"))
          assertEquals(2, parentReads.get());
        f.unchanged();
        f.released();
      }
    }
  }

  @Test
  void backup2120001FiveIdentityFieldsAndContentOnlyChange() {
    var before = inode(040700, 2000, 2001, 7, 101);
    assertTrue(BackupArtifactVerifier.sameDirectoryInode(before, before));
    var contentOnly =
        new EnvironmentInodePolicy.Metadata(
            040700, 2000, 2001, 9, 8192, 7, 101, FileTime.fromMillis(1), FileTime.fromMillis(2));
    assertTrue(BackupArtifactVerifier.sameDirectoryInode(before, contentOnly));
    for (var changed :
        new EnvironmentInodePolicy.Metadata[] {
          inode(040700, 2000, 2001, 8, 101),
          inode(040700, 2000, 2001, 7, 102),
          inode(040750, 2000, 2001, 7, 101),
          inode(040700, 0, 2001, 7, 101),
          inode(040700, 2000, 0, 7, 101)
        }) assertFalse(BackupArtifactVerifier.sameDirectoryInode(before, changed));
    assertThrows(
        NullPointerException.class, () -> BackupArtifactVerifier.sameDirectoryInode(null, before));
    assertThrows(
        NullPointerException.class, () -> BackupArtifactVerifier.sameDirectoryInode(before, null));
  }

  @Test
  void backup2120002EachArchiveSizeMismatchRetainsWithoutMutation() throws Exception {
    for (String name : BackupArtifactFixture.NAMES) {
      try (var f = new BackupArtifactFixture(temporary)) {
        f.selectedRole = name;
        f.metadata = (role, values) -> values.put("size", (Long) values.get("size") + 1);
        assertTrue(f.verifier().inspectRetention(f.expected, 100).isEmpty(), name);
        f.unchanged();
        f.released();
      }
    }
  }

  @Test
  void backup2120003NonregularAndInvalidRawInodeNeverBecomeDeletionProof() throws Exception {
    for (String name : BackupArtifactFixture.NAMES) {
      try (var f = new BackupArtifactFixture(temporary)) {
        f.selectedRole = name;
        f.metadata = (role, values) -> values.put("mode", 040700);
        assertTrue(f.verifier().inspectRetention(f.expected, 100).isEmpty(), name);
        f.unchanged();
        f.released();
      }
      for (Map.Entry<String, Object> bad :
          List.<Map.Entry<String, Object>>of(
              Map.entry("size", -1L), Map.entry("dev", -1L), Map.entry("ino", 0L))) {
        try (var f = new BackupArtifactFixture(temporary)) {
          f.selectedRole = name;
          f.metadata = (role, values) -> values.put(bad.getKey(), bad.getValue());
          var failure =
              assertThrows(
                  StorageIoException.class, () -> f.verifier().inspectRetention(f.expected, 100));
          assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
          f.unchanged();
          f.released();
        }
      }
    }
  }

  @Test
  void backup2120004EveryDigestMismatchRetainsAndDoesNotRepair() throws Exception {
    for (String name : List.of("schubert_nk.dump", "config.tar", "credentials.tar.age")) {
      try (var f = new BackupArtifactFixture(temporary)) {
        Path artifact = f.child.resolve(name);
        byte[] corrupted = Files.readAllBytes(artifact);
        corrupted[0] ^= 1;
        Files.write(artifact, corrupted);
        Map<String, byte[]> before = f.disk();
        assertTrue(f.verifier().inspectRetention(f.expected, 100).isEmpty(), name);
        var after = f.disk();
        assertEquals(before.keySet(), after.keySet());
        for (String role : before.keySet())
          assertArrayEquals(before.get(role), after.get(role), role);
        f.released();
      }
    }
  }
}
