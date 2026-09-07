package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.NoSuchAlgorithmException;
import java.util.Objects;

/**
 * Fresh file/directory initialization and verified streams on held FDs. NK-SCN-001; RD
 * FIL-001..009; UI237/243; SS333/342/343; SSC-020; PT-SCN-008-W07/W09.
 */
final class HeldTransferFileIo implements TransferFileIo {
  private final StorageIdentity identity;

  HeldTransferFileIo(StorageIdentity identity) {
    this.identity = Objects.requireNonNull(identity, "identity");
  }

  @Override
  public void initializeDirectory(Path handle) throws IOException {
    initialize(handle, "rwxr-x---");
  }

  @Override
  public LargeResultContent writePart(Path handle, ScenarioRecordStream prepared)
      throws IOException, NoSuchAlgorithmException {
    Objects.requireNonNull(prepared, "prepared");
    initializePart(handle);
    LargeResultContent content;
    try (var channel = FileChannel.open(handle, StandardOpenOption.WRITE)) {
      content = prepared.write(channel);
    }
    verify(handle, content);
    return content;
  }

  @Override
  public void verify(Path handle, LargeResultContent content)
      throws IOException, NoSuchAlgorithmException {
    Objects.requireNonNull(handle, "handle");
    Objects.requireNonNull(content, "content");
    StorageAttributeGuard.file(
        Files.readAttributes(handle, "unix:owner,group,mode,nlink,size"),
        identity,
        content.byteLength());
    try (var channel = FileChannel.open(handle, StandardOpenOption.READ)) {
      TransferContentVerifier.verify(channel, content);
    }
  }

  /** Only the fresh inode returned by CREATE_NEW may be initialized. SSC-020/022. */
  void initializePart(Path handle) throws IOException {
    initialize(handle, "rw-r-----");
  }

  private void initialize(Path handle, String permissions) throws IOException {
    Objects.requireNonNull(handle, "handle");
    var group =
        handle
            .getFileSystem()
            .getUserPrincipalLookupService()
            .lookupPrincipalByGroupName(identity.group());
    Files.setAttribute(handle, "posix:group", group);
    Files.setPosixFilePermissions(handle, PosixFilePermissions.fromString(permissions));
  }
}
