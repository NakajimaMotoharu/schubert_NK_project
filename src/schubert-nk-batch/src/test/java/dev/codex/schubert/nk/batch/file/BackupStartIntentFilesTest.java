package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.RepeatedTest;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-OPS-BFENCE001-006; public marker bytes only, synthetic root metadata. */
final class BackupStartIntentFilesTest {
  private static final String FIXTURE_BACKUP_START_INTENT_4FC63345 = "backup-start.intent";
  @TempDir Path temporary;

  private BackupPublicationFixture fixture() throws Exception {
    var fixture = new BackupPublicationFixture(temporary);
    fixture.metadata =
        (role, values) -> {
          values.put("uid", 0);
          values.put("gid", 0);
        };
    return fixture;
  }

  private static BackupStartIntentFiles files(BackupPublicationFixture fixture) {
    return new BackupStartIntentFiles(fixture.root, fixture, fixture, () -> {});
  }

  @Test
  void isspub007PublicationRecoveryNeverRetiresAnOldQuarantine() throws Exception {
    try (var fixture = fixture()) {
      var files =
          new BackupStartIntentFiles(
              fixture.root, fixture, fixture, () -> {}, "permit-start.intent");
      var token = files.begin();
      Path marker = fixture.parent.resolve("permit-start.intent");
      files.requirePresent(token);
      assertThrows(
          IOException.class,
          () ->
              new BackupStartIntentFiles(
                      fixture.root, fixture, fixture, () -> {}, "permit-start.intent")
                  .requirePresent(token));
      assertThrows(NullPointerException.class, () -> files.requirePresent(null));
      long inode = (Long) Files.getAttribute(marker, "unix:ino");
      files.quarantinePublication();
      assertEquals(inode, Files.getAttribute(marker, "unix:ino"));
      files.retire(token);
      assertThrows(IOException.class, () -> files.requirePresent(token));
      files.quarantinePublication();
      assertArrayEquals(new byte[0], Files.readAllBytes(marker));
      assertThrows(IOException.class, files::requireClear);
      assertThrows(IOException.class, () -> files.retire(token));
      Files.writeString(marker, "corrupt");
      assertThrows(IOException.class, files::quarantinePublication);
      assertEquals("corrupt", Files.readString(marker));
      assertThrows(
          IOException.class,
          () -> BackupStartIntentFilesTest.files(fixture).quarantinePublication());
      fixture.released();
    }
  }

  @Test
  void newOnlyMarkerSurvivesOwnerCloseAndRetiresOnlyWithSameToken() throws Exception {
    try (var fixture = fixture()) {
      var first = files(fixture);
      first.requireClear();
      var token = first.begin();
      first.requirePresent(token);
      Path marker = fixture.parent.resolve(FIXTURE_BACKUP_START_INTENT_4FC63345);
      assertTrue(Files.isRegularFile(marker));
      assertArrayEquals(new byte[0], Files.readAllBytes(marker));
      assertThrows(IOException.class, first::requireClear);
      assertThrows(IOException.class, first::begin);
      var restarted = files(fixture);
      assertThrows(IOException.class, restarted::requireClear);
      assertThrows(IOException.class, () -> restarted.retire(token));
      assertTrue(Files.exists(marker));
      first.retire(token);
      first.requireClear();
      assertFalse(Files.exists(marker));
      fixture.released();
    }
  }

  @Test
  void uncertainDurabilityPreservesMarkerAndNextAdmissionRefuses() throws Exception {
    try (var fixture = fixture()) {
      fixture.faults.put("sync#1", new IOException("test-only"));
      var owner = files(fixture);
      assertThrows(IOException.class, owner::begin);
      assertTrue(Files.exists(fixture.parent.resolve(FIXTURE_BACKUP_START_INTENT_4FC63345)));
      fixture.faults.clear();
      assertThrows(IOException.class, files(fixture)::requireClear);
      fixture.released();
    }
  }

  @Test
  void existingOrCorruptMarkerIsNeverRepaired() throws Exception {
    for (String content : List.of("", "unexpected")) {
      try (var fixture = fixture()) {
        Path marker = fixture.parent.resolve(FIXTURE_BACKUP_START_INTENT_4FC63345);
        Files.writeString(marker, content);
        assertThrows(IOException.class, files(fixture)::requireClear);
        assertEquals(content, Files.readString(marker));
        fixture.released();
      }
    }
  }

  @Test
  void unsafeRootOrInterruptedActorCannotCreateIntent() throws Exception {
    for (String fault :
        List.of("uid", "acl", "readonly", "filesystem", "metadata", "gate", "interrupt")) {
      try (var fixture = fixture()) {
        BackupStartIntentFiles owner = files(fixture);
        switch (fault) {
          case "uid" -> fixture.effective = 1;
          case "acl" -> fixture.acl = new byte[] {1};
          case "readonly" -> fixture.readonly = true;
          case "filesystem" -> fixture.copyFilesystem = "ext4";
          case "metadata" -> fixture.nullMap = true;
          case "gate" ->
              owner =
                  new BackupStartIntentFiles(
                      fixture.root,
                      fixture,
                      fixture,
                      () -> {
                        throw new IOException("test-only");
                      });
          default -> Thread.currentThread().interrupt();
        }
        try {
          BackupStartIntentFiles selected = owner;
          assertThrows(IOException.class, selected::begin);
          assertFalse(Files.exists(fixture.parent.resolve(FIXTURE_BACKUP_START_INTENT_4FC63345)));
        } finally {
          Thread.interrupted();
        }
        fixture.released();
      }
    }
  }

  @RepeatedTest(10)
  void concurrentDistinctOwnersCannotPublishTwoIntents() throws Exception {
    try (var fixture = fixture();
        var executor = Executors.newFixedThreadPool(2)) {
      var start = new CountDownLatch(1);
      Callable<Boolean> race =
          () -> {
            start.await();
            try {
              files(fixture).begin();
              return true;
            } catch (IOException blocked) {
              return false;
            }
          };
      var left = executor.submit(race);
      var right = executor.submit(race);
      start.countDown();
      assertEquals(1, (left.get() ? 1 : 0) + (right.get() ? 1 : 0));
      assertTrue(Files.exists(fixture.parent.resolve(FIXTURE_BACKUP_START_INTENT_4FC63345)));
      assertThrows(IOException.class, files(fixture)::requireClear);
      fixture.released();
    }
  }

  @Test
  void nullContractsAreExplicit() throws Exception {
    try (var fixture = fixture()) {
      assertThrows(
          NullPointerException.class,
          () -> new BackupStartIntentFiles(null, fixture, fixture, () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new BackupStartIntentFiles(fixture.root, null, fixture, () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new BackupStartIntentFiles(fixture.root, fixture, null, () -> {}));
      assertThrows(
          NullPointerException.class,
          () -> new BackupStartIntentFiles(fixture.root, fixture, fixture, null));
      assertThrows(NullPointerException.class, () -> files(fixture).retire(null));
      assertThrows(NullPointerException.class, () -> BackupStartIntentFiles.create(null, null));
      fixture.released();
    }
  }
}
