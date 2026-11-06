package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.controller.QuestionController;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import java.time.Duration;
import java.util.Arrays;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-SCR-QUESTION-BEAN001..002 / SCR022023 FUN010 UI224236 SS311313. No controller invocation. */
final class QuestionMvcBeanPortTest {
  @Test
  void publicConfigurationImportsAndBeanSignatureMatchQuestionComposition() throws Exception {
    var configuration = QuestionMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = QuestionMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        QuestionMvcConfiguration.class.getDeclaredMethod(
            "questionController", QuestionWireClient.class, ApiSessionInvalidHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(QuestionController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(QuestionMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshQuestionControllers() {
    try (var ports = new MvcBeanPortFixture()) {
      var client =
          new QuestionWireClient(
              ports.requester(),
              ports.sender(),
              ports.clock(),
              ports.identifiers(),
              Duration.ofSeconds(1));
      var invalid = ports.invalid();
      var factory = new QuestionMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(NullPointerException.class, () -> factory.questionController(null, invalid))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(NullPointerException.class, () -> factory.questionController(client, null))
              .getMessage());
      var first = factory.questionController(client, invalid);
      var second = factory.questionController(client, invalid);
      assertNotSame(first, second);
      assertEquals(QuestionController.class, first.getClass());
      assertEquals(QuestionController.class, second.getClass());
    }
  }
}
