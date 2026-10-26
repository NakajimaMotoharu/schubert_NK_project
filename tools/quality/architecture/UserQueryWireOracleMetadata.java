package dev.codex.schubert.nk.api.application.admin;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;

/** Independent metadata only, no production/old Test classpath. */
public final class UserQueryWireOracleMetadata {
  private UserQueryWireOracleMetadata() {}

  public static void main(String[] args) throws Exception {
    List<String> lines = Files.readAllLines(Path.of(args[0]), StandardCharsets.US_ASCII);
    if (lines.size() != 27) throw new AssertionError("vector inventory");
    int checked = 0;
    for (String line : lines) {
      String[] f = line.split("\t", -1);
      if (f.length != 9) throw new AssertionError("vector schema");
      byte[] actual =
          wire(
              f[0],
              f[1],
              Integer.parseInt(f[2]),
              Long.parseLong(f[3]),
              Integer.parseInt(f[4]),
              Long.parseLong(f[5]),
              Boolean.parseBoolean(f[6]));
      if (actual.length != Integer.parseInt(f[7])) throw new AssertionError("length");
      String hash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(actual));
      if (!hash.equals(f[8])) throw new AssertionError("independent whole wire " + f[0]);
      checked++;
    }
    int negative = 0;
    for (String profile : List.of("", "UDTRSP01", "UNKNOWN1")) {
      try {
        wire(profile, "0000", 0, 0, 1, 1, false);
        throw new AssertionError("unknown profile accepted");
      } catch (IllegalArgumentException expected) {
        negative++;
      }
    }
    byte[] first = wire("USRREQ01", "0000", 1, 1, 1, 0, false);
    first[0] = 0;
    if (wire("USRREQ01", "0000", 1, 1, 1, 0, false)[0] != 'S')
      throw new AssertionError("shared array");
    System.out.println("METADATA\t" + checked + "\t" + negative + "\tfresh-array\tPRODUCT_PT=0");
  }

  private static byte[] wire(
      String layout, String code, int count, long total, int page, long target, boolean optional) {
    return UserQueryWireOracle.wire(
        layout,
        new UUID(100, 100),
        new UUID(101, 101),
        Instant.parse("2026-10-01T00:00:01.123456Z"),
        Instant.parse("2026-10-01T00:00:00.123456Z"),
        code,
        count,
        total,
        page,
        target,
        optional);
  }
}
