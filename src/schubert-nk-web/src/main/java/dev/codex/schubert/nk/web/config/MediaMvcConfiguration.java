package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.MediaController;
import dev.codex.schubert.nk.web.logging.WebMediaAudit;
import dev.codex.schubert.nk.web.media.MediaRangeService;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit media-only composition, not full native ready. UI223/237/SS313,333/PG-D-343. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class MediaMvcConfiguration {
  @Bean
  public MediaController mediaController(
      MediaDescriptorWireClient client,
      ApiSessionInvalidHandler invalid,
      MediaRangeService service,
      WebMediaAudit audit) {
    return new MediaController(client, invalid, service, audit);
  }
}
