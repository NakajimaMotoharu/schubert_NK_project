package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.file.attribute.FileTime;
import org.junit.jupiter.api.Test;

/** PT-CADDY-2112-001..004; OPS009/UI251/SS342343; literal inode oracle, no native authority. */
final class CaddyPublicMetadataTest {
  private static EnvironmentInodePolicy.Metadata metadata(
      int mode, long uid, long gid, int links, long size, long device, long inode) {
    return new EnvironmentInodePolicy.Metadata(
        mode, uid, gid, links, size, device, inode, FileTime.fromMillis(0), FileTime.fromMillis(0));
  }

  @Test
  void caddy2112001DirectoryOwnerGroupLinksAndEveryAllowedMode() throws Exception {
    for (int mode : new int[] {040700, 040750, 040755}) {
      CaddyPublicConfiguration.requireDirectoryMetadata(metadata(mode, 71, 72, 2, 0, 1, 3), 71, 72);
      CaddyPublicConfiguration.requireDirectoryMetadata(metadata(mode, 71, 72, 9, 0, 1, 3), 71, 72);
    }
    for (var bad :
        new EnvironmentInodePolicy.Metadata[] {
          metadata(040755, 70, 72, 2, 0, 1, 3),
          metadata(040755, 71, 73, 2, 0, 1, 3),
          metadata(040755, 71, 72, 1, 0, 1, 3),
          metadata(040777, 71, 72, 2, 0, 1, 3),
          metadata(0100755, 71, 72, 2, 0, 1, 3)
        }) {
      assertThrows(
          IOException.class, () -> CaddyPublicConfiguration.requireDirectoryMetadata(bad, 71, 72));
    }
    assertThrows(
        NullPointerException.class,
        () -> CaddyPublicConfiguration.requireDirectoryMetadata(null, 71, 72));
  }

  @Test
  void caddy2112002EveryDirectoryIdentityDriftRejectedButContentChangeAllowed() throws Exception {
    var before = metadata(040755, 71, 72, 2, 16, 1, 3);
    CaddyPublicConfiguration.requireStableDirectory(before, before);
    var contentOnly =
        new EnvironmentInodePolicy.Metadata(
            040755, 71, 72, 2, 8192, 1, 3, FileTime.fromMillis(1), FileTime.fromMillis(2));
    CaddyPublicConfiguration.requireStableDirectory(before, contentOnly);
    for (var after :
        new EnvironmentInodePolicy.Metadata[] {
          metadata(040750, 71, 72, 2, 16, 1, 3),
          metadata(040755, 70, 72, 2, 16, 1, 3),
          metadata(040755, 71, 73, 2, 16, 1, 3),
          metadata(040755, 71, 72, 3, 16, 1, 3),
          metadata(040755, 71, 72, 2, 16, 2, 3),
          metadata(040755, 71, 72, 2, 16, 1, 4)
        }) {
      assertThrows(
          IOException.class, () -> CaddyPublicConfiguration.requireStableDirectory(before, after));
    }
    assertThrows(
        NullPointerException.class,
        () -> CaddyPublicConfiguration.requireStableDirectory(null, before));
    assertThrows(
        NullPointerException.class,
        () -> CaddyPublicConfiguration.requireStableDirectory(before, null));
  }

  @Test
  void caddy2112003DeviceAndInodeBounds() throws Exception {
    CaddyPublicConfiguration.requireInodeIdentity(metadata(040755, 0, 0, 2, 0, 0, 1));
    CaddyPublicConfiguration.requireInodeIdentity(
        metadata(040755, 0, 0, 2, 0, Long.MAX_VALUE, Long.MAX_VALUE));
    assertThrows(
        IOException.class,
        () -> CaddyPublicConfiguration.requireInodeIdentity(metadata(040755, 0, 0, 2, 0, -1, 1)));
    assertThrows(
        IOException.class,
        () -> CaddyPublicConfiguration.requireInodeIdentity(metadata(040755, 0, 0, 2, 0, 0, 0)));
    assertThrows(
        IOException.class,
        () -> CaddyPublicConfiguration.requireInodeIdentity(metadata(040755, 0, 0, 2, 0, 0, -1)));
    assertThrows(
        NullPointerException.class, () -> CaddyPublicConfiguration.requireInodeIdentity(null));
  }

  @Test
  void caddy2112004MissingAndNonemptyAclRejectedWithoutMutation() throws Exception {
    CaddyPublicConfiguration.requireNoAccessAcl(new byte[0]);
    assertThrows(IOException.class, () -> CaddyPublicConfiguration.requireNoAccessAcl(null));
    byte[] acl = {1, 2, 3};
    assertThrows(IOException.class, () -> CaddyPublicConfiguration.requireNoAccessAcl(acl));
    assertArrayEquals(new byte[] {1, 2, 3}, acl);
  }
}
