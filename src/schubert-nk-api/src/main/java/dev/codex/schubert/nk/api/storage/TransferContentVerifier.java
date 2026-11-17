package dev.codex.schubert.nk.api.storage;

import dev.codex.schubert.nk.protocol.file.LargeResultContent;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.ReadableByteChannel;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.Objects;

/**
 * Bounded exact-length/hash verification after held-inode attributes; never opens/closes paths.
 * NK-SCN-001; RD FIL-001..009; UI237; SS333 §5..7; PG-D-059; PT-SCN-008-W06.
 */
final class TransferContentVerifier {
  private TransferContentVerifier() {
    throw new AssertionError("static namespace");
  }

  static void verify(ReadableByteChannel channel, LargeResultContent expected)
      throws StorageIoException, NoSuchAlgorithmException {
    Objects.requireNonNull(channel, "channel");
    Objects.requireNonNull(expected, "expected");
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    ByteBuffer buffer = ByteBuffer.allocate(4800);
    try {
      for (int index = 0; index < expected.recordCount(); index++) {
        while (buffer.hasRemaining()) {
          if (channel.read(buffer) <= 0) {
            throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
          }
        }
        buffer.flip();
        digest.update(buffer);
        buffer.clear();
      }
      buffer.limit(1);
      if (channel.read(buffer) != -1) {
        throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
      }
    } catch (IOException failure) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
    if (!MessageDigest.isEqual(digest.digest(), HexFormat.of().parseHex(expected.sha256()))) {
      throw new StorageIoException(StorageIoException.Reason.UNAVAILABLE);
    }
  }
}
