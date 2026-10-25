package dev.codex.schubert.nk.web.media;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.protocol.file.ContentDisposition;
import dev.codex.schubert.nk.protocol.file.MediaDescriptor;
import dev.codex.schubert.nk.protocol.file.MediaType;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Seven approved format literals and actual held files; PT-MED-026, SS333. */
class DescriptorFileResolverTest {
  @TempDir Path root;

  @Test
  void med026ApprovedAssetsUseVerifiedRetainedReadOnlyChannels() throws Exception {
    Files.setPosixFilePermissions(root, PosixFilePermissions.fromString("rwxr-x---"));
    var attrs = Files.readAttributes(root, java.nio.file.attribute.PosixFileAttributes.class);
    var identity = new StorageIdentity(attrs.owner().getName(), attrs.group().getName());
    try (var held = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(), root)) {
      assertThrows(NullPointerException.class, () -> new DescriptorFileResolver(null, identity));
      assertThrows(NullPointerException.class, () -> new DescriptorFileResolver(held, null));
      var resolver = new DescriptorFileResolver(held, identity);
      assertThrows(NullPointerException.class, () -> resolver.read(null, c -> fail("null read")));
      var audio = descriptor(MediaType.AUDIO, "scenario/a.ogg", "audio/ogg");
      assertThrows(NullPointerException.class, () -> resolver.read(audio, null));
      for (String[] format :
          List.of(
              new String[] {"AUDIO", "scenario/a.ogg", "audio/ogg"},
              new String[] {"VIDEO", "video/a.mp4", "video/mp4"},
              new String[] {"MUSIC", "music/a.m4a", "audio/mp4"},
              new String[] {"MUSIC", "music/a.mp3", "audio/mpeg"},
              new String[] {"MUSIC", "music/a.ogg", "audio/ogg"},
              new String[] {"MUSIC", "music/a.wav", "audio/wav"},
              new String[] {"MUSIC", "music/a.flac", "audio/flac"})) {
        Path file = root.resolve(format[1]);
        Files.createDirectories(file.getParent());
        Files.setPosixFilePermissions(
            file.getParent(), PosixFilePermissions.fromString("rwxr-x---"));
        Files.write(file, new byte[] {7, 8, 9});
        Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-r-----"));
        AtomicReference<SeekableByteChannel> channel = new AtomicReference<>();
        resolver.read(
            descriptor(MediaType.valueOf(format[0]), format[1], format[2]),
            c -> {
              channel.set(c);
              ByteBuffer bytes = ByteBuffer.allocate(3);
              assertEquals(3, c.read(bytes));
              assertArrayEquals(new byte[] {7, 8, 9}, bytes.array());
            });
        assertFalse(channel.get().isOpen());
      }
      assertEquals(Boolean.TRUE, held.atDirectory(Files::isDirectory));
      reject(
          () ->
              resolver.read(
                  descriptor(MediaType.AUDIO, "scenario/" + "a".repeat(252) + ".ogg", "audio/ogg"),
                  c -> fail("long segment")));
      reject(
          () ->
              resolver.read(
                  descriptor(MediaType.AUDIO, "scenario/missing.ogg", "audio/ogg"),
                  c -> fail("missing")));
      reject(
          () ->
              resolver.read(
                  audio,
                  c -> {
                    throw new IOException("SYNTHETIC_PRIVATE_PATH");
                  }));
      Path file = root.resolve("scenario/a.ogg");
      Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-------"));
      reject(() -> resolver.read(audio, c -> fail("permissions")));
      Files.setPosixFilePermissions(file, PosixFilePermissions.fromString("rw-r-----"));
      Files.write(file, new byte[] {7});
      reject(() -> resolver.read(audio, c -> fail("size")));
      Files.move(file, root.resolve("saved"));
      Files.createSymbolicLink(file, root.resolve("saved"));
      reject(() -> resolver.read(audio, c -> fail("symlink")));
      assertArrayEquals(new byte[] {7}, Files.readAllBytes(root.resolve("saved")));
      assertTrue(Files.isSymbolicLink(file));
    }
  }

  private static MediaDescriptor descriptor(MediaType type, String path, String mime) {
    return new MediaDescriptor(
        type,
        "7",
        path,
        "name" + path.substring(path.lastIndexOf('.')),
        3,
        "a".repeat(64),
        mime,
        ContentDisposition.INLINE);
  }

  private static void reject(org.junit.jupiter.api.function.Executable action) {
    MediaDeliveryException failure = assertThrows(MediaDeliveryException.class, action);
    assertEquals(MediaDeliveryException.Reason.UNAVAILABLE, failure.reason());
    assertEquals("media delivery failed", failure.getMessage());
    assertEquals(503, failure.httpStatus());
    assertTrue(failure.retryAfterSeconds().isEmpty());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }
}
