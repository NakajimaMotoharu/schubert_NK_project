package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.MusicController;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/**
 * SCR011/012/FUN007/UI223,235/SS311,313/PG211/PT-SCR072..083. Explicit composition, not production
 * bootstrap.
 */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
public class MusicMvcConfiguration {
  @Bean
  public MusicController musicController(MusicWireClient client, ApiSessionInvalidHandler invalid) {
    return new MusicController(client, invalid);
  }
}
