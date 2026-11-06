package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.controller.AnimationController;
import dev.codex.schubert.nk.web.messaging.AnimationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import java.time.Duration;
import java.util.Arrays;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-SCR-ANIMATION-BEAN001..002 / SCR008009 FUN006 UI223235 SS311313. No controller invocation. */
final class AnimationMvcBeanPortTest {
  @Test
  void publicConfigurationImportsAndBeanSignatureMatchAnimationComposition() throws Exception {
    var configuration = AnimationMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = AnimationMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        AnimationMvcConfiguration.class.getDeclaredMethod(
            "animationController", AnimationWireClient.class, ApiSessionInvalidHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(AnimationController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(AnimationMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshAnimationControllers() {
    try (var ports = new MvcBeanPortFixture()) {
      var client =
          new AnimationWireClient(
              ports.requester(),
              ports.sender(),
              ports.clock(),
              ports.identifiers(),
              Duration.ofSeconds(1));
      var invalid = ports.invalid();
      var factory = new AnimationMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(NullPointerException.class, () -> factory.animationController(null, invalid))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(NullPointerException.class, () -> factory.animationController(client, null))
              .getMessage());
      var first = factory.animationController(client, invalid);
      var second = factory.animationController(client, invalid);
      assertNotSame(first, second);
      assertEquals(AnimationController.class, first.getClass());
      assertEquals(AnimationController.class, second.getClass());
    }
  }
}
