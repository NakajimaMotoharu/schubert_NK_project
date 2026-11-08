package dev.codex.schubert.nk.api.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.ReadableByteChannel;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.function.Executable;

/** Independent literal sha256sum lines, never production-generated expected hashes. SS333/343. */
class AssetChecksumManifestTest {
  private static final String MUSIC_TYPE = "MUSIC";
  private static final String MUSIC_PREFIX = "music/";
  private static final String OGG_SUFFIX = ".ogg";
  private static final String MUSIC_A_PATH = "music/a.ogg";
  static final String ABC_SHA = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad";
  static final List<String[]> FORMATS =
      List.of(
          new String[] {"AUDIO", "scenario/音声.ogg", "audio/ogg"},
          new String[] {"VIDEO", "video/動画.mp4", "video/mp4"},
          new String[] {MUSIC_TYPE, "music/曲.m4a", "audio/mp4"},
          new String[] {MUSIC_TYPE, "music/曲.mp3", "audio/mpeg"},
          new String[] {MUSIC_TYPE, "music/曲.ogg", "audio/ogg"},
          new String[] {MUSIC_TYPE, "music/曲.wav", "audio/wav"},
          new String[] {MUSIC_TYPE, "music/曲.flac", "audio/flac"});

  @Test
  void med041LiteralManifestsPreserveApprovedPathsAndHashes() throws Exception {
    StringBuilder lines = new StringBuilder();
    for (String[] format : FORMATS) lines.append(line(format[1]));
    AssetChecksumManifest manifest = parse(lines.toString(), 7);
    assertEquals(7, manifest.entryCount());
    for (String[] format : FORMATS) manifest.requireMatches(descriptor(format));
    String longest = MUSIC_PREFIX + "a".repeat(250) + "/" + "b".repeat(251) + OGG_SUFFIX;
    assertEquals(512, longest.getBytes(StandardCharsets.UTF_8).length);
    var boundary = parse(line(longest), 1);
    boundary.requireMatches(music(longest, ABC_SHA, 3));
    StringBuilder maximum = new StringBuilder();
    for (int i = 0; i < 59_627; i++) maximum.append(line(MUSIC_PREFIX + i + OGG_SUFFIX));
    var inventory = parse(maximum.toString(), 59_627);
    assertEquals(59_627, inventory.entryCount());
    inventory.requireMatches(music("music/0.ogg", ABC_SHA, 3));
    inventory.requireMatches(music("music/59626.ogg", ABC_SHA, 3));
  }

  @Test
  void med042MalformedAndMismatchedCountsNeverPublishPartialCatalog() throws Exception {
    // BUG-042: 69 UTF8 bytes are only 23 Java characters; slicing must never leak runtime errors.
    reject(() -> parse("あ".repeat(23) + "\n", 1));
    assertThrows(NullPointerException.class, () -> AssetChecksumManifest.read(null, 1));
    for (int count : new int[] {-1, 0, 59_628, Integer.MAX_VALUE}) {
      try (var source = new Source(line(MUSIC_A_PATH).getBytes(StandardCharsets.UTF_8), 13)) {
        assertThrows(
            IllegalArgumentException.class, () -> AssetChecksumManifest.read(source, count));
        assertEquals(0, source.reads);
        assertTrue(source.isOpen());
      }
    }
    String good = line(MUSIC_A_PATH);
    for (String invalid :
        List.of(
            "",
            "\n",
            good.stripTrailing(),
            good + "x",
            good + good,
            "\ufeff" + good,
            good.replace("\n", "\r\n"),
            good.replace(ABC_SHA, "A".repeat(64)),
            good.replace(ABC_SHA, "a".repeat(63)),
            good.replace(ABC_SHA, "g".repeat(64)),
            ABC_SHA + "x music/a.ogg\n",
            ABC_SHA + " xmusic/a.ogg\n",
            ABC_SHA + "  \n",
            ABC_SHA + "\t music/a.ogg\n",
            "あ".repeat(33) + "\n")) {
      reject(() -> parse(invalid, 1));
    }
    for (String path :
        List.of(
            "/music/a.ogg",
            "music/../a.ogg",
            "music/./a.ogg",
            "music\\a.ogg",
            "music//a.ogg",
            MUSIC_PREFIX,
            "music/\u0000.ogg",
            "music/e\u0301.ogg",
            MUSIC_PREFIX + "a".repeat(252) + OGG_SUFFIX,
            MUSIC_PREFIX + "a".repeat(250) + "/" + "b".repeat(252) + OGG_SUFFIX)) {
      reject(() -> parse(line(path), 1));
    }
    reject(() -> parse(good, 2));
    reject(() -> parse(good + good, 2));
    reject(() -> parse(good + line("music/b.ogg"), 1));
    byte[] broken = (ABC_SHA + "  music/x.ogg\n").getBytes(StandardCharsets.UTF_8);
    broken[72] = (byte) 0xff;
    try (var source = new Source(broken, 1)) {
      reject(() -> AssetChecksumManifest.read(source, 1));
      assertTrue(source.isOpen());
    }
  }

  @Test
  void med043PartialReadsIoFailuresAndHashMismatchesRemainRedacted() throws Exception {
    byte[] bytes = line(MUSIC_A_PATH).getBytes(StandardCharsets.UTF_8);
    for (int chunk : new int[] {1, 13, 65_536}) {
      try (var source = new Source(bytes, chunk)) {
        var manifest = AssetChecksumManifest.read(source, 1);
        manifest.requireMatches(music(MUSIC_A_PATH, ABC_SHA, 3));
        assertTrue(source.isOpen());
        assertThrows(NullPointerException.class, () -> manifest.requireMatches(null));
        reject(() -> manifest.requireMatches(music("music/missing.ogg", ABC_SHA, 3)));
        for (int i = 0; i < 64; i++) {
          char[] hash = ABC_SHA.toCharArray();
          hash[i] = hash[i] == '0' ? '1' : '0';
          reject(() -> manifest.requireMatches(music(MUSIC_A_PATH, new String(hash), 3)));
        }
      }
    }
    try (var source = new Source(bytes, 0)) {
      reject(() -> AssetChecksumManifest.read(source, 1));
      assertTrue(source.isOpen());
    }
    for (int failAfter : new int[] {0, 3}) {
      try (var source = new Source(bytes, 13)) {
        source.failAfter = failAfter;
        reject(() -> AssetChecksumManifest.read(source, 1));
        assertEquals(failAfter + 1, source.reads);
        assertTrue(source.isOpen());
      }
    }
  }

  @Test
  void med044ConcurrentMatchesOwnImmutableInput() throws Exception {
    byte[] bytes = line(MUSIC_A_PATH).getBytes(StandardCharsets.UTF_8);
    try (var source = new Source(bytes, 13)) {
      var manifest = AssetChecksumManifest.read(source, 1);
      Arrays.fill(bytes, (byte) '!');
      assertEquals("AssetChecksumManifest[entries=1]", manifest.toString());
      var pool = Executors.newFixedThreadPool(10);
      try {
        List<Callable<Boolean>> tasks = new ArrayList<>();
        for (int i = 0; i < 100; i++)
          tasks.add(
              () -> {
                manifest.requireMatches(music(MUSIC_A_PATH, ABC_SHA, 3));
                reject(() -> manifest.requireMatches(music(MUSIC_A_PATH, "0".repeat(64), 3)));
                return manifest.entryCount() == 1;
              });
        for (var future : pool.invokeAll(tasks, 10, TimeUnit.SECONDS)) assertTrue(future.get());
      } finally {
        pool.shutdownNow();
        assertTrue(pool.awaitTermination(10, TimeUnit.SECONDS), "checksum executor terminated");
      }
      assertTrue(source.isOpen());
    }
  }

  static String line(String path) {
    return ABC_SHA + "  " + path + "\n";
  }

  static AssetChecksumManifest parse(String text, int count) throws IOException {
    try (var source = new Source(text.getBytes(StandardCharsets.UTF_8), 65_536)) {
      return AssetChecksumManifest.read(source, count);
    }
  }

  static MediaDescriptor descriptor(String[] format) {
    return new MediaDescriptor(
        MediaType.valueOf(format[0]),
        "7",
        format[1],
        "表示名" + format[1].substring(format[1].lastIndexOf('.')),
        3,
        ABC_SHA,
        format[2],
        ContentDisposition.INLINE);
  }

  static MediaDescriptor music(String path, String hash, long size) {
    return new MediaDescriptor(
        MediaType.MUSIC, "7", path, "name.ogg", size, hash, "audio/ogg", ContentDisposition.INLINE);
  }

  static void reject(Executable action) {
    var failure = assertThrows(MediaIntegrityException.class, action);
    assertEquals("media integrity verification failed", failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  static final class Source implements ReadableByteChannel {
    final byte[] bytes;
    final int chunk;
    int position;
    int reads;
    int failAfter = Integer.MAX_VALUE;
    boolean open = true;

    Source(byte[] bytes, int chunk) {
      this.bytes = bytes;
      this.chunk = chunk;
    }

    @Override
    public int read(ByteBuffer output) throws IOException {
      int readAttempt = reads;
      reads++;
      if (readAttempt == failAfter) throw new IOException("SYNTHETIC_PRIVATE_INPUT");
      if (position == bytes.length) return -1;
      int length = Math.min(Math.min(output.remaining(), chunk), bytes.length - position);
      output.put(bytes, position, length);
      position += length;
      return length;
    }

    @Override
    public boolean isOpen() {
      return open;
    }

    @Override
    public void close() {
      open = false;
    }
  }
}
