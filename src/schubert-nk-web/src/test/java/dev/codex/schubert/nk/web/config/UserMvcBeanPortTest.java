package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.controller.UserAdminController;
import dev.codex.schubert.nk.web.messaging.UserAdministrationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import java.time.Duration;
import java.util.Arrays;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-SCR-USER-BEAN001..002 / SCR015 FUN011 UI225236 SS311313. No controller invocation. */
final class UserMvcBeanPortTest {
  @Test
  void publicConfigurationImportsAndBeanSignatureMatchUserComposition() throws Exception {
    var configuration = UserMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = UserMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        UserMvcConfiguration.class.getDeclaredMethod(
            "userAdminController",
            UserAdministrationWireClient.class,
            ApiSessionInvalidHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(UserAdminController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(UserMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshUserAdminControllers() {
    try (var ports = new MvcBeanPortFixture()) {
      var client =
          new UserAdministrationWireClient(
              ports.requester(),
              ports.sender(),
              ports.clock(),
              ports.identifiers(),
              Duration.ofSeconds(1));
      var invalid = ports.invalid();
      var factory = new UserMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(NullPointerException.class, () -> factory.userAdminController(null, invalid))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(NullPointerException.class, () -> factory.userAdminController(client, null))
              .getMessage());
      var first = factory.userAdminController(client, invalid);
      var second = factory.userAdminController(client, invalid);
      assertNotSame(first, second);
      assertEquals(UserAdminController.class, first.getClass());
      assertEquals(UserAdminController.class, second.getClass());
    }
  }
}
