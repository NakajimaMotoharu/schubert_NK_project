package dev.codex.schubert.nk.api.file;

import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.FORMATS;
import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.descriptor;
import static dev.codex.schubert.nk.api.file.AssetChecksumManifestTest.reject;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import dev.codex.schubert.nk.storage.StorageIdentity;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.GroupPrincipal;
import java.nio.file.attribute.UserPrincipal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** Retained real files, independent Unix permissions and injected failures. PT-MED-045/046. */
class AssetManifestLoaderTest {
  @TempDir Path directory;

  @Test
  void med045HeldManifestLoadsWithoutReopeningOrMutatingNames() throws Exception {
    try (var fixture = new MediaAssetFixture(directory.resolve("normal"))) {
      byte[] before = Files.readAllBytes(fixture.manifest);
      var manifest = new AssetManifestLoader(fixture.held, fixture.identity).load(7);
      assertEquals(7, manifest.entryCount());
      for (String[] format : FORMATS) manifest.requireMatches(descriptor(format));
      assertArrayEquals(before, Files.readAllBytes(fixture.manifest));
      assertEquals(0100640, Files.getAttribute(fixture.manifest, "unix:mode"));
      fixture.assertRootOwned();
      var io = new FaultIo();
      io.renameFrom = fixture.manifest;
      var retained = new AssetManifestLoader(fixture.held, fixture.identity, io).load(7);
      for (String[] format : FORMATS) retained.requireMatches(descriptor(format));
      assertEquals("REPLACED_SYNTHETIC_MANIFEST", Files.readString(fixture.manifest));
      assertArrayEquals(
          before, Files.readAllBytes(fixture.manifest.resolveSibling("saved.sha256")));
      assertEquals(1, io.opens);
      assertEquals(1, io.closes);
      fixture.assertRootOwned();
    }
  }

  @Test
  void med046NullLinksAttributesAndIoFaultsFailClosed() throws Exception {
    try (var fixture = new MediaAssetFixture(directory.resolve("faults"))) {
      assertThrows(
          NullPointerException.class, () -> new AssetManifestLoader(null, fixture.identity));
      assertThrows(NullPointerException.class, () -> new AssetManifestLoader(fixture.held, null));
      assertThrows(
          NullPointerException.class,
          () -> new AssetManifestLoader(fixture.held, fixture.identity, null));
      var countIo = new FaultIo();
      var loader = new AssetManifestLoader(fixture.held, fixture.identity, countIo);
      for (int count : new int[] {0, -1, 59_628})
        assertThrows(IllegalArgumentException.class, () -> loader.load(count));
      assertEquals(0, countIo.attributes);
      reject(
          () ->
              new AssetManifestLoader(fixture.held, new StorageIdentity("not-owner", "not-group"))
                  .load(7));
      for (int step = 1; step <= 4; step++) {
        for (String fault : List.of("io", "unsupported", "owner", "group", "mode", "nlink")) {
          var io = new FaultIo();
          io.attributeStep = step;
          io.attributeFault = fault;
          reject(() -> new AssetManifestLoader(fixture.held, fixture.identity, io).load(7));
          assertEquals(io.opens, io.closes);
          fixture.assertRootOwned();
        }
      }
      for (Object bad :
          List.of(
              "missing",
              Integer.valueOf(100),
              Long.valueOf(0),
              Long.valueOf(-1),
              Long.valueOf(34_524_034))) {
        var io = new FaultIo();
        io.attributeStep = 3;
        io.attributeFault = "size";
        io.sizeValue = bad;
        reject(() -> new AssetManifestLoader(fixture.held, fixture.identity, io).load(7));
        assertEquals(0, io.opens);
        fixture.assertRootOwned();
      }
      for (String fault :
          List.of(
              "open",
              "read",
              "zero",
              "size-io",
              "size-before",
              "size-after",
              "close",
              "read-close")) {
        var io = new FaultIo();
        io.channelFault = fault;
        reject(() -> new AssetManifestLoader(fixture.held, fixture.identity, io).load(7));
        assertEquals(io.opens, io.closes);
        fixture.assertRootOwned();
      }
      for (int close : new int[] {1, 2}) {
        fixture.calls.failCloseAfter = close;
        reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
        fixture.assertRootOwned();
      }
      fixture.calls.failCloseAfter = Integer.MAX_VALUE;
      Path saved = fixture.manifest.resolveSibling("saved.sha256");
      Files.move(fixture.manifest, saved);
      reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
      Files.createSymbolicLink(fixture.manifest, saved);
      reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
      Files.delete(fixture.manifest); // Test-owned symlink only.
      Files.createLink(fixture.manifest, saved);
      reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
      Files.delete(fixture.manifest); // Test-owned hardlink only; original retained.
      Files.move(saved, fixture.manifest);
      MediaAssetFixture.mode(fixture.manifest, "rw-------");
      reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
      assertEquals(0100600, Files.getAttribute(fixture.manifest, "unix:mode"));
      MediaAssetFixture.mode(fixture.manifest, "rw-r-----");
      Files.writeString(fixture.manifest, "");
      reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
      Path manifests = fixture.manifest.getParent();
      Path moved = fixture.root.resolve("saved-manifests");
      Files.move(manifests, moved);
      reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
      Files.createSymbolicLink(manifests, moved);
      reject(() -> new AssetManifestLoader(fixture.held, fixture.identity).load(7));
      fixture.assertRootOwned();
    }
    var closed = new MediaAssetFixture(directory.resolve("closed"));
    var closedLoader = new AssetManifestLoader(closed.held, closed.identity);
    closed.close();
    reject(() -> closedLoader.load(7));
  }

  private static final class FaultIo implements AssetManifestLoader.Io {
    int attributes;
    int attributeStep;
    String attributeFault = "";
    Object sizeValue = "missing";
    String channelFault = "";
    int opens;
    int closes;
    @org.jspecify.annotations.Nullable Path renameFrom;

    @Override
    public Map<String, Object> attributes(Path held) throws IOException {
      Map<String, Object> values =
          new HashMap<>(Files.readAttributes(held, "unix:owner,group,mode,nlink,size"));
      if (++attributes == attributeStep) {
        switch (attributeFault) {
          case "io" -> throw new IOException("SYNTHETIC_PRIVATE_ATTRIBUTES");
          case "unsupported" ->
              throw new UnsupportedOperationException("SYNTHETIC_PRIVATE_PROVIDER");
          case "owner" -> values.put("owner", (UserPrincipal) () -> "not-owner");
          case "group" -> values.put("group", (GroupPrincipal) () -> "not-group");
          case "mode" -> values.put("mode", 0100600);
          case "nlink" -> values.put("nlink", 0);
          case "size" -> {
            values.remove("size");
            if (!sizeValue.equals("missing")) values.put("size", sizeValue);
          }
          default -> fail("unknown test fault");
        }
      }
      return values;
    }

    @Override
    public SeekableByteChannel openReadOnly(Path held) throws IOException {
      if (channelFault.equals("open")) throw new IOException("SYNTHETIC_PRIVATE_OPEN");
      if (renameFrom != null) {
        Files.move(renameFrom, renameFrom.resolveSibling("saved.sha256"));
        Files.writeString(renameFrom, "REPLACED_SYNTHETIC_MANIFEST");
      }
      var channel = FileChannel.open(held, StandardOpenOption.READ);
      opens++;
      return new SeekableByteChannel() {
        int sizeCalls;

        @Override
        public int read(ByteBuffer output) throws IOException {
          if (channelFault.contains("read")) throw new IOException("SYNTHETIC_PRIVATE_READ");
          if (channelFault.equals("zero")) return 0;
          return channel.read(output);
        }

        @Override
        public long size() throws IOException {
          sizeCalls++;
          if (channelFault.equals("size-io")) throw new IOException("SYNTHETIC_PRIVATE_SIZE");
          if ((sizeCalls == 1 && channelFault.equals("size-before"))
              || (sizeCalls == 2 && channelFault.equals("size-after"))) return channel.size() + 1;
          return channel.size();
        }

        @Override
        public void close() throws IOException {
          assertTrue(channel.isOpen());
          channel.close();
          closes++;
          if (channelFault.contains("close")) throw new IOException("SYNTHETIC_PRIVATE_CLOSE");
        }

        @Override
        public boolean isOpen() {
          return channel.isOpen();
        }

        @Override
        public long position() {
          return fail("manifest needs no seeking");
        }

        @Override
        public SeekableByteChannel position(long p) {
          return fail("manifest needs no seeking");
        }

        @Override
        public int write(ByteBuffer input) {
          return fail("readonly");
        }

        @Override
        public SeekableByteChannel truncate(long n) {
          return fail("readonly");
        }
      };
    }
  }
}
