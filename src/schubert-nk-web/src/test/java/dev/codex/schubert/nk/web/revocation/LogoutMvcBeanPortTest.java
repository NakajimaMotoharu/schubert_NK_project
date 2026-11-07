package dev.codex.schubert.nk.web.revocation;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.config.LogoutMvcConfiguration;
import dev.codex.schubert.nk.web.config.WebMvcConfiguration;
import dev.codex.schubert.nk.web.controller.LogoutController;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogoutWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.LocalLogoutHandler;
import dev.codex.schubert.nk.web.session.BusinessMvcOwnerPortFixture;
import java.security.Provider;
import java.security.SecureRandom;
import java.security.SecureRandomSpi;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.ResourceBundle;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-WEB-LOGOUT-MVC-BEAN001..002; UI226/SS313314; constructor-only, no Logout operation. */
final class LogoutMvcBeanPortTest {
  private static final String FIXTURE = "public-fixture";

  @Test
  void publicConfigurationAndSingleBorrowedHandlerBeanMatchLogoutComposition() throws Exception {
    var configuration = LogoutMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = LogoutMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        LogoutMvcConfiguration.class.getDeclaredMethod(
            "logoutController", LocalLogoutHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(LogoutController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(LogoutMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRejectsNullAndReturnsFreshControllersWithoutInvokingBorrowedOwners() {
    try (var sessions = new BusinessMvcOwnerPortFixture();
        var codec =
            new RevocationPayloadCodec(FIXTURE, new byte[32], null, null, new NeverRandom())) {
      var clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
      var requester = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 1);
      var wire =
          new LogoutWireClient(
              requester,
              (id, bytes) -> {
                throw new AssertionError("wire callback forbidden in constructor-only fixture");
              },
              clock,
              () -> {
                throw new AssertionError("identifier generation forbidden");
              },
              Duration.ofSeconds(1));
      var coordinator = new LocalLogoutCoordinator(sessions.localSessions(), codec, wire, clock);
      var audit = new WebSecurityAudit(new NoLog(), clock, FIXTURE, FIXTURE);
      var handler = new LocalLogoutHandler(sessions.sessions(), coordinator, audit);
      var factory = new LogoutMvcConfiguration();
      assertEquals(
          "Logout handler",
          assertThrows(NullPointerException.class, () -> factory.logoutController(null))
              .getMessage());
      var first = factory.logoutController(handler);
      var second = factory.logoutController(handler);
      assertNotSame(first, second);
      assertEquals(LogoutController.class, first.getClass());
      assertEquals(LogoutController.class, second.getClass());
    }
  }

  private static final class NeverRandom extends SecureRandom {
    private static final long serialVersionUID = 1L;

    NeverRandom() {
      super(new NeverSpi(), new OwnProvider());
    }
  }

  private static final class OwnProvider extends Provider {
    private static final long serialVersionUID = 1L;

    OwnProvider() {
      super("PGPT_NO_RANDOM", "1.0", "Own fixture, no services or global registration");
    }
  }

  private static final class NeverSpi extends SecureRandomSpi {
    private static final long serialVersionUID = 1L;

    @Override
    protected void engineSetSeed(byte[] seed) {
      throw new AssertionError("random seeding forbidden");
    }

    @Override
    protected void engineNextBytes(byte[] bytes) {
      throw new AssertionError("random generation forbidden");
    }

    @Override
    protected byte[] engineGenerateSeed(int count) {
      throw new AssertionError("random seed generation forbidden");
    }
  }

  private static final class NoLog implements System.Logger {
    @Override
    public String getName() {
      return FIXTURE;
    }

    @Override
    public boolean isLoggable(Level level) {
      return false;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      throw new AssertionError("audit output forbidden in constructor-only fixture");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      throw new AssertionError("audit output forbidden in constructor-only fixture");
    }
  }
}
