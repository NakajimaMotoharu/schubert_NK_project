package dev.codex.schubert.nk.web.storage;

import dev.codex.schubert.nk.protocol.file.LargeResultDescriptor;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.PosixFilePermissions;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;
import java.util.Locale;
import java.util.UUID;

/** Literal UI234 offsets, independent byte/hash oracle; never calls production encode. */
final class ScenarioFileFixture {
  static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000071");

  private ScenarioFileFixture() {}

  static LargeResultDescriptor write(Path file, int count) throws Exception {
    MessageDigest digest = MessageDigest.getInstance("SHA-256");
    try (var channel =
        FileChannel.open(file, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
      for (int sequence = 1; sequence <= count; sequence++) {
        byte[] record = golden(sequence);
        digest.update(record);
        ByteBuffer buffer = ByteBuffer.wrap(record);
        while (buffer.hasRemaining()) channel.write(buffer);
      }
    }
    Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-r-----"));
    return descriptor(count, HexFormat.of().formatHex(digest.digest()));
  }

  static LargeResultDescriptor descriptor(int count, String hash) {
    return new LargeResultDescriptor(ID, "20260908/" + ID + ".ready", 4800L * count, hash, count);
  }

  static String hash(byte[] bytes) throws Exception {
    return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
  }

  static byte[] golden(int sequence) {
    byte[] bytes = new byte[4800];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 0, String.format(Locale.ROOT, "%012d", 50001 - sequence));
    put(bytes, 12, String.format(Locale.ROOT, "%06d", sequence));
    put(bytes, 18, "00000042");
    put(bytes, 26, "narration");
    put(bytes, 164, "本文");
    put(bytes, 4260, "000");
    return bytes;
  }

  static void put(byte[] target, int offset, String value) {
    byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }
}
