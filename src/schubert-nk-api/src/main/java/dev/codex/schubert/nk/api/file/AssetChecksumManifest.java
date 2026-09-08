package dev.codex.schubert.nk.api.file;

import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.layout.semantic.RelativePath;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.ReadableByteChannel;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/**
 * Immutable checksum subset of the full migration inventory. NK-MED-001; FIL-006/007/MIG-DAT;
 * UI237/243; SS333/343; PG-D-078; PT-MED-041..044. Does not replace byte/category/pair/ID/order
 * migration checks or hash every asset on GET. No physical path or hash appears in toString().
 */
public final class AssetChecksumManifest {
  static final int MAXIMUM_ENTRIES = 59_627;
  static final int MAXIMUM_LINE_BYTES = 578;
  private final Map<String, String> hashes;

  private AssetChecksumManifest(Map<String, String> hashes) {
    this.hashes = Map.copyOf(hashes);
  }

  /** Caller owns the channel; consumes exactly the LF-terminated manifest without closing it. */
  public static AssetChecksumManifest read(ReadableByteChannel channel, int expectedEntries)
      throws MediaIntegrityException {
    Objects.requireNonNull(channel, "channel");
    requireExpectedCount(expectedEntries);
    ByteBuffer buffer = ByteBuffer.allocate(65_536);
    byte[] line = new byte[MAXIMUM_LINE_BYTES];
    Map<String, String> hashes = new HashMap<>();
    int length = 0;
    try {
      int read;
      while ((read = channel.read(buffer)) != -1) {
        require(read > 0);
        buffer.flip();
        while (buffer.hasRemaining()) {
          byte value = buffer.get();
          if (value == '\n') {
            require(hashes.size() < expectedEntries);
            addLine(hashes, line, length);
            Arrays.fill(line, (byte) 0);
            length = 0;
          } else {
            require(length < line.length);
            line[length++] = value;
          }
        }
        buffer.clear();
      }
      require(length == 0 && hashes.size() == expectedEntries);
      return new AssetChecksumManifest(hashes);
    } catch (IOException | IllegalArgumentException failure) {
      throw new MediaIntegrityException();
    } finally {
      Arrays.fill(buffer.array(), (byte) 0);
      Arrays.fill(line, (byte) 0);
    }
  }

  static void requireExpectedCount(int count) {
    if (count < 1 || count > MAXIMUM_ENTRIES)
      throw new IllegalArgumentException("invalid master manifest count");
  }

  private static void addLine(Map<String, String> hashes, byte[] bytes, int length)
      throws IOException {
    require(length >= 67);
    String line =
        StandardCharsets.UTF_8
            .newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(bytes, 0, length))
            .toString();
    // BUG-042: UTF8 byte width does not establish the decoded String's slicing bounds.
    require(line.length() >= 67);
    String hash = line.substring(0, 64);
    require(hash.matches("[0-9a-f]{64}") && line.charAt(64) == ' ' && line.charAt(65) == ' ');
    String path = line.substring(66);
    require(RelativePath.of(path).wireValue().equals(path));
    require(hashes.putIfAbsent(path, hash) == null);
  }

  /**
   * Require a catalogued path and equal SHA; physical size/type/ownership remain a separate gate.
   */
  public void requireMatches(MediaDescriptor descriptor) throws MediaIntegrityException {
    Objects.requireNonNull(descriptor, "descriptor");
    String expected = hashes.get(descriptor.storageRelativePath());
    if (expected == null) throw new MediaIntegrityException();
    byte[] left = expected.getBytes(StandardCharsets.US_ASCII);
    byte[] right = descriptor.sha256().getBytes(StandardCharsets.US_ASCII);
    try {
      require(MessageDigest.isEqual(left, right));
    } catch (IOException failure) {
      throw new MediaIntegrityException();
    } finally {
      Arrays.fill(left, (byte) 0);
      Arrays.fill(right, (byte) 0);
    }
  }

  public int entryCount() {
    return hashes.size();
  }

  @Override
  public String toString() {
    return "AssetChecksumManifest[entries=" + hashes.size() + "]";
  }

  private static void require(boolean valid) throws MediaIntegrityException {
    if (!valid) throw new MediaIntegrityException();
  }
}
