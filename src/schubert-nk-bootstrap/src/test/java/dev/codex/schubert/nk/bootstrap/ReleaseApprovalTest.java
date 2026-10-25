package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** Independent literal ASCII frames; public digest only, never production-generated expected. */
final class ReleaseApprovalTest {
  private static final String SHA =
      "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb";
  private static final String GOLDEN =
      "NKRELEASEAPPROVAL1\nversion=1.2.3-PG313\nmanifest_sha256=" + SHA + "\n";

  private static byte[] bytes(String s) {
    return s.getBytes(StandardCharsets.UTF_8);
  }

  private static void refused(String s) {
    assertThrows(IllegalArgumentException.class, () -> ReleaseApproval.parse(bytes(s)));
  }

  @Test
  void approval001IndependentLiteral() {
    var decoded = ReleaseApproval.parse(bytes(GOLDEN));
    assertEquals("1.2.3-PG313", decoded.version());
    assertEquals(SHA, decoded.manifestSha256());
    assertArrayEquals(bytes(GOLDEN), new ReleaseApproval("1.2.3-PG313", SHA).encode());
  }

  @Test
  void approval002VersionBoundaries() {
    for (String version : List.of("A", "a".repeat(64), "0._-Z")) {
      String expected =
          "NKRELEASEAPPROVAL1\nversion=" + version + "\nmanifest_sha256=" + SHA + "\n";
      assertArrayEquals(bytes(expected), new ReleaseApproval(version, SHA).encode());
      assertEquals(version, ReleaseApproval.parse(bytes(expected)).version());
    }
    for (String v : List.of("", "a".repeat(65), "-x", ".x", "../x", "a/b", "é", "x\n")) {
      assertThrows(IllegalArgumentException.class, () -> new ReleaseApproval(v, SHA));
      refused(GOLDEN.replace("1.2.3-PG313", v));
    }
  }

  @Test
  void approval003NullAndDigestContracts() {
    assertThrows(NullPointerException.class, () -> new ReleaseApproval(null, SHA));
    assertThrows(NullPointerException.class, () -> new ReleaseApproval("A", null));
    assertThrows(NullPointerException.class, () -> ReleaseApproval.parse(null));
    for (String s :
        List.of(
            "",
            "b".repeat(63),
            "b".repeat(65),
            "B".repeat(64),
            "g".repeat(64),
            "b".repeat(63) + "\0")) {
      assertThrows(IllegalArgumentException.class, () -> new ReleaseApproval("A", s));
      refused(GOLDEN.replace(SHA, s));
    }
  }

  @Test
  void approval004ByteBoundsAndNonAscii() {
    assertEquals(192, ReleaseApproval.MAX_BYTES);
    for (int length : List.of(0, 192, 193))
      assertThrows(IllegalArgumentException.class, () -> ReleaseApproval.parse(new byte[length]));
    var invalid = bytes(GOLDEN);
    invalid[0] = (byte) 0xff;
    assertThrows(IllegalArgumentException.class, () -> ReleaseApproval.parse(invalid));
    refused("\ufeff" + GOLDEN);
    refused(GOLDEN.replace("version=", "versión="));
  }

  @Test
  void approval005CanonicalOrderAndKeys() {
    for (String s :
        List.of(
            GOLDEN.replace("\n", "\r\n"),
            GOLDEN.stripTrailing(),
            GOLDEN + "\n",
            GOLDEN + "approved=true\n",
            GOLDEN.replace("version=", "unknown="),
            GOLDEN.replace("version=", "version=A\nversion="),
            "NKRELEASEAPPROVAL1\nmanifest_sha256=" + SHA + "\nversion=1.2.3-PG313\n",
            GOLDEN.replace("manifest_sha256=", "manifest_sha256=\\u0062"))) refused(s);
  }

  @Test
  void approval006DefensiveCopies() {
    byte[] input = bytes(GOLDEN);
    byte[] saved = input.clone();
    var value = ReleaseApproval.parse(input);
    assertArrayEquals(saved, input);
    Arrays.fill(input, (byte) 0);
    byte[] encoded = value.encode();
    Arrays.fill(encoded, (byte) 0);
    assertArrayEquals(bytes(GOLDEN), value.encode());
    assertEquals(SHA, value.manifestSha256());
  }

  @Test
  void approval007ParallelOwners() throws Exception {
    try (var executor = Executors.newFixedThreadPool(4)) {
      var barrier = new CyclicBarrier(4);
      var futures = new ArrayList<Future<String>>();
      for (int i = 0; i < 4; i++)
        futures.add(
            executor.submit(
                () -> {
                  barrier.await(5, TimeUnit.SECONDS);
                  return ReleaseApproval.parse(bytes(GOLDEN)).version();
                }));
      for (var future : futures) assertEquals("1.2.3-PG313", future.get(5, TimeUnit.SECONDS));
    }
  }

  @Test
  void approval008HeaderAndFixedProfile() {
    for (String s :
        List.of(
            GOLDEN.replace("NKRELEASEAPPROVAL1", "NKRELEASEAPPROVAL2"),
            GOLDEN.replace("NKRELEASEAPPROVAL1", ""),
            GOLDEN.replace("\nversion=", "\nversion= "),
            " " + GOLDEN,
            GOLDEN.replace("\nmanifest_sha256=", "\nmanifest_sha256= "))) refused(s);
    assertEquals(
        "0",
        ReleaseApproval.parse(
                bytes("NKRELEASEAPPROVAL1\nversion=0\nmanifest_sha256=" + "0".repeat(64) + "\n"))
            .version());
  }
}
