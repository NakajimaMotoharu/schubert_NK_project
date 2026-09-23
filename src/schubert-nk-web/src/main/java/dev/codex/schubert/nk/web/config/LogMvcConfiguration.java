package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.LogController;
import dev.codex.schubert.nk.web.messaging.LogSearchWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit SCR014 MVC composition; NK-WEB-002/FUN008/AUT002/UI225/SS313/PG218/PT-SCR099. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class LogMvcConfiguration {
  @Bean
  public LogController logController(LogSearchWireClient client, ApiSessionInvalidHandler invalid) {
    return new LogController(client, invalid);
  }
}
