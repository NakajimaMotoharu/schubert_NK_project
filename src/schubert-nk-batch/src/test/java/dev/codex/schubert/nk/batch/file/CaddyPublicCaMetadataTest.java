package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertThrows;

import java.io.IOException;
import java.nio.file.attribute.FileTime;
import org.junit.jupiter.api.Test;

/** NK-OPS-001; SS342/SSC183; CA461001..003. Independent POSIX literals, no native waiver. */
final class CaddyPublicCaMetadataTest {
  private static EnvironmentInodePolicy.Metadata literal(
      int mode, long uid, long gid, int links, long size) {
    return new EnvironmentInodePolicy.Metadata(
        mode, uid, gid, links, size, 7, 101, FileTime.fromMillis(0), FileTime.fromMillis(0));
  }

  @Test
  void ca461001OnlyFixedPublicCaModesAndSizeBoundaries() throws Exception {
    for (int mode : new int[] {0100600, 0100640, 0100644}) {
      for (long size : new long[] {1, 631, 65536}) {
        CaddyPublicConfiguration.requireFileMetadata(
            literal(mode, 993, 978, 1, size), 993, 978, true);
      }
    }
    // Public-CA permission cannot leak into the root-owned configuration contract.
    CaddyPublicConfiguration.requireFileMetadata(literal(0100640, 0, 978, 1, 1), 0, 978, false);
    for (int mode : new int[] {0100600, 0100644}) {
      assertThrows(
          IOException.class,
          () ->
              CaddyPublicConfiguration.requireFileMetadata(
                  literal(mode, 0, 978, 1, 631), 0, 978, false));
    }
  }

  @Test
  void ca461002UnknownModesOwnerLinksAndSizeAreNotRepaired() {
    for (int mode :
        new int[] {
          0, 040700, 0120600, 0100400, 0100620, 0100660, 0100666, 0100700, 0102640, 0104640
        }) {
      assertThrows(
          IOException.class,
          () ->
              CaddyPublicConfiguration.requireFileMetadata(
                  literal(mode, 993, 978, 1, 631), 993, 978, true));
    }
    for (var invalid :
        new EnvironmentInodePolicy.Metadata[] {
          literal(0100600, 0, 978, 1, 631), literal(0100600, 993, 0, 1, 631),
          literal(0100600, 993, 978, 0, 631), literal(0100600, 993, 978, 2, 631),
          literal(0100600, 993, 978, 1, 0), literal(0100600, 993, 978, 1, -1),
          literal(0100600, 993, 978, 1, 65537), literal(0100600, 993, 978, 1, Long.MAX_VALUE)
        }) {
      assertThrows(
          IOException.class,
          () -> CaddyPublicConfiguration.requireFileMetadata(invalid, 993, 978, true));
    }
  }

  @Test
  void ca461003NullIsRejectedBeforeAnyFileAccess() {
    assertThrows(
        NullPointerException.class,
        () -> CaddyPublicConfiguration.requireFileMetadata(null, 993, 978, true));
  }
}
