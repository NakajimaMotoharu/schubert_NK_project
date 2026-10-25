package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.api.maintenance.InspectorDbCredential;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** ROOTSRC001..006: public synthetic host/root metadata, no real credential material. SSC138. */
final class RootServiceCredentialSourceTest {
  @TempDir Path temporary;

  private BackupPublicationFixture fixture() throws Exception {
    var f = new BackupPublicationFixture(temporary);
    Files.delete(f.child);
    f.copyFilesystem = "ext4";
    f.metadata =
        (role, m) -> {
          m.put("uid", 0);
          m.put("gid", 0);
          m.put("mode", role.equals("parent") ? 040700 : 0100600);
        };
    Files.writeString(f.parent.resolve("db-api"), "PUBLIC_é\n");
    return f;
  }

  private static RootBatchCredentialReader.Io io(BackupPublicationFixture f) {
    return new RootBatchCredentialReader.Io() {
      public Map<String, Object> attributes(Path held) throws IOException {
        return f.attributes(held);
      }

      public String filesystem(Path held) {
        return f.filesystem(held);
      }

      public java.nio.channels.SeekableByteChannel open(Path held) throws IOException {
        return f.open(held);
      }
    };
  }

  private static int read(BackupPublicationFixture f, byte[] material) throws IOException {
    try {
      return RootServiceCredentialSource.readFixed(
          f.root, f, io(f), new EnvironmentInodePolicy(f, f), "db-api", 0, material);
    } catch (IOException | RuntimeException | Error failure) {
      if (material != null) Arrays.fill(material, (byte) 0);
      throw failure;
    }
  }

  @Test
  void wholePublicUtf8BytesEofAndOwnedDecoderWipesCopy() throws Exception {
    try (var f = fixture()) {
      byte[] material = new byte[65537];
      f.chunk = 1;
      int count = read(f, material);
      byte[] literal = "PUBLIC_é\n".getBytes(StandardCharsets.UTF_8);
      assertEquals(literal.length, count);
      assertArrayEquals(literal, Arrays.copyOf(material, count));
      byte[] owned = Arrays.copyOf(material, count);
      try (var secret = InspectorDbCredential.consume(owned)) {
        char[] actual = secret.copyPassword();
        assertArrayEquals("PUBLIC_é".toCharArray(), actual);
        Arrays.fill(actual, '\0');
        assertArrayEquals(new byte[owned.length], owned);
      }
      Arrays.fill(material, (byte) 0);
      f.released();
    }
  }

  @Test
  void everySecurityMutationRefusesRootSourceWithoutRepair() throws Exception {
    for (String fault :
        List.of(
            "uid", "gid", "mode", "link", "readonly", "fs", "acl", "size", "device", "effective")) {
      try (var f = fixture()) {
        switch (fault) {
          case "readonly" -> f.readonly = true;
          case "fs" -> f.copyFilesystem = "nfs";
          case "acl" -> f.acl = new byte[] {1};
          case "effective" -> f.effective = 1;
          default ->
              f.metadata =
                  (role, m) -> {
                    m.put("uid", 0);
                    m.put("gid", 0);
                    m.put("mode", role.equals("parent") ? 040700 : 0100600);
                    if (!role.equals("parent"))
                      switch (fault) {
                        case "uid" -> m.put("uid", 1);
                        case "gid" -> m.put("gid", 1);
                        case "mode" -> m.put("mode", 0100640);
                        case "link" -> m.put("nlink", 2);
                        case "size" -> m.put("size", 65537L);
                        default -> m.put("dev", -1L);
                      }
                  };
        }
        assertThrows(IOException.class, () -> read(f, new byte[65537]), fault);
        assertEquals("PUBLIC_é\n", Files.readString(f.parent.resolve("db-api")));
        f.released();
      }
    }
  }

  @Test
  void allReadIoPositionsAndInvalidProgressFailClosed() throws Exception {
    int positions;
    try (var f = fixture()) {
      f.position = 0;
      read(f, new byte[65537]);
      positions = f.position;
    }
    for (int i = 1; i <= positions; i++)
      try (var f = fixture()) {
        f.position = 0;
        f.faultAt = i;
        assertThrows(IOException.class, () -> read(f, new byte[65537]));
        f.released();
      }
    for (String fault :
        List.of("zero", "short", "large", "position", "extra-any", "eof-position-any"))
      try (var f = fixture()) {
        f.readMode = fault;
        assertThrows(IOException.class, () -> read(f, new byte[65537]), fault);
        if (fault.equals("extra-any")) assertTrue(f.counts.get("extraInjected") > 0);
        if (fault.equals("eof-position-any")) assertEquals(1, f.counts.get("eofPositionInjected"));
        f.released();
      }
    try (var f = fixture()) {
      assertThrows(IOException.class, () -> read(f, new byte[65536]));
      assertThrows(NullPointerException.class, () -> read(f, null));
      Files.delete(f.parent.resolve("db-api"));
      assertThrows(IOException.class, () -> read(f, new byte[65537]));
      f.released();
    }
  }
}
