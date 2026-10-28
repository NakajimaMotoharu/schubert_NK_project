package dev.codex.schubert.nk.bootstrap;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

/** PT-OPS-PROOF-001..008, literal public vector independent of schema/production encoder. */
final class StartupProofFrameTest {
  private static final String FIXTURE_SERVICE_3E9B10A4 = "service";
  private static final String GOLDEN =
      """
      NKSTART1
      service=API
      boot_id=11111111-1111-1111-1111-111111111111
      invocation_id=11111111111111111111111111111111
      pid=42
      start_ticks=12345
      admission_fd=128
      admission_device=123
      admission_inode=456
      service_uid=200
      service_gid=201
      service_groups=200,201,202
      permit_epoch=33333333-3333-3333-3333-333333333333
      permit_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
      release_sha256=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
      config_sha256=cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
      roots_sha256=dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd
      broker_invocation_id=22222222222222222222222222222222
      """;

  @Test
  void proof001IndependentGoldenAndExplicitFieldOrdering() {
    var input = bytes(GOLDEN);
    var parsed = StartupProofFrame.parse(input);
    assertArrayEquals(bytes(GOLDEN), parsed.encode());
    var builderInput = fields();
    var built = StartupProofFrame.fromFields(builderInput);
    assertArrayEquals(bytes(GOLDEN), built.encode());
    assertEquals(fields(), parsed.fields());
    assertEquals("128", parsed.value("admission_fd"));
    assertEquals("StartupProofFrame[REDACTED]", parsed.toString());
    assertFalse(parsed.fields().containsKey("proof_fd"));
  }

  @Test
  void proof002EveryMissingExtraDuplicateAndNoncanonicalRow() {
    for (String key : fields().keySet()) {
      var missing = fields();
      missing.remove(key);
      invalid(() -> StartupProofFrame.fromFields(missing));
      String original = key + "=" + fields().get(key) + "\n";
      invalid(() -> StartupProofFrame.parse(bytes(GOLDEN.replace(original, ""))));
      invalid(() -> StartupProofFrame.parse(bytes(GOLDEN.replace(original, original + original))));
      invalid(
          () ->
              StartupProofFrame.parse(
                  bytes(GOLDEN.replace(original, "unknown=" + fields().get(key) + "\n"))));
    }
    var extra = fields();
    extra.put("proof_fd", "129");
    invalid(() -> StartupProofFrame.fromFields(extra));
    invalid(
        () ->
            StartupProofFrame.parse(
                bytes(GOLDEN.replace("service=API\nboot_id=", "boot_id=API\nservice="))));
    invalid(() -> StartupProofFrame.parse(bytes(GOLDEN.replace("NKSTART1", "NKSTART2"))));
    invalid(() -> StartupProofFrame.parse(bytes(GOLDEN.substring(0, GOLDEN.length() - 1))));
    invalid(() -> StartupProofFrame.parse(bytes(GOLDEN + "\n")));
    invalid(
        () -> StartupProofFrame.parse(bytes(GOLDEN.substring(0, GOLDEN.length() - 1) + "\nextra")));
    invalid(() -> StartupProofFrame.parse(bytes(GOLDEN.replace("service=API", "service : API"))));
  }

  @Test
  void proof003AsciiByteSizeAndEveryNullContract() {
    for (int b : List.of(0, 9, 13, 31, 127, 128, 255)) {
      byte[] input = bytes(GOLDEN);
      input[0] = (byte) b;
      invalid(() -> StartupProofFrame.parse(input));
      assertEquals((byte) b, input[0]);
    }
    for (int size : List.of(0, 8192, 8193)) invalid(() -> StartupProofFrame.parse(new byte[size]));
    assertThrows(NullPointerException.class, () -> StartupProofFrame.parse(null));
    assertThrows(NullPointerException.class, () -> StartupProofFrame.fromFields(null));
    var nullValue = fields();
    nullValue.put(FIXTURE_SERVICE_3E9B10A4, null);
    assertThrows(NullPointerException.class, () -> StartupProofFrame.fromFields(nullValue));
    var nullKey = fields();
    nullKey.put(null, "API");
    assertThrows(NullPointerException.class, () -> StartupProofFrame.fromFields(nullKey));
    var frame = StartupProofFrame.parse(bytes(GOLDEN));
    assertThrows(NullPointerException.class, () -> frame.value(null));
    invalid(() -> frame.value("proof_fd"));
  }

  @Test
  void proof004NumericLowerUpperOverflowAndCanonicalDecimals() {
    for (var bounds :
        Map.of(
                "pid",
                List.of("2", "2147483647"),
                "start_ticks",
                List.of("1", "9223372036854775807"),
                "admission_fd",
                List.of("128", "65535"),
                "admission_device",
                List.of("1", "18446744073709551615"),
                "admission_inode",
                List.of("1", "18446744073709551615"),
                "service_uid",
                List.of("1", "4294967294"),
                "service_gid",
                List.of("1", "4294967294"))
            .entrySet()) {
      for (String valid : bounds.getValue())
        assertEquals(
            valid,
            StartupProofFrame.fromFields(with(bounds.getKey(), valid)).value(bounds.getKey()));
      for (String bad :
          List.of(
              "",
              "0",
              "-1",
              "+1",
              "01",
              " 1",
              "1 ",
              "1.0",
              "1e3",
              "1\n",
              "18446744073709551616",
              "9".repeat(21)))
        invalid(() -> StartupProofFrame.fromFields(with(bounds.getKey(), bad)));
    }
    for (var bad :
        Map.of(
                "pid",
                List.of("1", "2147483648"),
                "start_ticks",
                List.of("9223372036854775808"),
                "admission_fd",
                List.of("1", "127", "65536"),
                "service_uid",
                List.of("4294967295"),
                "service_gid",
                List.of("4294967295"))
            .entrySet())
      for (String value : bad.getValue())
        invalid(() -> StartupProofFrame.fromFields(with(bad.getKey(), value)));
  }

  @Test
  void proof005StrictSortedGroupsAndInvalidGroupBoundary() {
    for (String valid : List.of("1", "4294967294", "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16"))
      assertEquals(
          valid,
          StartupProofFrame.fromFields(with("service_groups", valid)).value("service_groups"));
    for (String bad :
        List.of(
            "",
            "0",
            "01",
            "1,1",
            "2,1",
            "1,0",
            "1,4294967295",
            "4294967295",
            "1, 2",
            "1,",
            "-1",
            "1\n2",
            "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17"))
      invalid(() -> StartupProofFrame.fromFields(with("service_groups", bad)));
  }

  @Test
  void proof006ServiceBootEpochInvocationAndDigestDomains() {
    assertEquals(
        "WEB",
        StartupProofFrame.fromFields(with(FIXTURE_SERVICE_3E9B10A4, "WEB"))
            .value(FIXTURE_SERVICE_3E9B10A4));
    for (String service : List.of("web", "ROOT", "BATCH", " API", "API\n", "API=WEB"))
      invalid(() -> StartupProofFrame.fromFields(with(FIXTURE_SERVICE_3E9B10A4, service)));
    for (String key : List.of("boot_id", "permit_epoch"))
      for (String bad :
          List.of(
              "00000000-0000-0000-0000-000000000000",
              "1-1-1-1-1",
              "A1111111-1111-1111-1111-111111111111",
              "11111111-1111-1111-1111-111111111111 ",
              "1".repeat(32))) invalid(() -> StartupProofFrame.fromFields(with(key, bad)));
    for (String key : List.of("invocation_id", "broker_invocation_id"))
      for (String bad :
          List.of("0".repeat(32), "1".repeat(31), "1".repeat(33), "A".repeat(32), "1-1"))
        invalid(() -> StartupProofFrame.fromFields(with(key, bad)));
    for (String key : List.of("permit_sha256", "release_sha256", "config_sha256", "roots_sha256")) {
      assertEquals(
          "0".repeat(64), StartupProofFrame.fromFields(with(key, "0".repeat(64))).value(key));
      for (String bad :
          List.of("a".repeat(63), "a".repeat(65), "A".repeat(64), "g".repeat(64), "1".repeat(32)))
        invalid(() -> StartupProofFrame.fromFields(with(key, bad)));
    }
    var frame = StartupProofFrame.parse(bytes(GOLDEN));
    assertEquals("a".repeat(64), frame.value("permit_sha256"));
    assertEquals("b".repeat(64), frame.value("release_sha256"));
    assertEquals("c".repeat(64), frame.value("config_sha256"));
    assertEquals("d".repeat(64), frame.value("roots_sha256"));
  }

  @Test
  void proof007ImmutableInputSnapshotAndByteOwnership() {
    var fields = fields();
    var frame = StartupProofFrame.fromFields(fields);
    fields.put(FIXTURE_SERVICE_3E9B10A4, "WEB");
    fields.clear();
    assertArrayEquals(bytes(GOLDEN), frame.encode());
    assertThrows(UnsupportedOperationException.class, () -> frame.fields().put("pid", "3"));
    byte[] input = bytes(GOLDEN);
    byte[] initial = input.clone();
    var parsed = StartupProofFrame.parse(input);
    assertArrayEquals(initial, input);
    Arrays.fill(input, (byte) 0);
    assertArrayEquals(bytes(GOLDEN), parsed.encode());
    byte[] output = parsed.encode();
    Arrays.fill(output, (byte) 0);
    assertArrayEquals(bytes(GOLDEN), parsed.encode());
  }

  @Test
  void proof008ConcurrentIndependentImmutableFrames() throws Exception {
    try (var executor = Executors.newFixedThreadPool(8)) {
      var work = new ArrayList<Callable<byte[]>>();
      for (int i = 0; i < 32; i++) work.add(() -> StartupProofFrame.parse(bytes(GOLDEN)).encode());
      for (var result : executor.invokeAll(work)) assertArrayEquals(bytes(GOLDEN), result.get());
    }
  }

  private static Map<String, String> fields() {
    var map = new HashMap<String, String>();
    for (String line : GOLDEN.lines().skip(1).toList()) {
      int at = line.indexOf('=');
      map.put(line.substring(0, at), line.substring(at + 1));
    }
    return map;
  }

  private static Map<String, String> with(String key, String value) {
    var fields = fields();
    fields.put(key, value);
    return fields;
  }

  private static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.US_ASCII);
  }

  private static void invalid(org.junit.jupiter.api.function.Executable operation) {
    var e = assertThrows(IllegalArgumentException.class, operation);
    assertEquals("invalid startup proof frame", e.getMessage());
    assertNull(e.getCause());
    assertEquals(0, e.getSuppressed().length);
  }
}
