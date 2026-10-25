package dev.codex.schubert.nk.batch.file;

import static dev.codex.schubert.nk.batch.file.MorningBackupRetentionTest.acceptsAll;
import static dev.codex.schubert.nk.batch.file.MorningBackupRetentionTest.generations;
import static dev.codex.schubert.nk.batch.file.MorningBackupRetentionTest.subject;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import dev.codex.schubert.nk.storage.OwnedTransferDirectory;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS341/343 SSC133, PT-OPS-RETWIRE-001/002: own synthetic fixture, independent wire oracle. */
final class RetentionWireBoundaryTest {
  @TempDir Path temporary;

  private static final String HEADER =
      "NKBRET1\n"
          + "boot_id=11111111-1111-4111-8111-111111111111\n"
          + "epoch_id=22222222-2222-4333-8444-555555555555\n"
          + "run_id=12345678-9abc-def0-8123-456789abcdef\n"
          + "cutoff_utc=2026-09-12T15:00:00.000000Z\n"
          + "activation_id=44444444-2222-4333-8444-555555555555\n"
          + "morning_invocation_id=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\n"
          + "broker_invocation_id=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n";
  private static final String ROOT = "ROOT|16832|2000|2001|11|12\n";
  private static final String PAYLOADS =
      "|26|9ae12cbba1c4e9e71419a38fde527ad49dac8ecd22d408173df80165d27d0aa9"
          + "|35|0793bedfb1288edbbf286aeda46ff08601492dc311bcc9ef352d5b76b4a0eb9a"
          + "|32|de5619301aab91cfd8872a1bd80b7f9c793bf01ca40fa38bfe2ac15ff93debb2\n";
  private static final List<String> NAMES =
      List.of(
          "20260906-000002-12345678-9abc-def0-8123-00000000006b",
          "20260907-000002-12345678-9abc-def0-8123-00000000006a",
          "20260908-000002-12345678-9abc-def0-8123-000000000069",
          "20260909-000002-12345678-9abc-def0-8123-000000000068",
          "20260910-000002-12345678-9abc-def0-8123-000000000067",
          "20260911-000002-12345678-9abc-def0-8123-000000000066",
          "20260912-000002-12345678-9abc-def0-8123-000000000065",
          "20260913-000002-12345678-9abc-def0-8123-456789abcdef");

  @Test
  void retwire001DeletedGenerationWholeFrameAndDiskPostconditions() throws Exception {
    try (var f = new BackupArtifactFixture(temporary);
        var root = OwnedTransferDirectory.open(MorningBackupRetention.directoryCalls(), f.parent)) {
      fixedMetadata(f);
      generations(
          f, 7); // Input creation only; expected order above is not obtained from production.
      var hashes = new LinkedHashMap<String, String>();
      var originals = new LinkedHashMap<Path, byte[]>();
      for (String name : NAMES) {
        Path directory = f.parent.resolve(name);
        byte[] input = Files.readAllBytes(directory.resolve("MANIFEST.json"));
        hashes.put(
            name, HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(input)));
        for (String file : BackupArtifactFixture.NAMES)
          originals.put(directory.resolve(file), Files.readAllBytes(directory.resolve(file)));
      }
      var expected = new StringBuilder(HEADER).append("MODE|NEW_SUCCESS\nCURRENT|");
      expected
          .append(hex(NAMES.getLast()))
          .append('|')
          .append(hashes.get(NAMES.getLast()))
          .append('\n');
      expected.append(ROOT).append("COUNTS|8|7|7|1|0\n");
      for (String name : NAMES) expected.append("BEFORE|").append(hex(name)).append('\n');
      for (String name : NAMES.subList(1, 8))
        expected.append("AFTER|").append(hex(name)).append('\n');
      expected
          .append("DELETE|")
          .append(hex(NAMES.getFirst()))
          .append('|')
          .append(hashes.get(NAMES.getFirst()))
          .append('\n');
      for (String name : NAMES.subList(1, 8))
        expected
            .append("RETAIN|")
            .append(hex(name))
            .append('|')
            .append(hashes.get(name))
            .append(PAYLOADS);
      var subject = subject(f, root, acceptsAll());
      var result =
          subject.collect(MorningBackupRetention.Mode.NEW_SUCCESS, Optional.of(f.expected));
      assertArrayEquals(expected.toString().getBytes(StandardCharsets.US_ASCII), render(f, result));
      assertFalse(Files.exists(f.parent.resolve(NAMES.getFirst()), LinkOption.NOFOLLOW_LINKS));
      try (var entries = Files.list(f.parent)) {
        assertEquals(
            NAMES.subList(1, 8), entries.map(p -> p.getFileName().toString()).sorted().toList());
      }
      for (var entry : originals.entrySet())
        if (!entry.getKey().startsWith(f.parent.resolve(NAMES.getFirst())))
          assertArrayEquals(entry.getValue(), Files.readAllBytes(entry.getKey()));
      subject.recheck();
      f.unchanged();
      f.released();
    }
  }

  @Test
  void retwire002InjectedName255Accepted256RejectedWithoutFilesystemNameCreation()
      throws Exception {
    for (int length : List.of(255, 256)) {
      try (var f = new BackupArtifactFixture(temporary)) {
        fixedMetadata(f);
        f.listing = held -> List.of(held.resolve("x".repeat(length)));
        var result =
            subject(f, f.root, acceptsAll())
                .collect(MorningBackupRetention.Mode.FAILED, Optional.empty());
        if (length == 255) {
          String expected =
              HEADER
                  + "MODE|FAILED\nCURRENT|-|-\n"
                  + ROOT
                  + "COUNTS|1|1|-|0|1\nBEFORE|"
                  + "78".repeat(255)
                  + "\nAFTER|"
                  + "78".repeat(255)
                  + "\nPROTECT|"
                  + "78".repeat(255)
                  + "|READ_ONLY\n";
          assertArrayEquals(expected.getBytes(StandardCharsets.US_ASCII), render(f, result));
        } else {
          assertThrows(IOException.class, () -> render(f, result));
        }
        f.unchanged();
        f.released();
      }
    }
  }

  private static void fixedMetadata(BackupArtifactFixture f) {
    f.metadata =
        (role, fields) -> {
          fields.put("dev", 11L);
          if (role.equals("parent")) fields.put("ino", 12L);
        };
  }

  private static String hex(String name) {
    return HexFormat.of().formatHex(name.getBytes(StandardCharsets.UTF_8));
  }

  private static byte[] render(BackupArtifactFixture f, MorningBackupRetention.Result result)
      throws IOException {
    var epoch =
        new StartupPermitRecords.Epoch(
            StartupPermitRecords.State.INVALID,
            UUID.fromString("11111111-1111-4111-8111-111111111111"),
            UUID.fromString("22222222-2222-4333-8444-555555555555"),
            new MaintenanceActivation(
                f.expected.run(), UUID.fromString("44444444-2222-4333-8444-555555555555")),
            Optional.empty());
    return MorningGateEvidence.retention(epoch, "a".repeat(32), "b".repeat(32), result);
  }
}
