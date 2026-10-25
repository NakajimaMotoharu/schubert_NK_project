package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.attribute.BasicFileAttributes;
import java.nio.file.attribute.PosixFilePermissions;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-OPS-BFENCE-NIO001 / OPS009/UI251/SS343. Own TempDir only; independent atomic new-only
 * collision oracle. Neither a real startup intent nor recovery/retirement authority.
 */
final class BackupStartIntentCollisionTest {
  @TempDir Path temporary;

  @Test
  void bfenceNio001CollisionAfterClearKeepsTheOriginalInodeAndRejectsPublication()
      throws Exception {
    try (var fixture = new BackupPublicationFixture(temporary)) {
      fixture.metadata =
          (role, values) -> {
            values.put("uid", 0);
            values.put("gid", 0);
          };
      Path marker = fixture.parent.resolve("backup-start.intent");
      var gates = new AtomicInteger();
      var original = new AtomicReference<Object>();
      var owner =
          new BackupStartIntentFiles(
              fixture.root,
              fixture,
              fixture,
              () -> {
                if (gates.incrementAndGet() == 2) {
                  // Last successful requireClear gate, before the atomic CREATE_NEW boundary.
                  Files.createFile(
                      marker,
                      PosixFilePermissions.asFileAttribute(
                          PosixFilePermissions.fromString("rw-------")));
                  original.set(Files.readAttributes(marker, BasicFileAttributes.class).fileKey());
                }
              });
      assertThrows(IOException.class, owner::begin);
      assertEquals(2, gates.get());
      assertNotNull(original.get());
      assertArrayEquals(new byte[0], Files.readAllBytes(marker));
      assertEquals(
          original.get(), Files.readAttributes(marker, BasicFileAttributes.class).fileKey());
      assertThrows(IOException.class, owner::requireClear);
      assertEquals(3, gates.get());
      assertEquals(
          original.get(), Files.readAttributes(marker, BasicFileAttributes.class).fileKey());
      assertArrayEquals(new byte[0], Files.readAllBytes(marker));
      fixture.released();
    }
  }
}
