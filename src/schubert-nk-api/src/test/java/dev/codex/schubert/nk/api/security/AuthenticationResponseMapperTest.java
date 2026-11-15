package dev.codex.schubert.nk.api.security;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.api.domain.Role;
import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.header.ResultCode;
import dev.codex.schubert.nk.protocol.layout.FixedPayload;
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
import org.junit.jupiter.api.Timeout;

/**
 * PT-AUT-WIRE-001..003. Golden bytes come from UI234 offsets/literals, never production encoders.
 */
@Timeout(value = 30, threadMode = Timeout.ThreadMode.SEPARATE_THREAD)
final class AuthenticationResponseMapperTest {
  private final AuthenticationResponseMapper mapper = new AuthenticationResponseMapper();
  private static final Instant AT = Instant.parse("2026-09-08T01:02:03.456789Z");
  private static final Instant EXPIRY = Instant.parse("2026-09-08T09:02:03.456789Z");
  private static final AuthContextIdentity IDENTITY = new AuthContextIdentity(new UUID(0, 1), 7);
  private static final AuthenticationContext RAW = AuthenticationContext.of("a".repeat(64));

  @Test
  void loginSuccessMatchesIndependentUserAndAdminByteVectors() {
    for (Role role : Role.values()) {
      var result =
          new LoginResult.Success(
              new AuthenticatedActor(7, "利用者", role), new IssuedContext(IDENTITY, RAW, AT, EXPIRY));
      byte[] expected = loginBlank();
      put(expected, 0, "利用者");
      put(expected, 64, role == Role.ADMIN ? "ADMIN" : "USER");
      put(expected, 69, "a".repeat(64));
      put(expected, 133, "20260908100203456");
      put(expected, 150, "20260908180203456");
      assertPayload(expected, mapper.login(result));
    }
  }

  @Test
  void failuresLocksAndInfrastructureNeverExposeIdentity() {
    byte[] failure = loginBlank();
    put(failure, 176, "ユーザー名またはパスワードが正しくありません。");
    assertPayload(
        failure, mapper.login(new LoginResult.Failure(ResultCode.AUTHENTICATION_FAILED, 0)));
    for (int retry : new int[] {1, 900}) {
      byte[] expected = loginBlank();
      put(expected, 167, retry == 1 ? "000001" : "000900");
      put(expected, 176, "ログイン試行回数が上限に達しました。15分ほど待ってから再度お試しください。");
      assertPayload(expected, mapper.login(new LoginResult.Failure(ResultCode.LOCKED, retry)));
    }
    byte[] unavailable = loginBlank();
    put(unavailable, 176, "現在処理できません。しばらくしてから再操作してください。");
    assertPayload(unavailable, mapper.temporaryLoginFailure());
  }

  @Test
  void logoutNullAndBoundaryResultsPreserveTheOriginalInstant() throws Exception {
    byte[] expected = "20260908100203456       ".getBytes(StandardCharsets.US_ASCII);
    for (ResultCode code : List.of(ResultCode.SUCCESS, ResultCode.IDEMPOTENT_SUCCESS))
      assertPayload(expected, mapper.logout(new RevokedContext(IDENTITY, AT, code)));
    for (var boundary :
        java.util.Map.of(
                "2026-09-08T01:02:03.999999Z", "20260908100203999",
                "2026-09-08T01:02:04.000000Z", "20260908100204000",
                "2026-09-08T01:02:04.000001Z", "20260908100204000")
            .entrySet()) {
      var result =
          new RevokedContext(IDENTITY, Instant.parse(boundary.getKey()), ResultCode.SUCCESS);
      assertPayload(
          (boundary.getValue() + "       ").getBytes(StandardCharsets.US_ASCII),
          mapper.logout(result));
      assertEquals(Instant.parse(boundary.getKey()), result.revokedAt());
    }
    assertThrows(NullPointerException.class, () -> mapper.login(null));
    assertThrows(NullPointerException.class, () -> mapper.logout(null));
    var executor = Executors.newFixedThreadPool(16);
    try {
      var futures = new ArrayList<Future<FixedPayload>>();
      for (int i = 0; i < 100; i++)
        futures.add(
            executor.submit(
                () ->
                    mapper.logout(
                        new RevokedContext(IDENTITY, AT, ResultCode.IDEMPOTENT_SUCCESS))));
      for (var future : futures) assertPayload(expected, future.get(5, TimeUnit.SECONDS));
    } finally {
      executor.shutdownNow();
      org.junit.jupiter.api.Assertions.assertTrue(executor.awaitTermination(10, TimeUnit.SECONDS));
    }
  }

  private static byte[] loginBlank() {
    byte[] bytes = new byte[432];
    Arrays.fill(bytes, (byte) ' ');
    put(bytes, 167, "000000000");
    return bytes;
  }

  private static void put(byte[] target, int offset, String text) {
    byte[] bytes = text.getBytes(StandardCharsets.UTF_8);
    System.arraycopy(bytes, 0, target, offset, bytes.length);
  }

  private static void assertPayload(byte[] expected, FixedPayload actual) {
    assertEquals(expected.length, actual.dataLength());
    assertEquals(0, actual.recordCount());
    assertEquals(0, actual.recordLength());
    assertArrayEquals(expected, actual.copyData());
  }
}
