package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.controller.ScenarioController;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import java.time.Duration;
import java.util.Arrays;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-SCR-SCENARIO-BEAN001..002 / SCR004006 FUN004 UI223235 SS311313. No controller invocation. */
final class ScenarioMvcBeanPortTest {
  @Test
  void publicConfigurationImportsAndBeanSignatureMatchScenarioComposition() throws Exception {
    var configuration = ScenarioMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = ScenarioMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        ScenarioMvcConfiguration.class.getDeclaredMethod(
            "scenarioController", ScenarioWireClient.class, ApiSessionInvalidHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(ScenarioController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(ScenarioMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshScenarioControllers() {
    try (var ports = new MvcBeanPortFixture()) {
      var client =
          new ScenarioWireClient(
              ports.requester(),
              ports.sender(),
              ports.clock(),
              ports.identifiers(),
              Duration.ofSeconds(1));
      var invalid = ports.invalid();
      var factory = new ScenarioMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(NullPointerException.class, () -> factory.scenarioController(null, invalid))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(NullPointerException.class, () -> factory.scenarioController(client, null))
              .getMessage());
      var first = factory.scenarioController(client, invalid);
      var second = factory.scenarioController(client, invalid);
      assertNotSame(first, second);
      assertEquals(ScenarioController.class, first.getClass());
      assertEquals(ScenarioController.class, second.getClass());
    }
  }
}
