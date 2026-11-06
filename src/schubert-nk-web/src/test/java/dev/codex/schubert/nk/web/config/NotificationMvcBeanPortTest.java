package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.controller.NotificationController;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import java.time.Duration;
import java.util.Arrays;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-SCR-NOTIFICATION-BEAN001..002 / SCR020 FUN010 UI224236 SS311313. No controller invocation. */
final class NotificationMvcBeanPortTest {
  @Test
  void publicConfigurationImportsAndBeanSignatureMatchNotificationComposition() throws Exception {
    var configuration =
        NotificationMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = NotificationMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        NotificationMvcConfiguration.class.getDeclaredMethod(
            "notificationController", NotificationWireClient.class, ApiSessionInvalidHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(NotificationController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(NotificationMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshNotificationControllers() {
    try (var ports = new MvcBeanPortFixture()) {
      var client =
          new NotificationWireClient(
              ports.requester(),
              ports.sender(),
              ports.clock(),
              ports.identifiers(),
              Duration.ofSeconds(1));
      var invalid = ports.invalid();
      var factory = new NotificationMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(
                  NullPointerException.class, () -> factory.notificationController(null, invalid))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(
                  NullPointerException.class, () -> factory.notificationController(client, null))
              .getMessage());
      var first = factory.notificationController(client, invalid);
      var second = factory.notificationController(client, invalid);
      assertNotSame(first, second);
      assertEquals(NotificationController.class, first.getClass());
      assertEquals(NotificationController.class, second.getClass());
    }
  }
}
