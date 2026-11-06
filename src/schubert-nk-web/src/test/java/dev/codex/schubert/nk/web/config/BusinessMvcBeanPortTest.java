package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import dev.codex.schubert.nk.web.controller.NotificationController;
import dev.codex.schubert.nk.web.controller.QuestionController;
import dev.codex.schubert.nk.web.controller.UserAdminController;
import dev.codex.schubert.nk.web.logging.WebSecurityAudit;
import dev.codex.schubert.nk.web.messaging.JmsRequestReplyClient;
import dev.codex.schubert.nk.web.messaging.JmsRequestSender;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.messaging.ReplyCorrelationRegistry;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.receipt.ReceiptReferenceRepository;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.BusinessMvcOwnerPortFixture;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.List;
import java.util.ResourceBundle;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** UI224/226/236; SS313/314; QA048/049; PT-SCR-BIZBEAN001..006. Constructors only. */
final class BusinessMvcBeanPortTest {
  private static final String CLIENT = "client";
  private static final String INVALID = "invalid";
  private static final String TOKENS = "tokens";

  @Test
  void notificationBusinessSignatureRequiresTheTokenLifecyclePort() throws Exception {
    metadata(
        NotificationBusinessMvcConfiguration.class,
        "notificationController",
        NotificationController.class,
        NotificationWireClient.class,
        ApiSessionInvalidHandler.class,
        SessionOperationTokenLifecycle.class);
  }

  @Test
  void notificationBusinessRejectsEveryMissingPortAndReturnsFreshControllers() {
    try (var ports = new Ports()) {
      var config = new NotificationBusinessMvcConfiguration();
      assertEquals(
          CLIENT,
          assertThrows(
                  NullPointerException.class,
                  () -> config.notificationController(null, ports.invalid, ports.owner.tokens()))
              .getMessage());
      assertEquals(
          INVALID,
          assertThrows(
                  NullPointerException.class,
                  () ->
                      config.notificationController(ports.notification, null, ports.owner.tokens()))
              .getMessage());
      assertEquals(
          TOKENS,
          assertThrows(
                  NullPointerException.class,
                  () -> config.notificationController(ports.notification, ports.invalid, null))
              .getMessage());
      var first =
          config.notificationController(ports.notification, ports.invalid, ports.owner.tokens());
      var second =
          config.notificationController(ports.notification, ports.invalid, ports.owner.tokens());
      assertEquals(NotificationController.class, first.getClass());
      assertNotSame(first, second);
    }
  }

  @Test
  void userBusinessSignatureRequiresTheTokenLifecyclePort() throws Exception {
    metadata(
        UserBusinessMvcConfiguration.class,
        "userAdminController",
        UserAdminController.class,
        UserAdministrationWireClient.class,
        ApiSessionInvalidHandler.class,
        SessionOperationTokenLifecycle.class);
  }

  @Test
  void userBusinessRejectsEveryMissingPortAndReturnsFreshControllers() {
    try (var ports = new Ports()) {
      var config = new UserBusinessMvcConfiguration();
      assertEquals(
          CLIENT,
          assertThrows(
                  NullPointerException.class,
                  () -> config.userAdminController(null, ports.invalid, ports.owner.tokens()))
              .getMessage());
      assertEquals(
          INVALID,
          assertThrows(
                  NullPointerException.class,
                  () -> config.userAdminController(ports.users, null, ports.owner.tokens()))
              .getMessage());
      assertEquals(
          TOKENS,
          assertThrows(
                  NullPointerException.class,
                  () -> config.userAdminController(ports.users, ports.invalid, null))
              .getMessage());
      var first = config.userAdminController(ports.users, ports.invalid, ports.owner.tokens());
      var second = config.userAdminController(ports.users, ports.invalid, ports.owner.tokens());
      assertEquals(UserAdminController.class, first.getClass());
      assertNotSame(first, second);
    }
  }

  @Test
  void questionAcceptanceSignatureRequiresReceiptAndTokenPorts() throws Exception {
    metadata(
        QuestionAcceptanceMvcConfiguration.class,
        "questionController",
        QuestionController.class,
        QuestionWireClient.class,
        ApiSessionInvalidHandler.class,
        ReceiptReferenceRepository.class,
        SessionOperationTokenLifecycle.class);
  }

  @Test
  void questionAcceptanceRejectsEveryMissingPortAndReturnsFreshControllers() {
    try (var ports = new Ports()) {
      var config = new QuestionAcceptanceMvcConfiguration();
      assertEquals(
          CLIENT,
          assertThrows(
                  NullPointerException.class,
                  () ->
                      config.questionController(
                          null, ports.invalid, ports.owner.receipts(), ports.owner.tokens()))
              .getMessage());
      assertEquals(
          INVALID,
          assertThrows(
                  NullPointerException.class,
                  () ->
                      config.questionController(
                          ports.question, null, ports.owner.receipts(), ports.owner.tokens()))
              .getMessage());
      assertEquals(
          "receipts",
          assertThrows(
                  NullPointerException.class,
                  () ->
                      config.questionController(
                          ports.question, ports.invalid, null, ports.owner.tokens()))
              .getMessage());
      assertEquals(
          TOKENS,
          assertThrows(
                  NullPointerException.class,
                  () ->
                      config.questionController(
                          ports.question, ports.invalid, ports.owner.receipts(), null))
              .getMessage());
      var first =
          config.questionController(
              ports.question, ports.invalid, ports.owner.receipts(), ports.owner.tokens());
      var second =
          config.questionController(
              ports.question, ports.invalid, ports.owner.receipts(), ports.owner.tokens());
      assertEquals(QuestionController.class, first.getClass());
      assertNotSame(first, second);
    }
  }

  private static void metadata(Class<?> config, String name, Class<?> result, Class<?>... arguments)
      throws Exception {
    var annotation = config.getAnnotation(Configuration.class);
    assertFalse(annotation.proxyBeanMethods());
    assertEquals(
        List.of(WebMvcConfiguration.class),
        Arrays.asList(config.getAnnotation(Import.class).value()));
    var method = config.getMethod(name, arguments);
    assertTrue(method.isAnnotationPresent(Bean.class));
    assertEquals(result, method.getReturnType());
    assertEquals(
        1L, Arrays.stream(config.getDeclaredMethods()).filter(m -> !m.isSynthetic()).count());
  }

  private static final class Ports implements AutoCloseable {
    private final BusinessMvcOwnerPortFixture owner = new BusinessMvcOwnerPortFixture();
    private final ApiSessionInvalidHandler invalid;
    private final NotificationWireClient notification;
    private final UserAdministrationWireClient users;
    private final QuestionWireClient question;

    Ports() {
      var clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
      var requester = new JmsRequestReplyClient(new ReplyCorrelationRegistry(), clock, 1);
      JmsRequestSender sender =
          (id, bytes) -> {
            throw new AssertionError("JMS forbidden");
          };
      Supplier<UUID> ids =
          () -> {
            throw new AssertionError("identifier generation forbidden");
          };
      invalid =
          new ApiSessionInvalidHandler(
              owner.sessions(), new WebSecurityAudit(new NoLog(), clock, "fixture", "fixture"));
      notification = new NotificationWireClient(requester, sender, clock, ids, Duration.ofNanos(1));
      users = new UserAdministrationWireClient(requester, sender, clock, ids, Duration.ofNanos(1));
      question = new QuestionWireClient(requester, sender, clock, ids, Duration.ofNanos(1));
    }

    @Override
    public void close() {
      owner.close();
    }
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
      throw new AssertionError("audit output forbidden");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      throw new AssertionError("audit output forbidden");
    }
  }
}
