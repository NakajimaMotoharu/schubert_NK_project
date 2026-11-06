package dev.codex.schubert.nk.web.session;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Test;

/** FUN001/AUT/UI226/SS314331352/PT-WEB-SNAP001..008: immutable synthetic data, no auth/keys. */
final class WebSessionSnapshotPortTest {
  // Independent Python hashlib.sha256(ASCII('A' * 43)); never production-derived expected.
  private static final String HASH =
      "0f007385b6f9d4b7eeb2748605afe1a984a0a3bfa3f014d09e2a784ce9e5cd1a";
  private static final String FIXTURE_VERSION = "fixture-v1";
  private static final Instant AT = Instant.parse("2026-11-06T00:00:00Z");
  private static final SessionAttributes ANONYMOUS =
      new SessionAttributes(Optional.empty(), Optional.empty(), Optional.empty(), List.of());

  private static WebSessionId identity() {
    return WebSessionId.parse("A".repeat(43));
  }

  private static WebSessionRow row(String hash, long version) {
    return new WebSessionRow(
        new SessionPayloadIdentity(new UUID(0, version + 1), hash, AT),
        new EncryptedSessionPayload(FIXTURE_VERSION, new byte[29]),
        AT,
        AT.plusSeconds(1),
        1,
        version);
  }

  @Test
  void matchingIndependentHashRetainsInputObjects() throws Exception {
    var id = identity();
    var row = row(HASH, 0);
    var value = new WebSessionSnapshot(id, row, ANONYMOUS);
    assertSame(id, value.sessionId());
    assertSame(row, value.row());
    assertSame(ANONYMOUS, value.attributes());
    assertEquals(HASH, value.row().identity().sessionIdHash());
    assertEquals(0, value.row().version());
    assertEquals("WebSessionSnapshot[REDACTED]", value.toString());
    assertEquals(Optional.empty(), value.attributes().principal());
  }

  @Test
  void mismatchedIdentityRejectsWithFixedMessage() {
    var mismatch = row("f".repeat(64), 0);
    var failure =
        assertThrows(
            IllegalArgumentException.class,
            () -> new WebSessionSnapshot(identity(), mismatch, ANONYMOUS));
    assertEquals("session snapshot identity is inconsistent", failure.getMessage());
    assertEquals(null, failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  @Test
  void nullSessionIdentityRejects() {
    assertThrows(
        NullPointerException.class, () -> new WebSessionSnapshot(null, row(HASH, 0), ANONYMOUS));
  }

  @Test
  void nullRowRejects() {
    assertThrows(
        NullPointerException.class, () -> new WebSessionSnapshot(identity(), null, ANONYMOUS));
  }

  @Test
  void nullAttributesReject() {
    assertThrows(
        NullPointerException.class, () -> new WebSessionSnapshot(identity(), row(HASH, 0), null));
  }

  @Test
  void expiredRowRemainsDataWithoutAuthenticationGrant() throws Exception {
    var row =
        new WebSessionRow(
            new SessionPayloadIdentity(new UUID(0, 1), HASH, AT.minusSeconds(120)),
            new EncryptedSessionPayload(FIXTURE_VERSION, new byte[29]),
            AT.minusSeconds(60),
            AT.minusSeconds(1),
            28800,
            999_999_999);
    var value = new WebSessionSnapshot(identity(), row, ANONYMOUS);
    assertEquals(AT.minusSeconds(1), value.row().expiresAt());
    assertTrue(value.row().expiresAt().isBefore(AT));
    assertEquals(28800, value.row().maxInactiveSeconds());
    assertEquals(999_999_999, value.row().version());
    assertTrue(value.attributes().principal().isEmpty());
    assertTrue(value.attributes().csrfToken().isEmpty());
    assertTrue(value.attributes().operationTokens().isEmpty());
  }

  @Test
  void retainedPayloadKeepsDefensiveByteOwnership() throws Exception {
    byte[] supplied = new byte[29];
    var payload = new EncryptedSessionPayload(FIXTURE_VERSION, supplied);
    var row =
        new WebSessionRow(
            new SessionPayloadIdentity(new UUID(0, 1), HASH, AT),
            payload,
            AT,
            AT.plusSeconds(1),
            1,
            0);
    var value = new WebSessionSnapshot(identity(), row, ANONYMOUS);
    Arrays.fill(supplied, (byte) 7);
    byte[] returned = value.row().payload().ciphertext();
    Arrays.fill(returned, (byte) 8);
    assertArrayEquals(new byte[29], value.row().payload().ciphertext());
    assertEquals(FIXTURE_VERSION, value.row().payload().keyVersion());
    assertEquals("WebSessionSnapshot[REDACTED]", value.toString());
  }

  @Test
  void parallelSnapshotsKeepDistinctRows() throws Exception {
    try (var workers = Executors.newFixedThreadPool(2)) {
      var pending = new ArrayList<Future<WebSessionSnapshot>>();
      for (int i = 0; i < 8; i++) {
        long version = i;
        pending.add(
            workers.submit(
                () -> new WebSessionSnapshot(identity(), row(HASH, version), ANONYMOUS)));
      }
      for (int i = 0; i < 8; i++) {
        var value = pending.get(i).get(10, TimeUnit.SECONDS);
        assertEquals(i, value.row().version());
        assertEquals(new UUID(0, i + 1), value.row().identity().id());
        assertEquals(HASH, value.row().identity().sessionIdHash());
        assertSame(ANONYMOUS, value.attributes());
      }
    }
  }
}
