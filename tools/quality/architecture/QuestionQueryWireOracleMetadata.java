package dev.codex.schubert.nk.api.application.question;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;

/** G03 metadata only: no production classpath, database, crypto owner, or original Test loading. */
public final class QuestionQueryWireOracleMetadata {
  private QuestionQueryWireOracleMetadata() {}

  public static void main(String[] args) throws Exception {
    List<String> vectors = Files.readAllLines(Path.of(args[0]), StandardCharsets.US_ASCII);
    if (vectors.size() != 24) throw new AssertionError("vector inventory");
    int checked = 0;
    for (String row : vectors) {
      String[] fields = row.split("\t", -1);
      if (fields.length != 5) throw new AssertionError("vector schema");
      byte[] actual = wire(fields[0], fields[1], Integer.parseInt(fields[2]));
      if (actual.length != Integer.parseInt(fields[3])) throw new AssertionError("wire length");
      String hash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual));
      if (!hash.equals(fields[4])) throw new AssertionError("independent wire hash " + fields[0]);
      checked++;
    }
    int negatives = 0;
    for (String unknown : List.of("", "QSSRSP01", "XXXXXXXX")) {
      try {
        wire(unknown, "0000", 0);
        throw new AssertionError("unknown profile accepted");
      } catch (IllegalArgumentException expected) {
        negatives++;
      }
    }
    for (int count : new int[] {-1, 2}) {
      try {
        wire("QSSREQ01", "0000", count);
        throw new AssertionError("fixture bound accepted");
      } catch (IllegalArgumentException expected) {
        negatives++;
      }
    }
    byte[] first = wire("QSSREQ01", "0000", 1);
    first[0] = 0;
    if (wire("QSSREQ01", "0000", 1)[0] != 'S') throw new AssertionError("fresh array");
    System.out.println("METADATA\t" + checked + "\t" + negatives + "\tfresh-array\tPRODUCT_PT=0");
  }

  private static byte[] wire(String layout, String code, int count) {
    return QuestionQueryWireOracle.wire(
        layout,
        new UUID(100, 100),
        new UUID(101, 101),
        Instant.parse("2026-10-01T00:00:01.123456Z"),
        Instant.parse("2026-10-01T00:00:00.123456Z"),
        code,
        count);
  }
}
