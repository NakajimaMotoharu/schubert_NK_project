package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.ScenarioController;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/**
 * Explicit hierarchy composition, not full bootstrap.
 * NK-WEB-002/FUN004/UI221..223/SS311,313/SSC071/PG194/PT-SCR-015.
 */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class ScenarioMvcConfiguration {
  @Bean
  public ScenarioController scenarioController(
      ScenarioWireClient client, ApiSessionInvalidHandler invalid) {
    return new ScenarioController(client, invalid);
  }
}
