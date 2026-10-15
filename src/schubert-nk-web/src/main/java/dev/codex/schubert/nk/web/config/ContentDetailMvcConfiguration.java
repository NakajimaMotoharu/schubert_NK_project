package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.ContentDetailController;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.messaging.ScenarioWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.storage.LargeResultReader;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit SCR007/010/013 composition; all resources borrowed. UI223234235/SS313/PG-D365. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
public class ContentDetailMvcConfiguration {
  @Bean
  public ContentDetailController contentDetailController(
      ScenarioWireClient scenarios,
      MediaDescriptorWireClient media,
      MusicWireClient music,
      LargeResultReader files,
      ApiSessionInvalidHandler invalid) {
    return new ContentDetailController(scenarios, media, music, files, invalid);
  }
}
