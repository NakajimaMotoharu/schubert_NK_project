package dev.codex.schubert.nk.api.file;

import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.ABC_SHA;
import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.FORMATS;
import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.descriptor;
import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.music;
import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.reject;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** API metadata admission without DB/JMS or per-GET full hashing. SS333; PT-MED-047..049. */
class HeldMediaFileInspectorTest {
  @TempDir Path directory;

  @Test
  void med047ApprovedFilesRequireManifestAndExactPhysicalSize() throws Exception {
    try (var f = new MediaAssetFixture(directory.resolve("normal"))) {
      var manifest = new AssetManifestLoader(f.held, f.identity).load(7);
      var inspector = new HeldMediaFileInspector(f.held, f.identity, manifest);
      for (String[] format : FORMATS) {
        inspector.verify(descriptor(format));
        assertEquals("abc", Files.readString(f.root.resolve(format[1])));
        assertEquals(0100640, Files.getAttribute(f.root.resolve(format[1]), "unix:mode"));
      }
      f.assertRootOwned();
    }
  }

  @Test
  void med048MissingHashPathsAndPhysicalFaultsNeverBecomeNotFound() throws Exception {
    try (var f = new MediaAssetFixture(directory.resolve("faults"))) {
      var manifest = new AssetManifestLoader(f.held, f.identity).load(7);
      assertThrows(
          NullPointerException.class, () -> new HeldMediaFileInspector(null, f.identity, manifest));
      assertThrows(
          NullPointerException.class, () -> new HeldMediaFileInspector(f.held, null, manifest));
      assertThrows(
          NullPointerException.class, () -> new HeldMediaFileInspector(f.held, f.identity, null));
      var inspector = new HeldMediaFileInspector(f.held, f.identity, manifest);
      int beforeDirectories = f.calls.directoryOpens;
      int beforeEntries = f.calls.entryOpens;
      assertThrows(NullPointerException.class, () -> inspector.verify(null));
      reject(() -> inspector.verify(music("music/missing.ogg", ABC_SHA, 3)));
      for (int i = 0; i < 64; i++) {
        char[] hash = ABC_SHA.toCharArray();
        hash[i] = hash[i] == '0' ? '1' : '0';
        reject(() -> inspector.verify(music("music/曲.ogg", new String(hash), 3)));
      }
      assertEquals(beforeDirectories, f.calls.directoryOpens);
      assertEquals(beforeEntries, f.calls.entryOpens);
      reject(() -> inspector.verify(music("music/曲.ogg", ABC_SHA, 2)));
      Path path = f.root.resolve("music/曲.ogg");
      MediaAssetFixture.mode(path, "rw-------");
      reject(() -> inspector.verify(music("music/曲.ogg", ABC_SHA, 3)));
      assertEquals(0100600, Files.getAttribute(path, "unix:mode"));
      MediaAssetFixture.mode(path, "rw-r-----");
      Path saved = f.root.resolve("saved.ogg");
      Files.move(path, saved);
      reject(() -> inspector.verify(music("music/曲.ogg", ABC_SHA, 3)));
      Files.createSymbolicLink(path, saved);
      reject(() -> inspector.verify(music("music/曲.ogg", ABC_SHA, 3)));
      Files.delete(path); // Only the test-created link, not its target.
      Files.createLink(path, saved);
      reject(() -> inspector.verify(music("music/曲.ogg", ABC_SHA, 3)));
      assertEquals("abc", Files.readString(saved));
      assertEquals(2, Files.getAttribute(saved, "unix:nlink"));
      f.assertRootOwned();
    }
    var closed = new MediaAssetFixture(directory.resolve("closed"));
    var manifest = new AssetManifestLoader(closed.held, closed.identity).load(7);
    var inspector = new HeldMediaFileInspector(closed.held, closed.identity, manifest);
    closed.close();
    reject(() -> inspector.verify(descriptor(FORMATS.getFirst())));
  }

  @Test
  void med049ConcurrentInspectionsRetainRootOwnership() throws Exception {
    try (var f = new MediaAssetFixture(directory.resolve("parallel"))) {
      var manifest = new AssetManifestLoader(f.held, f.identity).load(7);
      var inspector = new HeldMediaFileInspector(f.held, f.identity, manifest);
      Path moved = directory.resolve("retained");
      Files.move(f.root, moved);
      Files.createDirectory(f.root);
      Files.writeString(f.root.resolve("marker"), "replacement must not be used");
      try (var pool = Executors.newFixedThreadPool(10)) {
        List<Callable<Boolean>> tasks = new ArrayList<>();
        for (int i = 0; i < 100; i++) {
          String[] format = FORMATS.get(i % 7);
          tasks.add(
              () -> {
                inspector.verify(descriptor(format));
                return true;
              });
        }
        for (var result : pool.invokeAll(tasks)) assertTrue(result.get());
      }
      for (String[] format : FORMATS)
        assertEquals("abc", Files.readString(moved.resolve(format[1])));
      assertEquals("replacement must not be used", Files.readString(f.root.resolve("marker")));
      f.assertRootOwned();
    }
  }
}
