package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.view.ViewFixtureWorkers;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** QA049/PG-D356/UI226/SS314; TOKV201..205 independent literal v1/v2 oracle. */
class SessionOperationTokenV2Test {
  private static final String OPERATION_PURPOSE = "QSBREQ01";
  private static final String TOKEN_ARRAY_END = "}]}";

  static final Instant ISSUED = Instant.parse("2026-10-04T00:00:00Z");
  static final UUID ID = UUID.fromString("00000000-0000-4000-8000-000000000001");
  static final String PREFIX =
      "{\"formatVersion\":2,\"operationTokens\":[{\"purpose\":\"QSBREQ01\",\"token\":\"00000000-0000-4000-8000-000000000001\",\"issuedAt\":\"2026-10-04T00:00:00Z\"";

  static SessionAttributes attributes(SessionOperationToken... tokens) {
    return new SessionAttributes(
        Optional.empty(), Optional.empty(), Optional.empty(), List.of(tokens));
  }

  static byte[] bytes(String value) {
    return value.getBytes(StandardCharsets.UTF_8);
  }

  static void invalid(String input) {
    assertThrows(
        SessionAttributeException.class, () -> new SessionAttributeCodec().decode(bytes(input)));
  }

  @Test
  void tokv201CompletionInvariantAndLegacyConstructor() {
    var pending = new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED);
    assertEquals(Optional.empty(), pending.completedAt());
    for (Instant completed : List.of(ISSUED, ISSUED.plusNanos(1), ISSUED.plusSeconds(1))) {
      var token = new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED, Optional.of(completed));
      assertEquals(OPERATION_PURPOSE, token.purpose());
      assertEquals(ID, token.token());
      assertEquals(ISSUED, token.issuedAt());
      assertEquals(Optional.of(completed), token.completedAt());
      assertEquals("SessionOperationToken[REDACTED]", token.toString());
    }
    assertThrows(
        IllegalArgumentException.class,
        () ->
            new SessionOperationToken(
                OPERATION_PURPOSE, ID, ISSUED, Optional.of(ISSUED.minusNanos(1))));
    assertThrows(
        NullPointerException.class,
        () -> new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED, null));
  }

  /** PT-WEB-TOKVAL001. Equal values are interchangeable; completion remains part of the value. */
  @Test
  void tokenValuesDistinguishCompletionWhenReconstructed() {
    var pending = new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED);
    var equivalentPending =
        new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED, Optional.empty());
    var completedAt = Optional.of(ISSUED.plusSeconds(1));
    var completed = new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED, completedAt);

    var pendingValues = new HashSet<>(List.of(pending));
    assertTrue(pendingValues.contains(equivalentPending));
    assertFalse(pendingValues.contains(completed));
    var completedValues = new HashSet<>(List.of(completed));
    assertTrue(
        completedValues.contains(
            new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED, completedAt)));
    assertThrows(
        IllegalArgumentException.class, () -> new SessionOperationToken("UNKNOWN1", ID, ISSUED));
  }

  @Test
  void tokv202CurrentGoldenBytesAndCompletedTimes() {
    var codec = new SessionAttributeCodec();
    assertArrayEquals(
        bytes(PREFIX + TOKEN_ARRAY_END),
        codec.encode(attributes(new SessionOperationToken(OPERATION_PURPOSE, ID, ISSUED))));
    for (String literal :
        List.of("2026-10-04T00:00:00Z", "2026-10-04T00:00:00.000001Z", "2026-10-05T00:00:00Z")) {
      String expected = PREFIX + ",\"completedAt\":\"" + literal + "\"}]}";
      var value =
          attributes(
              new SessionOperationToken(
                  OPERATION_PURPOSE, ID, ISSUED, Optional.of(Instant.parse(literal))));
      assertArrayEquals(bytes(expected), codec.encode(value));
      assertEquals(
          Optional.of(Instant.parse(literal)),
          codec.decode(bytes(expected)).operationTokens().getFirst().completedAt());
    }
  }

  @Test
  void tokv203LegacyAndReorderedRootVersionRemainStrict() {
    var codec = new SessionAttributeCodec();
    String legacy = PREFIX.replace("\"formatVersion\":2", "\"formatVersion\":1") + TOKEN_ARRAY_END;
    var value = codec.decode(bytes(legacy));
    assertEquals(Optional.empty(), value.operationTokens().getFirst().completedAt());
    assertArrayEquals(bytes(PREFIX + TOKEN_ARRAY_END), codec.encode(value));
    String reversed =
        "{\"operationTokens\":[{\"completedAt\":\"2026-10-04T00:00:01Z\",\"issuedAt\":\"2026-10-04T00:00:00Z\",\"token\":\"00000000-0000-4000-8000-000000000001\",\"purpose\":\"QSBREQ01\"}],\"formatVersion\":2}";
    assertEquals(
        Optional.of(ISSUED.plusSeconds(1)),
        codec.decode(bytes(reversed)).operationTokens().getFirst().completedAt());
    invalid(reversed.replace("\"formatVersion\":2", "\"formatVersion\":1"));
    invalid(
        legacy.replace(
            "\"issuedAt\":\"2026-10-04T00:00:00Z\"",
            "\"issuedAt\":\"2026-10-04T00:00:00Z\",\"completedAt\":\"2026-10-04T00:00:00Z\""));
  }

  @Test
  void tokv204CompletedNullTypesUnknownDuplicateAndCanonicalBounds() {
    for (String value :
        List.of(
            "null",
            "1",
            "true",
            "{}",
            "[]",
            "\"2026-10-03T23:59:59.999999999Z\"",
            "\"2026-10-04T09:00:00+09:00\"",
            "\"2026-10-04T00:00:00.000Z\"",
            "\"not-time\"")) invalid(PREFIX + ",\"completedAt\":" + value + TOKEN_ARRAY_END);
    invalid(
        PREFIX
            + ",\"completedAt\":\"2026-10-04T00:00:00Z\",\"completedAt\":\"2026-10-04T00:00:01Z\"}]}");
    invalid(PREFIX + ",\"result\":\"0000\"}]}");
    invalid(
        PREFIX.replace(",\"issuedAt\":\"2026-10-04T00:00:00Z\"", "")
            + ",\"completedAt\":\"2026-10-04T00:00:00Z\"}]}");
    for (String version : List.of("0", "3", "2.0", "2e0", "\"2\"", "null"))
      invalid(
          (PREFIX + TOKEN_ARRAY_END)
              .replace("\"formatVersion\":2", "\"formatVersion\":" + version));
  }

  @Test
  void tokv205MixedCapacityAndConcurrentIndependentLiterals() throws Exception {
    var codec = new SessionAttributeCodec();
    var tokens = new ArrayList<SessionOperationToken>();
    var literals = new ArrayList<String>();
    for (int n = 1; n <= 10; n++) {
      UUID id = new UUID(0, n);
      boolean completed = n % 2 == 0;
      tokens.add(
          new SessionOperationToken(
              OPERATION_PURPOSE,
              id,
              ISSUED,
              completed ? Optional.of(ISSUED.plusSeconds(n)) : Optional.empty()));
      literals.add(
          "{\"purpose\":\"QSBREQ01\",\"token\":\""
              + String.format(Locale.ROOT, "00000000-0000-0000-0000-%012x", n)
              + "\",\"issuedAt\":\"2026-10-04T00:00:00Z\""
              + (completed
                  ? ",\"completedAt\":\"2026-10-04T00:00:"
                      + String.format(Locale.ROOT, "%02d", n)
                      + "Z\""
                  : "")
              + "}");
    }
    String golden =
        "{\"formatVersion\":2,\"operationTokens\":[" + String.join(",", literals) + "]}";
    var attributes =
        new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), tokens);
    assertArrayEquals(bytes(golden), codec.encode(attributes));
    assertEquals(tokens, codec.decode(bytes(golden)).operationTokens());
    invalid(
        golden.replace("]}", "," + PREFIX.substring(PREFIX.indexOf("[{") + 1) + TOKEN_ARRAY_END));
    tokens.add(new SessionOperationToken(OPERATION_PURPOSE, new UUID(0, 11), ISSUED));
    assertThrows(
        IllegalArgumentException.class,
        () -> new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), tokens));
    try (var workers = new ViewFixtureWorkers(Executors.newFixedThreadPool(10))) {
      var futures = new ArrayList<Future<Void>>();
      for (int n = 0; n < 100; n++)
        futures.add(
            workers.submit(
                () -> {
                  assertArrayEquals(bytes(golden), codec.encode(attributes));
                  assertEquals(10, codec.decode(bytes(golden)).operationTokens().size());
                  return null;
                }));
      for (var future : futures) future.get(20, TimeUnit.SECONDS);
    }
  }
}
