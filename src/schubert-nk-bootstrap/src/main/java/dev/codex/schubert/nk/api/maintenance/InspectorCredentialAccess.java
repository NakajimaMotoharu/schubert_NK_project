package dev.codex.schubert.nk.api.maintenance;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;
import java.util.Objects;
import org.jspecify.annotations.NullMarked;

/**
 * Strict systemd runtime credential access allowlist; performs no I/O and certifies no attribute
 * provenance. NK-DAT-001; DAT-009/OPS-009; UI212/241/251; SS343 6.2; QA-046/SSC-049/PG-D-132;
 * PT-DB-INBOX-113..120. Caller must obtain attributes/ACL/readonly from the same held inode.
 */
@NullMarked
public final class InspectorCredentialAccess {
  private final long serviceUid;
  private final byte[] fileAcl;
  private final byte[] directoryAcl;

  public InspectorCredentialAccess(long serviceUid) {
    require(serviceUid >= 1 && serviceUid <= 0xffff_fffeL);
    this.serviceUid = serviceUid;
    fileAcl = acl(4, serviceUid);
    directoryAcl = acl(5, serviceUid);
  }

  /** Directory capability admission; not an assertion about ancestors or contained files. */
  public void requireDirectory(
      int mode, long ownerUid, int links, boolean readOnlyFilesystem, byte[] accessAcl) {
    requireAccess(mode, ownerUid, readOnlyFilesystem, accessAcl, 040000, 5, directoryAcl);
    require(links >= 1);
  }

  /** Requires a single-linked regular AES credential with the SS343 6.1 encoded size bounds. */
  public void requireAesFile(
      int mode, long ownerUid, int links, long size, boolean readOnlyFilesystem, byte[] accessAcl) {
    requireAccess(mode, ownerUid, readOnlyFilesystem, accessAcl, 0100000, 4, fileAcl);
    require(links == 1 && size >= 54 && size <= 69);
  }

  /** Same runtime access contract, with SS343 6.6 password bounds; PT-DB-INBOX-197..201. */
  public void requireDatabaseFile(
      int mode, long ownerUid, int links, long size, boolean readOnlyFilesystem, byte[] accessAcl) {
    requireAccess(mode, ownerUid, readOnlyFilesystem, accessAcl, 0100000, 4, fileAcl);
    require(links == 1 && size >= 1 && size <= 65536);
  }

  private void requireAccess(
      int mode,
      long ownerUid,
      boolean readOnlyFilesystem,
      byte[] accessAcl,
      int type,
      int permission,
      byte[] expectedAcl) {
    Objects.requireNonNull(accessAcl, "access ACL");
    if (ownerUid == 0) {
      require(
          mode == (type | (permission << 6) | (permission << 3))
              && Arrays.equals(expectedAcl, accessAcl));
    } else {
      require(
          ownerUid == serviceUid
              && mode == (type | (permission << 6))
              && readOnlyFilesystem
              && accessAcl.length == 0);
    }
  }

  // Linux UAPI version2, LE tag:u16/perm:u16/id:u32; only the five systemd entries.
  private static byte[] acl(int permission, long uid) {
    ByteBuffer buffer = ByteBuffer.allocate(44).order(ByteOrder.LITTLE_ENDIAN);
    buffer.putInt(2);
    entry(buffer, 1, permission, -1);
    entry(buffer, 2, permission, (int) uid);
    entry(buffer, 4, 0, -1);
    entry(buffer, 16, permission, -1);
    entry(buffer, 32, 0, -1);
    return buffer.array();
  }

  private static void entry(ByteBuffer buffer, int tag, int permission, int id) {
    buffer.putShort((short) tag).putShort((short) permission).putInt(id);
  }

  private static void require(boolean accepted) {
    if (!accepted) throw new IllegalArgumentException("inspector credential access is invalid");
  }
}
