package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.file.attribute.FileTime;
import org.junit.jupiter.api.Test;

/** PT-BAK-2122-001..004; BAK/BKO/UI251/SS341343; literal metadata, never native admission. */
final class MorningBackupMetadataTest {
  private static EnvironmentInodePolicy.Metadata value(
      int mode, long uid, long gid, int links, long size) {
    return new EnvironmentInodePolicy.Metadata(
        mode, uid, gid, links, size, 7, 101, FileTime.fromMillis(0), FileTime.fromMillis(0));
  }

  @Test
  void backup2122001DirectoriesRetainExactRoleAndAllowZeroSize() throws Exception {
    MorningBackupArtifacts.requireDirectoryMetadata(value(040700, 0, 0, 2, 0), 0, 040700, 0);
    MorningBackupArtifacts.requireDirectoryMetadata(
        value(040750, 2000, 2001, 9, Long.MAX_VALUE), 2001, 040750, 2000);
    for (var invalid :
        new EnvironmentInodePolicy.Metadata[] {
          value(040755, 0, 0, 2, 0),
          value(040700, 1, 0, 2, 0),
          value(040700, 0, 1, 2, 0),
          value(040700, 0, 0, 1, 0),
          value(040700, 0, 0, 2, -1)
        })
      assertThrows(
          IOException.class,
          () -> MorningBackupArtifacts.requireDirectoryMetadata(invalid, 0, 040700, 0));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupArtifacts.requireDirectoryMetadata(null, 0, 040700, 0));
  }

  @Test
  void backup2122002FileZeroAndMaximumAcceptedOnlyForExactRootRole() throws Exception {
    for (long size : new long[] {0, 1, 4096})
      MorningBackupArtifacts.requireFileMetadata(
          value(0100640, 0, 2001, 1, size), 2001, 0100640, 4096);
    for (var invalid :
        new EnvironmentInodePolicy.Metadata[] {
          value(0100600, 0, 2001, 1, 1),
          value(0100640, 1, 2001, 1, 1),
          value(0100640, 0, 2002, 1, 1),
          value(0100640, 0, 2001, 2, 1),
          value(0100640, 0, 2001, 1, -1),
          value(0100640, 0, 2001, 1, 4097)
        })
      assertThrows(
          IOException.class,
          () -> MorningBackupArtifacts.requireFileMetadata(invalid, 2001, 0100640, 4096));
    assertThrows(
        NullPointerException.class,
        () -> MorningBackupArtifacts.requireFileMetadata(null, 2001, 0100640, 4096));
  }

  @Test
  void backup2122003ToolsHaveTwoModesRootOwnerOneLinkAndPositiveBoundedSize() throws Exception {
    for (int mode : new int[] {0100644, 0100755})
      for (long size : new long[] {1, 268435456})
        MorningBackupArtifacts.requireToolMetadata(value(mode, 0, 0, 1, size));
    for (var invalid :
        new EnvironmentInodePolicy.Metadata[] {
          value(0100640, 0, 0, 1, 1),
          value(0100644, 1, 0, 1, 1),
          value(0100644, 0, 1, 1, 1),
          value(0100644, 0, 0, 2, 1),
          value(0100644, 0, 0, 1, 0),
          value(0100644, 0, 0, 1, -1),
          value(0100644, 0, 0, 1, 268435457)
        })
      assertThrows(IOException.class, () -> MorningBackupArtifacts.requireToolMetadata(invalid));
    assertThrows(
        NullPointerException.class, () -> MorningBackupArtifacts.requireToolMetadata(null));
  }

  @Test
  void backup2122004AclIsPresentEmptyAndNeverRepaired() throws Exception {
    MorningBackupArtifacts.requireNoAccessAcl(new byte[0]);
    assertThrows(IOException.class, () -> MorningBackupArtifacts.requireNoAccessAcl(null));
    byte[] acl = {1, 2, 3};
    assertThrows(IOException.class, () -> MorningBackupArtifacts.requireNoAccessAcl(acl));
    assertArrayEquals(new byte[] {1, 2, 3}, acl);
  }
}
