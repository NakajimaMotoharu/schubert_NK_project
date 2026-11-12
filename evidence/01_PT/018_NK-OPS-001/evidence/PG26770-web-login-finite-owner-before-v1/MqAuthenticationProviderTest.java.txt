package dev.codex.schubert.nk.web.security;

import static dev.codex.schubert.nk.web.security.MqLoginClientTest.error;
import static dev.codex.schubert.nk.web.security.MqLoginClientTest.put;
import static dev.codex.schubert.nk.web.security.MqLoginClientTest.success;
import static dev.codex.schubert.nk.web.security.MqLoginContextProbeTest.CLOCK;
import static dev.codex.schubert.nk.web.security.MqLoginContextProbeTest.WAIT;
import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import jakarta.jms.JMSException;
import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.AuthenticationServiceException;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.TestingAuthenticationToken;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

/** Actual Spring authentication types with independent wire senders; SSC-043/PT-WEB-063..067. */
final class MqAuthenticationProviderTest {
  private static final String FIXTURE_USER_2DED8884 = "USER";
  private static final String FIXTURE_ADMIN_C4BB3010 = "ADMIN";
  private static final String FIXTURE_0000_876EEFE0 = "0000";
  private static final String FIXTURE_ALICE_1EA1F9A4 = "Alice";
  private static final String FIXTURE_0200_FC9DB3AC = "0200";
  private static final String FIXTURE_JMS_1AEA59D9 = "JMS";
  private static final String FIXTURE_LOGIN_SERVICE_IS_UNAVAILABLE_7A0A73D7 =
      "login service is unavailable";

  @Test
  void web063DetailsAndLockDelayAreBoundedAndRedacted() {
    String longest = "ffff:ffff:ffff:ffff:ffff:ffff:255.255.255.255";
    assertEquals(45, longest.length());
    for (String address : List.of("127.0.0.1", "::1", "2001:db8::1", longest)) {
      var details = new LoginClientAddress(address);
      assertEquals(address, details.value());
      assertEquals("LoginClientAddress[REDACTED]", details.toString());
    }
    assertThrows(NullPointerException.class, () -> new LoginClientAddress(null));
    for (String address :
        List.of(
            "",
            "localhost",
            "invalid.example",
            "1.1.1.999",
            "::xyz",
            "fe80::1%1",
            "[" + longest + "]")) {
      var failure =
          assertThrows(IllegalArgumentException.class, () -> new LoginClientAddress(address));
      assertEquals("login client address is invalid", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    for (int delay : new int[] {0, 900}) {
      var failure = new MqLoginLockedException(delay);
      assertEquals(delay, failure.retryAfterSeconds());
      assertEquals("login temporarily locked", failure.getMessage());
      assertNull(failure.getCause());
      assertEquals(0, failure.getSuppressed().length);
    }
    for (int delay : new int[] {-1, 901})
      assertThrows(IllegalArgumentException.class, () -> new MqLoginLockedException(delay));
  }

  @Test
  void web064FreshAuthenticationConsumesCredentialsAndUsesApiRole() {
    for (String role : List.of(FIXTURE_USER_2DED8884, FIXTURE_ADMIN_C4BB3010)) {
      var fixture = new Fixture(FIXTURE_0000_876EEFE0, role, FIXTURE_0000_876EEFE0, CLOCK);
      char[] password = "e\u0301".toCharArray();
      var input = input(" Alice ", password);
      Authentication result = fixture.provider.authenticate(input);
      assertTrue(result.isAuthenticated());
      assertNull(result.getCredentials());
      assertNull(result.getDetails());
      assertEquals(FIXTURE_ALICE_1EA1F9A4, result.getName());
      assertEquals(
          List.of("ROLE_" + role),
          result.getAuthorities().stream().map(a -> a.getAuthority()).toList());
      SessionPrincipal principal = assertInstanceOf(SessionPrincipal.class, result.getPrincipal());
      assertEquals(FIXTURE_ALICE_1EA1F9A4, principal.username());
      assertEquals(FIXTURE_ALICE_1EA1F9A4, principal.getName());
      assertEquals(UserRole.valueOf(role), principal.role());
      assertEquals("a".repeat(64), principal.authenticationContext().wireValue());
      assertEquals(Instant.parse("2026-09-08T00:00:00.123Z"), principal.loginAt());
      assertFalse(result.toString().contains("a".repeat(64)));
      assertFalse(result.toString().contains("é"));
      assertArrayEquals(new char[password.length], password);
      assertNull(input.getCredentials());
      assertFalse(input.isAuthenticated());
      assertEquals(1, fixture.logins.get());
      assertEquals(0, fixture.probes.get());
      fixture.closed();
    }
  }

  @Test
  void web065ReplayRequiresCurrentContextBeforeGrant() {
    // Old immutable expiry has passed, but API idle may have extended; current probe is
    // authoritative.
    Clock later = Clock.fixed(Instant.parse("2026-09-09T00:00:00Z"), ZoneOffset.UTC);
    for (String code : List.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC)) {
      var fixture = new Fixture(FIXTURE_0200_FC9DB3AC, FIXTURE_ADMIN_C4BB3010, code, later);
      char[] secret = {'p'};
      var input = input(FIXTURE_ALICE_1EA1F9A4, secret);
      var result = fixture.provider.authenticate(input);
      assertTrue(result.isAuthenticated());
      SessionPrincipal principal = assertInstanceOf(SessionPrincipal.class, result.getPrincipal());
      assertEquals(UserRole.ADMIN, principal.role());
      assertEquals(Instant.parse("2026-09-08T00:00:00.123Z"), principal.loginAt());
      assertEquals(
          List.of("ROLE_ADMIN"),
          result.getAuthorities().stream().map(a -> a.getAuthority()).toList());
      assertArrayEquals(new char[1], secret);
      assertNull(input.getCredentials());
      assertEquals(1, fixture.logins.get());
      assertEquals(1, fixture.probes.get());
      assertEquals(2, fixture.ids.get());
      fixture.closed();
    }
    for (String code : List.of("0102", "9000", "MALFORMED", FIXTURE_JMS_1AEA59D9)) {
      var fixture = new Fixture(FIXTURE_0200_FC9DB3AC, FIXTURE_ADMIN_C4BB3010, code, later);
      var input = input(FIXTURE_ALICE_1EA1F9A4, new char[] {'p'});
      if (code.equals("0102"))
        fixed(
            assertThrows(BadCredentialsException.class, () -> fixture.provider.authenticate(input)),
            "login authentication failed");
      else
        fixed(
            assertThrows(
                AuthenticationServiceException.class, () -> fixture.provider.authenticate(input)),
            FIXTURE_LOGIN_SERVICE_IS_UNAVAILABLE_7A0A73D7);
      assertNull(input.getCredentials());
      assertEquals(1, fixture.logins.get());
      assertEquals(1, fixture.probes.get());
      fixture.closed();
    }
  }

  @Test
  void web066FailureAndNullTypesNeverBecomeAuthentication() {
    var base =
        new Fixture(FIXTURE_0000_876EEFE0, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, CLOCK);
    assertThrows(NullPointerException.class, () -> new MqAuthenticationProvider(null, base.probe));
    assertThrows(NullPointerException.class, () -> new MqAuthenticationProvider(base.login, null));
    assertThrows(NullPointerException.class, () -> base.provider.authenticate(null));
    assertThrows(NullPointerException.class, () -> base.provider.supports(null));
    assertTrue(base.provider.supports(UsernamePasswordAuthenticationToken.class));
    assertFalse(base.provider.supports(TestingAuthenticationToken.class));
    assertFalse(base.provider.supports(DerivedToken.class));
    List<UsernamePasswordAuthenticationToken> invalid = new ArrayList<>();
    invalid.add(input(123, new char[] {'p'}));
    invalid.add(input(null, new char[] {'p'}));
    invalid.add(input(FIXTURE_ALICE_1EA1F9A4, null));
    invalid.add(input(FIXTURE_ALICE_1EA1F9A4, "synthetic-password-string"));
    var noDetails = input(FIXTURE_ALICE_1EA1F9A4, new char[] {'p'});
    noDetails.setDetails(null);
    invalid.add(noDetails);
    var wrongDetails = input(FIXTURE_ALICE_1EA1F9A4, new char[] {'p'});
    wrongDetails.setDetails("untrusted-XFF");
    invalid.add(wrongDetails);
    invalid.add(
        UsernamePasswordAuthenticationToken.authenticated(
            FIXTURE_ALICE_1EA1F9A4,
            new char[] {'p'},
            List.of(new SimpleGrantedAuthority("ROLE_ADMIN"))));
    invalid.add(new DerivedToken(FIXTURE_ALICE_1EA1F9A4, new char[] {'p'}));
    for (var input : invalid) {
      Object supplied = input.getCredentials();
      fixed(
          assertThrows(
              AuthenticationServiceException.class, () -> base.provider.authenticate(input)),
          FIXTURE_LOGIN_SERVICE_IS_UNAVAILABLE_7A0A73D7);
      assertNull(input.getCredentials());
      if (supplied instanceof char[] chars) assertArrayEquals(new char[chars.length], chars);
    }
    char[] unsupportedSecret = {'p'};
    var unsupported = new TestingAuthenticationToken(FIXTURE_ALICE_1EA1F9A4, unsupportedSecret);
    fixed(
        assertThrows(
            AuthenticationServiceException.class, () -> base.provider.authenticate(unsupported)),
        FIXTURE_LOGIN_SERVICE_IS_UNAVAILABLE_7A0A73D7);
    assertArrayEquals(new char[1], unsupportedSecret);
    assertEquals(0, base.logins.get());
    assertEquals(0, base.probes.get());
    base.closed();
    for (String code : List.of("0101", "0106", "9000", FIXTURE_JMS_1AEA59D9)) {
      var fixture = new Fixture(code, FIXTURE_USER_2DED8884, FIXTURE_0000_876EEFE0, CLOCK);
      char[] password = {'p'};
      var input = input(FIXTURE_ALICE_1EA1F9A4, password);
      switch (code) {
        case "0101" ->
            fixed(
                assertThrows(
                    BadCredentialsException.class, () -> fixture.provider.authenticate(input)),
                "login authentication failed");
        case "0106" -> {
          var failure =
              assertThrows(
                  MqLoginLockedException.class, () -> fixture.provider.authenticate(input));
          fixed(failure, "login temporarily locked");
          assertEquals(900, failure.retryAfterSeconds());
        }
        default ->
            fixed(
                assertThrows(
                    AuthenticationServiceException.class,
                    () -> fixture.provider.authenticate(input)),
                FIXTURE_LOGIN_SERVICE_IS_UNAVAILABLE_7A0A73D7);
      }
      assertArrayEquals(new char[1], password);
      assertNull(input.getCredentials());
      assertEquals(1, fixture.logins.get());
      assertEquals(0, fixture.probes.get());
      fixture.closed();
    }
    var invalidInput = input("", new char[] {'p'});
    fixed(
        assertThrows(BadCredentialsException.class, () -> base.provider.authenticate(invalidInput)),
        "login authentication failed");
    assertNull(invalidInput.getCredentials());
    assertEquals(0, base.logins.get());
  }

  @Test
  void web067ConcurrentProvidersNeverCrossCredentialsOrPrincipals() throws Exception {
    var fixture =
        new Fixture(FIXTURE_0200_FC9DB3AC, FIXTURE_ADMIN_C4BB3010, FIXTURE_0000_876EEFE0, CLOCK);
    try (var workers = Executors.newFixedThreadPool(8)) {
      List<Future<?>> results = new ArrayList<>();
      synchronized (fixture.provider) {
        for (int i = 0; i < 100; i++) {
          int ordinal = i;
          String name = "user" + i;
          results.add(
              workers.submit(
                  () -> {
                    char[] password = ("password-" + name).toCharArray();
                    var input = input(name, password);
                    var result = fixture.provider.authenticate(input);
                    assertTrue(result.isAuthenticated());
                    SessionPrincipal principal =
                        assertInstanceOf(SessionPrincipal.class, result.getPrincipal());
                    assertEquals(name, principal.username());
                    assertEquals(name, result.getName());
                    assertEquals(
                        ordinal % 2 == 0 ? UserRole.USER : UserRole.ADMIN, principal.role());
                    assertEquals(
                        String.format(java.util.Locale.ROOT, "%064x", ordinal),
                        principal.authenticationContext().wireValue());
                    assertArrayEquals(new char[password.length], password);
                    assertNull(input.getCredentials());
                    assertNull(result.getCredentials());
                  }));
        }
        for (var result : results) result.get(10, TimeUnit.SECONDS);
      }
    }
    assertEquals(100, fixture.logins.get());
    assertEquals(100, fixture.probes.get());
    assertEquals(200, fixture.ids.get());
    fixture.closed();
  }

  private static UsernamePasswordAuthenticationToken input(Object username, Object password) {
    var input = UsernamePasswordAuthenticationToken.unauthenticated(username, password);
    input.setDetails(new LoginClientAddress("::1"));
    return input;
  }

  private static void fixed(RuntimeException failure, String message) {
    assertEquals(message, failure.getMessage());
    assertNull(failure.getCause());
    assertEquals(0, failure.getSuppressed().length);
  }

  private static final class DerivedToken extends UsernamePasswordAuthenticationToken {
    private static final long serialVersionUID = 1L;

    DerivedToken(String username, char[] password) {
      super(username, password);
    }
  }

  private static final class Fixture {
    final AtomicInteger ids = new AtomicInteger();
    final AtomicInteger logins = new AtomicInteger();
    final AtomicInteger probes = new AtomicInteger();
    final java.util.Set<String> issued = java.util.concurrent.ConcurrentHashMap.newKeySet();
    final List<byte[]> buffers = java.util.Collections.synchronizedList(new ArrayList<>());
    final JmsRequestReplyClient client;
    final MqLoginClient login;
    final MqLoginContextProbe probe;
    final MqAuthenticationProvider provider;

    Fixture(String loginCode, String role, String probeCode, Clock clock) {
      client = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 12);
      login =
          new MqLoginClient(
              client,
              (id, body) -> {
                logins.incrementAndGet();
                buffers.add(body);
                assertEquals("LGNREQ01", new String(body, 11, 8, StandardCharsets.US_ASCII));
                assertEquals(id.toString(), new String(body, 60, 36, StandardCharsets.US_ASCII));
                if (loginCode.equals(FIXTURE_JMS_1AEA59D9))
                  throw new JMSException("synthetic-provider-secret");
                String username = new String(body, 256, 64, StandardCharsets.UTF_8).stripTrailing();
                String context = "a".repeat(64);
                String effectiveRole = role;
                if (username.startsWith("user")) {
                  int ordinal = Integer.parseInt(username.substring(4));
                  context = String.format(java.util.Locale.ROOT, "%064x", ordinal);
                  effectiveRole = ordinal % 2 == 0 ? FIXTURE_USER_2DED8884 : FIXTURE_ADMIN_C4BB3010;
                  assertEquals(
                      "password-" + username,
                      new String(body, 320, 256, StandardCharsets.UTF_8).stripTrailing());
                }
                issued.add(context);
                byte[] reply;
                if (List.of(FIXTURE_0000_876EEFE0, FIXTURE_0200_FC9DB3AC).contains(loginCode)) {
                  reply = success(id, username, effectiveRole, context);
                  put(reply, 208, loginCode);
                } else
                  reply =
                      error(id, loginCode, loginCode.equals("0106") ? 900 : 0, "合成error message");
                assertTrue(client.onReply(id, reply));
                Arrays.fill(reply, (byte) 0);
              },
              clock,
              () -> new UUID(0, ids.incrementAndGet()),
              WAIT);
      probe =
          new MqLoginContextProbe(
              client,
              (id, body) -> {
                probes.incrementAndGet();
                buffers.add(body);
                assertEquals("GAMREQ01", new String(body, 11, 8, StandardCharsets.US_ASCII));
                assertEquals(id.toString(), new String(body, 60, 36, StandardCharsets.US_ASCII));
                String context = new String(body, 113, 64, StandardCharsets.US_ASCII);
                assertTrue(issued.contains(context));
                if (probeCode.equals(FIXTURE_JMS_1AEA59D9))
                  throw new JMSException("synthetic-probe-secret");
                byte[] reply =
                    probeCode.equals("MALFORMED")
                        ? new byte[0]
                        : MqLoginContextProbeTest.response(id, context, probeCode, 0);
                assertTrue(client.onReply(id, reply));
                Arrays.fill(reply, (byte) 0);
              },
              clock,
              () -> new UUID(0, ids.incrementAndGet()),
              WAIT);
      provider = new MqAuthenticationProvider(login, probe);
    }

    void closed() {
      assertEquals(0, client.pendingCount());
      assertEquals(0, client.lateReplyCount());
      for (byte[] buffer : buffers) assertArrayEquals(new byte[buffer.length], buffer);
    }
  }
}
