package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.protocol.header.AuthenticationContext;
import dev.codex.schubert.nk.protocol.layout.semantic.UserRole;
import dev.codex.schubert.nk.web.controller.LogController;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.LogSearchWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SecurityContextOwnerPortFixture;
import dev.codex.schubert.nk.web.session.SessionPrincipal;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.lang.reflect.Proxy;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.ResourceBundle;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.ui.ExtendedModelMap;
import org.springframework.util.LinkedMultiValueMap;

/** PT-SCR-LOG-BEAN001..003; SCR014 FUN008 AUT002 UI225 SS313. No Spring context or wire. */
final class LogMvcBeanPortTest {
  private static final Clock CLOCK = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);

  @Test
  void explicitConfigurationAndBeanDeclarationHaveExactPublicComposition() throws Exception {
    var configuration = LogMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = LogMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        LogMvcConfiguration.class.getDeclaredMethod(
            "logController", LogSearchWireClient.class, ApiSessionInvalidHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(LogController.class, method.getReturnType());
    assertEquals(
        1L,
        java.util.Arrays.stream(LogMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRequiresBothSuppliedDependenciesAndCreatesFreshControllers() {
    try (var owner = new SecurityContextOwnerPortFixture()) {
      var client = client();
      var invalid = invalid(owner);
      var factory = new LogMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(NullPointerException.class, () -> factory.logController(null, invalid))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(NullPointerException.class, () -> factory.logController(client, null))
              .getMessage());
      var first = factory.logController(client, invalid);
      var second = factory.logController(client, invalid);
      assertNotSame(first, second);
      assertEquals(LogController.class, first.getClass());
      assertEquals(LogController.class, second.getClass());
    }
  }

  @Test
  void returnedControllerRejectsUserRoleWithSingle403AndNoRequestOrBackendWork() throws Exception {
    try (var owner = new SecurityContextOwnerPortFixture()) {
      var controller = new LogMvcConfiguration().logController(client(), invalid(owner));
      var sent = new ArrayList<Integer>();
      var request =
          (HttpServletRequest)
              Proxy.newProxyInstance(
                  HttpServletRequest.class.getClassLoader(),
                  new Class<?>[] {HttpServletRequest.class},
                  (proxy, method, args) -> {
                    throw new AssertionError(
                        "request/session metadata forbidden: " + method.getName());
                  });
      var response =
          (HttpServletResponse)
              Proxy.newProxyInstance(
                  HttpServletResponse.class.getClassLoader(),
                  new Class<?>[] {HttpServletResponse.class},
                  (proxy, method, args) -> {
                    if (method.getName().equals("sendError") && args.length == 1) {
                      sent.add((Integer) args[0]);
                      return null;
                    }
                    throw new AssertionError("unexpected response callback: " + method.getName());
                  });
      var actor =
          new SessionPrincipal(
              "public-fixture",
              UserRole.USER,
              AuthenticationContext.of("0".repeat(64)),
              Instant.EPOCH);
      var model = new ExtendedModelMap();
      assertNull(controller.search(new LinkedMultiValueMap<>(), actor, model, request, response));
      assertEquals(List.of(403), sent);
      assertEquals(0, model.size());
    }
  }

  private static LogSearchWireClient client() {
    return new LogSearchWireClient(
        new JmsRequestReplyClient(new ReplyCorrelationRegistry(), CLOCK, 1),
        (id, bytes) -> {
          throw new AssertionError("JMS sender must not be called");
        },
        CLOCK,
        () -> {
          throw new AssertionError("identifier supplier must not be called");
        },
        Duration.ofSeconds(1));
  }

  private static ApiSessionInvalidHandler invalid(SecurityContextOwnerPortFixture owner) {
    return new ApiSessionInvalidHandler(
        owner.sessions(), new WebSecurityAudit(new NoLog(), CLOCK, "fixture", "fixture"));
  }

  private static final class NoLog implements System.Logger {
    @Override
    public String getName() {
      return "public-fixture";
    }

    @Override
    public boolean isLoggable(Level level) {
      return false;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      throw new AssertionError("audit log forbidden");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      throw new AssertionError("audit log forbidden");
    }
  }
}
