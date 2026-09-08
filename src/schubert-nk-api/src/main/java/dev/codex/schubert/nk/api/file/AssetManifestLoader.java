package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageAttributeGuard;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Map;
import java.util.Objects;

/**
 * Existing, retained startup manifest only; caller owns an admitted root. NK-MED-001; FIL-006/007;
 * UI243; SS333/343; PG-D-078; PT-MED-045/046. No mkdir/repair/DB/JMS or asset content in Git.
 */
public final class AssetManifestLoader {
  interface Io {
    Map<String, Object> attributes(Path held) throws IOException;

    SeekableByteChannel openReadOnly(Path held) throws IOException;
  }

  private final OwnedTransferDirectory root;
  private final StorageIdentity identity;
  private final Io io;

  public AssetManifestLoader(OwnedTransferDirectory root, StorageIdentity identity) {
    this(root, identity, new NioIo());
  }

  AssetManifestLoader(OwnedTransferDirectory root, StorageIdentity identity, Io io) {
    this.root = Objects.requireNonNull(root, "root");
    this.identity = Objects.requireNonNull(identity, "identity");
    this.io = Objects.requireNonNull(io, "io");
  }

  public AssetChecksumManifest load(int expectedEntries) throws MediaIntegrityException {
    AssetChecksumManifest.requireExpectedCount(expectedEntries);
    try {
      directory(root);
      try (var manifests = root.openExistingChild("manifests")) {
        directory(manifests);
        return manifests.atExistingEntryHandle(
            "master.sha256",
            path -> {
              Map<String, Object> attributes = io.attributes(path);
              long size = size(attributes);
              StorageAttributeGuard.existingFile(attributes, identity, size);
              try (var channel = io.openReadOnly(path)) {
                sameSize(channel, size);
                var result = AssetChecksumManifest.read(channel, expectedEntries);
                sameSize(channel, size);
                StorageAttributeGuard.existingFile(io.attributes(path), identity, size);
                return result;
              }
            });
      }
    } catch (IOException | UnsupportedOperationException failure) {
      throw new MediaIntegrityException();
    }
  }

  private void directory(OwnedTransferDirectory directory) throws IOException {
    directory.atDirectory(
        path -> {
          StorageAttributeGuard.directory(io.attributes(path), identity);
          return Boolean.TRUE;
        });
  }

  private static long size(Map<String, Object> attributes) throws MediaIntegrityException {
    Object value = attributes.get("size");
    if (!(value instanceof Long size)
        || size < 1
        || size
            > (AssetChecksumManifest.MAXIMUM_LINE_BYTES + 1L)
                * AssetChecksumManifest.MAXIMUM_ENTRIES) {
      throw new MediaIntegrityException();
    }
    return size;
  }

  private static void sameSize(SeekableByteChannel channel, long expected) throws IOException {
    if (channel.size() != expected) throw new MediaIntegrityException();
  }

  private static final class NioIo implements Io {
    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      return Files.readAttributes(held, "unix:owner,group,mode,nlink,size");
    }

    @Override
    public SeekableByteChannel openReadOnly(Path held) throws IOException {
      return FileChannel.open(held, StandardOpenOption.READ);
    }
  }
}
