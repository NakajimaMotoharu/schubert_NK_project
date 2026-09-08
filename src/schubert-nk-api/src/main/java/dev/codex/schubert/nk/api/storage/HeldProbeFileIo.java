package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;

/**
 * Opaque public diagnostic bytes, not a business result/descriptor. NK-SCN-001; RD FIL-001..009;
 * UI237/243; SS333 §7.4; SSC-022; PG-D-064; PT-SCN-008-P01/P03.
 */
final class HeldProbeFileIo implements ProbeFileIo {
  private final HeldTransferFileIo files;

  HeldProbeFileIo(StorageIdentity identity) {
    files = new HeldTransferFileIo(identity);
  }

  @Override
  public void initializeDirectory(Path handle) throws IOException {
    files.initializeDirectory(handle);
  }

  @Override
  public void write(Path handle, boolean second) throws IOException, NoSuchAlgorithmException {
    files.initializePart(handle);
    byte[] bytes = new byte[4800];
    Arrays.fill(bytes, (byte) (second ? 0x4e : 0x53));
    try (var channel = FileChannel.open(handle, StandardOpenOption.WRITE)) {
      // The stream adapter writes all bytes or throws; channel is the sole owned close boundary.
      Channels.newOutputStream(channel).write(bytes);
      channel.force(true);
    }
    verify(handle, second);
  }

  @Override
  public void verify(Path handle, boolean second) throws IOException, NoSuchAlgorithmException {
    files.verify(
        handle,
        new LargeResultContent(
            1,
            4800,
            second
                ? "fb6cbe5cba6ebae945fa9c8022f0ff813834b15fc981ec030f4fc2b8310a9ff7"
                : "311a3b1660bc9cec85deb46945fbcc8403c6f892edaa60ec9c030d5d477542d5"));
  }
}
