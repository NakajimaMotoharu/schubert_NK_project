package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.storage.ExistingFileAccess;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.util.List;
import java.util.Objects;

/**
 * API manifest then physical metadata verification; not per-GET full content hashing or auth.
 * NK-MED-001; FIL-006/007; UI237/243; SS312/333/343; PG-D-078; PT-MED-047..049.
 */
public final class HeldMediaFileInspector implements MediaFileInspector {
  private final AssetChecksumManifest manifest;
  private final ExistingFileAccess files;

  public HeldMediaFileInspector(
      OwnedTransferDirectory root, StorageIdentity identity, AssetChecksumManifest manifest) {
    this.manifest = Objects.requireNonNull(manifest, "manifest");
    files = new ExistingFileAccess(root, identity);
  }

  @Override
  public void verify(MediaDescriptor descriptor) throws MediaIntegrityException {
    Objects.requireNonNull(descriptor, "descriptor");
    manifest.requireMatches(descriptor);
    try {
      files.read(
          List.of(RelativePath.of(descriptor.storageRelativePath()).wireValue().split("/", -1)),
          descriptor.byteLength(),
          channel -> Boolean.TRUE);
    } catch (IllegalArgumentException | StorageIoException failure) {
      throw new MediaIntegrityException();
    }
  }
}
