package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.DIR;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.GID;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.MANIFEST_HASH;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.NAMES;
import static dev.codex.schubert.nk.batch.file.BackupArtifactFixture.UID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.storage.DirectoryCalls;
import dev.codex.schubert.nk.storage.LinuxDirectoryCalls;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import dev.codex.schubert.nk.storage.StorageIoException;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.jspecify.annotations.Nullable;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PT-BAK-4950-001..006; BAK/BKO/OPS009/UI251/SS341§6.3/343/SSC133; WBS-P017-05. Existing synthetic
 * policy ports, public synthetic archives and actual held Linux FDs only. No runtime
 * ownership/DB/Backup permission is created by these tests.
 */
final class BackupRetentionRejectionTest {
  private static final String FIXTURE_EFFECTIVEUID_EF410629 = "effectiveUid";
  @TempDir Path temporary;

  private static BackupManifestReader reader(BackupArtifactFixture fixture) {
    return new BackupManifestReader(fixture.root, fixture, UID, GID, fixture, fixture::clock);
  }

  private static void unavailable(org.junit.jupiter.api.function.Executable action) {
    var failure = assertThrows(StorageIoException.class, action);
    assertEquals(StorageIoException.Reason.UNAVAILABLE, failure.reason());
    assertNull(failure.getCause());
  }

  @Test
  void backup4950001NonrootNamesCannotReadOrMutateTheBorrowedRoot() throws Exception {
    try (var fixture = new BackupArtifactFixture(temporary)) {
      fixture.effective = 1000;
      unavailable(() -> reader(fixture).retentionNames(100));
      assertEquals(1, fixture.counts.get(FIXTURE_EFFECTIVEUID_EF410629));
      assertEquals(0, fixture.counts.getOrDefault("openNames", 0));
      assertEquals(0, fixture.counts.getOrDefault("attributes", 0));
      fixture.unchanged();
      fixture.released();
    }
  }

  @Test
  void backup4950002LateOwnerChangeRefusesTheOtherwiseStableNames() throws Exception {
    try (var fixture = new BackupArtifactFixture(temporary)) {
      fixture.hook =
          (name, count) -> {
            if (name.equals(FIXTURE_EFFECTIVEUID_EF410629) && count == 2) fixture.effective = 1000;
          };
      unavailable(() -> reader(fixture).retentionNames(100));
      assertEquals(2, fixture.counts.get(FIXTURE_EFFECTIVEUID_EF410629));
      assertEquals(1, fixture.counts.get("openNames"));
      assertEquals(1, fixture.counts.get("closeNames"));
      fixture.unchanged();
      fixture.released();
    }
  }

  @Test
  void backup4950003NonrootRetentionMetadataIsNeverADeletionProof() throws Exception {
    try (var fixture = new BackupArtifactFixture(temporary)) {
      fixture.effective = 1000;
      unavailable(() -> reader(fixture).retentionRoot(100));
      assertEquals(1, fixture.counts.get(FIXTURE_EFFECTIVEUID_EF410629));
      assertEquals(0, fixture.counts.getOrDefault("attributes", 0));
      fixture.unchanged();
      fixture.released();
    }
  }

  @Test
  void backup4950004NonrootChildClassificationCannotAcquireAnEntry() throws Exception {
    try (var fixture = new BackupArtifactFixture(temporary)) {
      fixture.effective = 1000;
      unavailable(() -> reader(fixture).retentionDirectory(DIR, 100));
      assertEquals(1, fixture.counts.get(FIXTURE_EFFECTIVEUID_EF410629));
      assertEquals(0, fixture.counts.getOrDefault("openEntry", 0));
      fixture.unchanged();
      fixture.released();
    }
  }

  @Test
  void backup4950005MissingPostDeleteStreamRetainsTheDirectoryAndReturnsAllHandles()
      throws Exception {
    postDeleteRefusal(false);
  }

  @Test
  void backup4950006ConcurrentUnknownMemberIsPreservedWithoutRecursiveDelete() throws Exception {
    postDeleteRefusal(true);
  }

  private void postDeleteRefusal(boolean introduceForeignMember) throws Exception {
    try (var fixture = new BackupArtifactFixture(temporary)) {
      var removed = new ArrayList<String>();
      var directoryRemovals = new AtomicInteger();
      var postDeleteCalls = new AtomicInteger();
      var ownerDeadlineChecks = new AtomicInteger();
      var nativeCalls = LinuxDirectoryCalls.create();
      var calls =
          (DirectoryCalls)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {DirectoryCalls.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("removeEmptyDirectory"))
                      directoryRemovals.incrementAndGet();
                    Object result;
                    try {
                      result = method.invoke(nativeCalls, args);
                    } catch (InvocationTargetException failure) {
                      throw failure.getCause();
                    }
                    if (method.getName().equals("unlink")) removed.add((String) args[1]);
                    return result;
                  });
      var io =
          new BackupArtifactVerifier.Io() {
            @Override
            public @Nullable Map<String, Object> attributes(Path held) throws IOException {
              return fixture.attributes(held);
            }

            @Override
            public @Nullable SeekableByteChannel open(Path held) throws IOException {
              return fixture.open(held);
            }

            @Override
            public @Nullable DirectoryStream<Path> openNames(Path held) throws IOException {
              if (removed.size() == 4) {
                assertEquals(1, postDeleteCalls.incrementAndGet());
                if (!introduceForeignMember) return null;
                // Explicit IO-boundary race in this test's private temporary child only.
                Files.writeString(fixture.child.resolve("public-foreign-member"), "keep-public\n");
              }
              return fixture.openNames(held);
            }
          };
      try (var root = OwnedTransferDirectory.open(calls, fixture.parent)) {
        var verifier = new BackupArtifactVerifier(root, fixture, UID, GID, io, fixture::clock);
        var admitted = verifier.verifyWithin(fixture.expected, 100);
        assertEquals(MANIFEST_HASH, admitted.manifest().sha256());
        unavailable(
            () ->
                verifier.removeRetained(
                    fixture.expected,
                    admitted,
                    100,
                    () -> {
                      ownerDeadlineChecks.incrementAndGet();
                      return 1_000_000L;
                    }));
        assertEquals(
            List.of("schubert_nk.dump", "config.tar", "credentials.tar.age", "MANIFEST.json"),
            removed);
        assertEquals(1, postDeleteCalls.get());
        // One initial check, two per fixed member, one before the post-delete observation.
        assertEquals(10, ownerDeadlineChecks.get());
        assertEquals(0, directoryRemovals.get());
        assertTrue(Files.isDirectory(fixture.child, LinkOption.NOFOLLOW_LINKS));
        for (String name : NAMES)
          assertFalse(Files.exists(fixture.child.resolve(name), LinkOption.NOFOLLOW_LINKS));
        try (var remaining = Files.list(fixture.child)) {
          assertEquals(
              introduceForeignMember ? List.of("public-foreign-member") : List.of(),
              remaining.map(path -> path.getFileName().toString()).sorted().toList());
        }
        if (introduceForeignMember)
          assertEquals(
              "keep-public\n", Files.readString(fixture.child.resolve("public-foreign-member")));
        fixture.released();
      }
    }
  }
}
