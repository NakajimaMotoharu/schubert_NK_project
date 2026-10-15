package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.QuestionController;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit partial SCR022023 read composition/UI224/SS313; PG-D350/PT-QRY-HTTP008,009. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class QuestionMvcConfiguration {
  @Bean
  public QuestionController questionController(
      QuestionWireClient client, ApiSessionInvalidHandler invalid) {
    return new QuestionController(client, invalid);
  }
}
