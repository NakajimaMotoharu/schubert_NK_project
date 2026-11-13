package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** PT-OPS-BREQ001..008 fixed request codec; root/file/worker admission tested separately. */
final class BackupWorkerRequestTest {
  private static final String VERIFY_DUMP_SIZE_ASSIGNMENT = "dump_size=3";

  private static final UUID RUN = UUID.fromString("11111111-2222-4333-8444-555555555555");
  private static final Instant START = Instant.parse("2026-09-27T14:59:59.123456Z");
  private static final String GOLDEN =
      "NKBACKUP1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T14:59:59.123456Z\n";

  private static byte[] bytes(String s) {
    return s.getBytes(StandardCharsets.US_ASCII);
  }

  private void refused(byte[] input) {
    assertThrows(IllegalArgumentException.class, () -> BackupWorkerRequest.consume(input));
    assertArrayEquals(new byte[input.length], input);
  }

  @Test
  void genuineVerificationProfileLiteralAndClosedInvariants() {
    String golden =
        "NKBACKUPVERIFY1\nrun=11111111-2222-4333-8444-555555555555\nstarted=2026-09-27T14:59:59.123456Z\n"
            + "manifest_sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\ndump_size=3\n"
            + "dump_sha256=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\n";
    byte[] input = bytes(golden);
    var request = BackupWorkerRequest.consume(input);
    assertArrayEquals(new byte[input.length], input);
    assertEquals(RUN, request.run());
    assertEquals(START, request.started());
    assertEquals(3, request.verification().orElseThrow().dumpSize());
    assertArrayEquals(bytes(golden), request.encode());
    assertEquals("20260927-235959-11111111-2222-4333-8444-555555555555", request.directoryName());
    assertTrue(new BackupWorkerRequest(RUN, START).verification().isEmpty());
    for (String bad :
        List.of(
            golden.replace("NKBACKUPVERIFY1", "NKBACKUP1"),
            GOLDEN.replace("NKBACKUP1", "NKBACKUPVERIFY1"),
            golden.replace(VERIFY_DUMP_SIZE_ASSIGNMENT, "dump_size=03"),
            golden.replace(VERIFY_DUMP_SIZE_ASSIGNMENT, "dump_size=0"),
            golden.replace(VERIFY_DUMP_SIZE_ASSIGNMENT, "dump_size=-1"),
            golden.replace(VERIFY_DUMP_SIZE_ASSIGNMENT, "dump_size=9223372036854775808"),
            golden.replace("manifest_sha256=", "manifest="),
            golden.replace("dump_sha256=", "command="),
            golden.replace("dump_size=", "path="),
            golden.replace("aaaaaaaa", "AAAAAAAA"),
            golden.replace("ba7816bf", "zz7816bf"),
            golden + "extra\n",
            golden.replace("dump_size=3\n", ""))) refused(bytes(bad));
    assertThrows(NullPointerException.class, () -> new BackupWorkerRequest(RUN, START, null));
    assertThrows(
        NullPointerException.class,
        () -> new BackupWorkerRequest.Verification(null, 3, "b".repeat(64)));
    assertThrows(
        NullPointerException.class,
        () -> new BackupWorkerRequest.Verification("a".repeat(64), 3, null));
    refused(new byte[401]);
  }

  @Test
  void literalCanonicalAndIndependentDirectory() {
    var expected = new BackupWorkerRequest(RUN, START);
    byte[] owned = bytes(GOLDEN);
    assertEquals(expected, BackupWorkerRequest.consume(owned));
    assertArrayEquals(new byte[owned.length], owned);
    assertArrayEquals(bytes(GOLDEN), expected.encode());
    assertEquals("20260927-235959-11111111-2222-4333-8444-555555555555", expected.directoryName());
  }

  @Test
  void dateAndMicroBoundaries() {
    var low = new BackupWorkerRequest(RUN, Instant.parse("0000-12-31T14:41:01Z"));
    assertEquals("00010101-000000-11111111-2222-4333-8444-555555555555", low.directoryName());
    var high = new BackupWorkerRequest(RUN, Instant.parse("9999-12-31T14:59:59.999999Z"));
    assertEquals(
        "00010101-001859-11111111-2222-4333-8444-555555555555",
        new BackupWorkerRequest(RUN, Instant.parse("0000-12-31T15:00:00Z")).directoryName());
    assertEquals("99991231-235959-11111111-2222-4333-8444-555555555555", high.directoryName());
    for (Instant wrong :
        List.of(
            Instant.MIN,
            Instant.MAX,
            Instant.parse("0000-12-31T14:41:00.999999Z"),
            Instant.parse("9999-12-31T15:00:00Z"),
            START.plusNanos(1)))
      assertThrows(IllegalArgumentException.class, () -> new BackupWorkerRequest(RUN, wrong));
  }

  @Test
  void everyNullAndValueInvariant() {
    assertThrows(NullPointerException.class, () -> new BackupWorkerRequest(null, START));
    assertThrows(NullPointerException.class, () -> new BackupWorkerRequest(RUN, null));
    assertThrows(NullPointerException.class, () -> BackupWorkerRequest.consume(null));
    assertThrows(
        IllegalArgumentException.class, () -> new BackupWorkerRequest(new UUID(0, 0), START));
    refused(bytes(GOLDEN.replace(RUN.toString(), "00000000-0000-0000-0000-000000000000")));
  }

  @Test
  void missingExtraAndFixedFieldOrder() {
    for (String bad :
        List.of(
            "",
            GOLDEN + "extra\n",
            GOLDEN + "tail",
            GOLDEN.replace("NKBACKUP1", "NKBACKUP2"),
            GOLDEN.replace("run=", "path="),
            GOLDEN.replace("started=", "command="),
            GOLDEN.replace("\nstarted=", "\nrun=1\nstarted="),
            GOLDEN.substring(0, GOLDEN.length() - 1),
            "NKBACKUP1\nstarted=2026-09-27T14:59:59.123456Z\nrun=" + RUN + "\n"))
      refused(bytes(bad));
  }

  @Test
  void asciiAndBoundedBytes() {
    refused(new byte[161]);
    refused(new byte[0]);
    refused(new byte[160]);
    for (byte bad : new byte[] {0, 9, 13, 31, 127, (byte) 128}) {
      byte[] input = bytes(GOLDEN);
      input[0] = bad;
      refused(input);
    }
  }

  @Test
  void uuidAndTimestampNoncanonical() {
    for (String value : List.of("1-2-3-4-5", "AAAAAAAA-BBBB-4CCC-8DDD-EEEEEEEEEEEE", "not_uuid"))
      refused(bytes(GOLDEN.replace(RUN.toString(), value)));
    for (String value :
        List.of(
            "bad",
            "2026-09-27T14:59:59.123456+00:00",
            "2026-09-27T14:59:59.1234560Z",
            "2026-09-27T14:59:59.123456789Z",
            "+10000-01-01T00:00:00Z")) refused(bytes(GOLDEN.replace(START.toString(), value)));
  }

  @Test
  void ownedByteMutationDoesNotMutateRecord() {
    byte[] input = bytes(GOLDEN);
    var r = BackupWorkerRequest.consume(input);
    Arrays.fill(input, (byte) 65);
    assertEquals(RUN, r.run());
    assertEquals(START, r.started());
    byte[] encoded = r.encode();
    Arrays.fill(encoded, (byte) 65);
    assertArrayEquals(bytes(GOLDEN), r.encode());
  }

  @Test
  void concurrentIndependentConsumption() throws Exception {
    var executor = Executors.newFixedThreadPool(4);
    try {
      var tasks = new ArrayList<Future<Boolean>>();
      for (int n = 0; n < 32; n++)
        tasks.add(
            executor.submit(
                () -> {
                  byte[] input = bytes(GOLDEN);
                  assertEquals(
                      new BackupWorkerRequest(RUN, START), BackupWorkerRequest.consume(input));
                  assertArrayEquals(new byte[input.length], input);
                  return true;
                }));
      for (var result : tasks) assertTrue(result.get(5, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      if (!executor.awaitTermination(10, TimeUnit.SECONDS))
        throw new AssertionError("owned backup request workers did not terminate");
    }
  }
}
