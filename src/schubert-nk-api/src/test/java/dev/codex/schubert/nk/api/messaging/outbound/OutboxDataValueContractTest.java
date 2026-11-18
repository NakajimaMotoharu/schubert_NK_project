package dev.codex.schubert.nk.api.messaging.outbound;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** PT-OUTBOX-DATA001..003; SS312/321/324/331/354: inert data, no actual claim/lease/JMS/DB. */
final class OutboxDataValueContractTest {
  private static final UUID MESSAGE = new UUID(0, 1);
  private static final UUID CORRELATION = new UUID(0, 2);
  private static final String FATAL_CODE = "CODE_A";
  private static final String UNKNOWN = "unknown";
  private static final String LAYOUT = "QWKREQ01";
  private static final String VERSION = "001";
  private static final String LEASE_OWNER = "worker";
  private static final String TRANSPORT = "ID:synthetic";
  private static final String ERROR = "QUESTION_RETRY_EXHAUSTED";
  private static final Instant CREATED = Instant.EPOCH;
  private static final Instant NEXT = Instant.parse("1970-01-01T00:00:01Z");
  private static final Instant UNTIL = Instant.parse("1970-01-01T00:00:10Z");

  @Test
  void data001RowAndRequestConstructorsKeepBodyOwnershipGettersAndEveryBoundedNonnullInput() {
    byte[] body = new byte[320];
    OutboxRequest request =
        new OutboxRequest(
            MESSAGE,
            CORRELATION,
            OutboxDestination.ASYNC_WORK,
            LAYOUT,
            VERSION,
            body,
            NEXT,
            CREATED);
    body[0] = 99;
    byte[] exported = request.body();
    exported[1] = 88;
    assertArrayEquals(new byte[320], request.body());
    assertEquals(MESSAGE, request.messageId());
    assertEquals(CORRELATION, request.correlationId());
    assertSame(OutboxDestination.ASYNC_WORK, request.destination());
    assertEquals(LAYOUT, request.layoutId());
    assertEquals(VERSION, request.layoutVersion());
    assertEquals(NEXT, request.nextAttemptAt());
    assertEquals(CREATED, request.createdAt());
    assertEquals(Optional.empty(), request.dlqMetadata());
    assertEquals("OutboxRequest[<redacted>]", request.toString());
    for (long id : new long[] {1, 999_999_999_999L}) {
      for (int attempts : new int[] {0, 100}) {
        for (String owner : List.of(LEASE_OWNER, "x".repeat(64))) {
          byte[] input = new byte[320];
          OutboxEntry entry = entry(id, attempts, LAYOUT, VERSION, input, owner);
          input[0] = 99;
          byte[] view = entry.body();
          view[1] = 88;
          assertArrayEquals(new byte[320], entry.body());
          assertEquals(id, entry.id());
          assertEquals(MESSAGE, entry.messageId());
          assertEquals(CORRELATION, entry.correlationId());
          assertSame(OutboxDestination.ASYNC_WORK, entry.destination());
          assertEquals(LAYOUT, entry.layoutId());
          assertEquals(VERSION, entry.layoutVersion());
          assertEquals(attempts, entry.attemptCount());
          assertEquals(NEXT, entry.nextAttemptAt());
          assertEquals(CREATED, entry.createdAt());
          assertEquals(owner, entry.leaseOwner());
          assertEquals(UNTIL, entry.leaseUntil());
          assertEquals(Optional.empty(), entry.dlqMetadata());
          assertEquals("OutboxEntry[<redacted>]", entry.toString());
        }
      }
    }
    for (long invalid : new long[] {Long.MIN_VALUE, -1, 0, 1_000_000_000_000L, Long.MAX_VALUE}) {
      assertThrows(
          IllegalArgumentException.class,
          () -> entry(invalid, 0, LAYOUT, VERSION, new byte[320], LEASE_OWNER));
    }
    for (int invalid : new int[] {Integer.MIN_VALUE, -1, 101, Integer.MAX_VALUE}) {
      assertThrows(
          IllegalArgumentException.class,
          () -> entry(1, invalid, LAYOUT, VERSION, new byte[320], LEASE_OWNER));
    }
    for (String invalid : List.of("", " \t", "x".repeat(65))) {
      assertThrows(
          IllegalArgumentException.class,
          () -> entry(1, 0, LAYOUT, VERSION, new byte[320], invalid));
    }
    for (String invalid : List.of("", "QWKREQ0", "QWKREQ011", "qwkreq01", "QWKREQ0_")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> entry(1, 0, invalid, VERSION, new byte[320], LEASE_OWNER));
      assertThrows(
          IllegalArgumentException.class,
          () ->
              new OutboxRequest(
                  MESSAGE,
                  CORRELATION,
                  OutboxDestination.ASYNC_WORK,
                  invalid,
                  VERSION,
                  new byte[320],
                  NEXT,
                  CREATED));
    }
    for (String invalid : List.of("", "01", "0000", "a01")) {
      assertThrows(
          IllegalArgumentException.class,
          () -> entry(1, 0, LAYOUT, invalid, new byte[320], LEASE_OWNER));
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> entry(1, 0, LAYOUT, VERSION, new byte[0], LEASE_OWNER));
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new OutboxRequest(
                MESSAGE,
                CORRELATION,
                OutboxDestination.ASYNC_WORK,
                LAYOUT,
                VERSION,
                new byte[0],
                NEXT,
                CREATED));
    for (int index = 0; index < 9; index++) {
      int absent = index;
      assertThrows(
          NullPointerException.class,
          () ->
              new OutboxRequest(
                  absent == 0 ? null : MESSAGE,
                  absent == 1 ? null : CORRELATION,
                  absent == 2 ? null : OutboxDestination.ASYNC_WORK,
                  absent == 3 ? null : LAYOUT,
                  absent == 4 ? null : VERSION,
                  absent == 5 ? null : new byte[320],
                  absent == 6 ? null : NEXT,
                  absent == 7 ? null : CREATED,
                  absent == 8 ? null : Optional.empty()));
    }
    for (int index = 0; index < 11; index++) {
      int absent = index;
      assertThrows(
          NullPointerException.class,
          () ->
              new OutboxEntry(
                  1,
                  absent == 0 ? null : MESSAGE,
                  absent == 1 ? null : CORRELATION,
                  absent == 2 ? null : OutboxDestination.ASYNC_WORK,
                  absent == 3 ? null : LAYOUT,
                  absent == 4 ? null : VERSION,
                  absent == 5 ? null : new byte[320],
                  0,
                  absent == 6 ? null : NEXT,
                  absent == 7 ? null : CREATED,
                  absent == 8 ? null : LEASE_OWNER,
                  absent == 9 ? null : UNTIL,
                  absent == 10 ? null : Optional.empty()));
    }
  }

  @Test
  void data002DlqAndFatalMetadataRecordComponentsRemainExplicitWithoutProviderDiagnostics() {
    OutboxDlqMetadata value = new OutboxDlqMetadata(MESSAGE, TRANSPORT, 1, ERROR, CREATED);
    sameValue(
        value,
        new OutboxDlqMetadata(MESSAGE, TRANSPORT, 1, ERROR, CREATED),
        List.of(
            new OutboxDlqMetadata(CORRELATION, TRANSPORT, 1, ERROR, CREATED),
            new OutboxDlqMetadata(MESSAGE, "ID:other", 1, ERROR, CREATED),
            new OutboxDlqMetadata(MESSAGE, TRANSPORT, 2, ERROR, CREATED),
            new OutboxDlqMetadata(MESSAGE, TRANSPORT, 1, ERROR, NEXT)));
    assertEquals("OutboxDlqMetadata[<redacted>]", value.toString());
    FatalDlqMetadata fatal =
        new FatalDlqMetadata(FATAL_CODE, FatalDlqMetadata.DetectedBy.API_SYNC, CREATED);
    assertEquals(FATAL_CODE, fatal.errorCode());
    assertSame(FatalDlqMetadata.DetectedBy.API_SYNC, fatal.detectedBy());
    assertEquals(CREATED, fatal.detectedAt());
    assertEquals(
        "FatalDlqMetadata[errorCode=CODE_A, detectedBy=API_SYNC, detectedAt=1970-01-01T00:00:00Z]",
        fatal.toString());
    sameValue(
        fatal,
        new FatalDlqMetadata(FATAL_CODE, FatalDlqMetadata.DetectedBy.API_SYNC, CREATED),
        List.of(
            new FatalDlqMetadata("CODE_B", FatalDlqMetadata.DetectedBy.API_SYNC, CREATED),
            new FatalDlqMetadata(FATAL_CODE, FatalDlqMetadata.DetectedBy.API_WORK, CREATED),
            new FatalDlqMetadata(FATAL_CODE, FatalDlqMetadata.DetectedBy.API_SYNC, NEXT)));
    for (String code : List.of("A", "A0_", "A".repeat(32))) {
      assertEquals(
          code,
          new FatalDlqMetadata(code, FatalDlqMetadata.DetectedBy.API_SYNC, CREATED).errorCode());
    }
    for (String invalid : List.of("", "lower", "0CODE", "_CODE", "A".repeat(33), "A\n", "A-")) {
      assertEquals(
          "DLQ error code is invalid",
          assertThrows(
                  IllegalArgumentException.class,
                  () ->
                      new FatalDlqMetadata(invalid, FatalDlqMetadata.DetectedBy.API_SYNC, CREATED))
              .getMessage());
    }
    assertThrows(
        NullPointerException.class,
        () -> new FatalDlqMetadata(null, FatalDlqMetadata.DetectedBy.API_SYNC, CREATED));
    assertThrows(NullPointerException.class, () -> new FatalDlqMetadata(FATAL_CODE, null, CREATED));
    assertThrows(
        NullPointerException.class,
        () -> new FatalDlqMetadata(FATAL_CODE, FatalDlqMetadata.DetectedBy.API_SYNC, null));
  }

  @Test
  void data003TwoDestinationsAndFourDetectionSitesKeepFixedFactoriesAndDefensiveValueArrays() {
    String[] names = {"ASYNC_WORK", "DLQ"};
    String[] addresses = {"nk.async.work", "nk.dead.letter"};
    OutboxDestination[] destinations = OutboxDestination.values();
    assertArrayEquals(names, Arrays.stream(destinations).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < names.length; i++) {
      assertEquals(i, destinations[i].ordinal());
      assertEquals(addresses[i], destinations[i].address());
      assertSame(destinations[i], OutboxDestination.valueOf(names[i]));
      assertSame(destinations[i], OutboxDestination.fromAddress(addresses[i]));
    }
    OutboxDestination[] destinationsCopy = OutboxDestination.values();
    assertNotSame(destinations, destinationsCopy);
    destinationsCopy[0] = null;
    assertSame(OutboxDestination.ASYNC_WORK, OutboxDestination.values()[0]);
    assertThrows(NullPointerException.class, () -> OutboxDestination.fromAddress(null));
    assertThrows(IllegalArgumentException.class, () -> OutboxDestination.fromAddress(UNKNOWN));
    assertThrows(IllegalArgumentException.class, () -> OutboxDestination.valueOf(UNKNOWN));
    assertThrows(NullPointerException.class, () -> OutboxDestination.valueOf(null));
    String[] sites = {"API_SYNC", "API_WORK", "API_WEB_LOG", "WEB_REPLY"};
    FatalDlqMetadata.DetectedBy[] detected = FatalDlqMetadata.DetectedBy.values();
    assertArrayEquals(sites, Arrays.stream(detected).map(Enum::name).toArray(String[]::new));
    for (int i = 0; i < sites.length; i++) {
      assertEquals(i, detected[i].ordinal());
      assertSame(detected[i], FatalDlqMetadata.DetectedBy.valueOf(sites[i]));
    }
    FatalDlqMetadata.DetectedBy[] detectedCopy = FatalDlqMetadata.DetectedBy.values();
    assertNotSame(detected, detectedCopy);
    detectedCopy[0] = null;
    assertSame(FatalDlqMetadata.DetectedBy.API_SYNC, FatalDlqMetadata.DetectedBy.values()[0]);
    assertThrows(
        IllegalArgumentException.class, () -> FatalDlqMetadata.DetectedBy.valueOf(UNKNOWN));
    assertThrows(NullPointerException.class, () -> FatalDlqMetadata.DetectedBy.valueOf(null));
  }

  private static OutboxEntry entry(
      long id, int count, String layout, String version, byte[] body, String owner) {
    return new OutboxEntry(
        id,
        MESSAGE,
        CORRELATION,
        OutboxDestination.ASYNC_WORK,
        layout,
        version,
        body,
        count,
        NEXT,
        CREATED,
        owner,
        UNTIL);
  }

  private static <T> void sameValue(T value, T equal, List<T> different) {
    assertEquals(value, value);
    assertEquals(value, equal);
    assertEquals(equal, value);
    assertEquals(value.hashCode(), equal.hashCode());
    assertEquals("found", Map.of(value, "found").get(equal));
    assertNotEquals(value, null);
    assertNotEquals(value, VERSION);
    for (T other : different) {
      assertNotEquals(value, other);
      assertNotEquals(other, value);
    }
  }
}
