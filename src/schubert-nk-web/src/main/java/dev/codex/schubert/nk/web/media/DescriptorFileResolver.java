package dev.codex.schubert.nk.web.media;

import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import dev.codex.schubert.nk.storage.ExistingFileAccess;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.util.List;
import java.util.Objects;

/**
 * File adapter for already authenticated/HMAC-verified descriptors, not an authorization gate.
 * NK-MED-001; FIL-006/007; UI237/243; SS311/333; PG-D-075; PT-MED-026. Caller owns admitted root.
 */
public final class DescriptorFileResolver implements MediaRangeService.FileSource {
  private final ExistingFileAccess files;

  public DescriptorFileResolver(OwnedTransferDirectory root, StorageIdentity identity) {
    files = new ExistingFileAccess(root, identity);
  }

  @Override
  public void read(MediaDescriptor descriptor, MediaRangeService.ReadOperation operation)
      throws MediaDeliveryException {
    Objects.requireNonNull(descriptor, "descriptor");
    Objects.requireNonNull(operation, "operation");
    try {
      var path = RelativePath.of(descriptor.storageRelativePath());
      files.read(
          List.of(path.wireValue().split("/", -1)),
          descriptor.byteLength(),
          channel -> {
            operation.execute(channel);
            return Boolean.TRUE;
          });
    } catch (IllegalArgumentException | StorageIoException failure) {
      throw new MediaDeliveryException(MediaDeliveryException.Reason.UNAVAILABLE);
    }
  }
}
