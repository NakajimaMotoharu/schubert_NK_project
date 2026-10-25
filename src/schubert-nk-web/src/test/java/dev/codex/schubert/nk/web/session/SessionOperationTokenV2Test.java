package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
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
    var pending = new SessionOperationToken("QSBREQ01", ID, ISSUED);
    assertEquals(Optional.empty(), pending.completedAt());
    for (Instant completed : List.of(ISSUED, ISSUED.plusNanos(1), ISSUED.plusSeconds(1))) {
      var token = new SessionOperationToken("QSBREQ01", ID, ISSUED, Optional.of(completed));
      assertEquals("QSBREQ01", token.purpose());
      assertEquals(ID, token.token());
      assertEquals(ISSUED, token.issuedAt());
      assertEquals(Optional.of(completed), token.completedAt());
      assertEquals("SessionOperationToken[REDACTED]", token.toString());
    }
    assertThrows(
        IllegalArgumentException.class,
        () -> new SessionOperationToken("QSBREQ01", ID, ISSUED, Optional.of(ISSUED.minusNanos(1))));
    assertThrows(
        NullPointerException.class, () -> new SessionOperationToken("QSBREQ01", ID, ISSUED, null));
  }

  @Test
  void tokv202CurrentGoldenBytesAndCompletedTimes() {
    var codec = new SessionAttributeCodec();
    assertArrayEquals(
        bytes(PREFIX + "}]}"),
        codec.encode(attributes(new SessionOperationToken("QSBREQ01", ID, ISSUED))));
    for (String literal :
        List.of("2026-10-04T00:00:00Z", "2026-10-04T00:00:00.000001Z", "2026-10-05T00:00:00Z")) {
      String expected = PREFIX + ",\"completedAt\":\"" + literal + "\"}]}";
      var value =
          attributes(
              new SessionOperationToken(
                  "QSBREQ01", ID, ISSUED, Optional.of(Instant.parse(literal))));
      assertArrayEquals(bytes(expected), codec.encode(value));
      assertEquals(
          Optional.of(Instant.parse(literal)),
          codec.decode(bytes(expected)).operationTokens().getFirst().completedAt());
    }
  }

  @Test
  void tokv203LegacyAndReorderedRootVersionRemainStrict() {
    var codec = new SessionAttributeCodec();
    String legacy = PREFIX.replace("\"formatVersion\":2", "\"formatVersion\":1") + "}]}";
    var value = codec.decode(bytes(legacy));
    assertEquals(Optional.empty(), value.operationTokens().getFirst().completedAt());
    assertArrayEquals(bytes(PREFIX + "}]}"), codec.encode(value));
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
            "\"not-time\"")) invalid(PREFIX + ",\"completedAt\":" + value + "}]}");
    invalid(
        PREFIX
            + ",\"completedAt\":\"2026-10-04T00:00:00Z\",\"completedAt\":\"2026-10-04T00:00:01Z\"}]}");
    invalid(PREFIX + ",\"result\":\"0000\"}]}");
    invalid(
        PREFIX.replace(",\"issuedAt\":\"2026-10-04T00:00:00Z\"", "")
            + ",\"completedAt\":\"2026-10-04T00:00:00Z\"}]}");
    for (String version : List.of("0", "3", "2.0", "2e0", "\"2\"", "null"))
      invalid((PREFIX + "}]}").replace("\"formatVersion\":2", "\"formatVersion\":" + version));
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
              "QSBREQ01",
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
    invalid(golden.replace("]}", "," + PREFIX.substring(PREFIX.indexOf("[{") + 1) + "}]}"));
    tokens.add(new SessionOperationToken("QSBREQ01", new UUID(0, 11), ISSUED));
    assertThrows(
        IllegalArgumentException.class,
        () -> new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), tokens));
    try (var pool = Executors.newFixedThreadPool(10)) {
      var futures = new ArrayList<Future<Void>>();
      for (int n = 0; n < 100; n++)
        futures.add(
            pool.submit(
                () -> {
                  assertArrayEquals(bytes(golden), codec.encode(attributes));
                  assertEquals(10, codec.decode(bytes(golden)).operationTokens().size());
                  return null;
                }));
      for (var future : futures) future.get(20, TimeUnit.SECONDS);
    }
  }
}
