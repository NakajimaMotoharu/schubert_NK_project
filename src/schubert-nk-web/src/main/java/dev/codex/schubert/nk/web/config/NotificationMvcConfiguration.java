package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.NotificationController;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit SCR020 partial composition/UI224/SS313; PG-D347/PT-NTF-HTTP008..010. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class NotificationMvcConfiguration {
  @Bean
  public NotificationController notificationController(
      NotificationWireClient client, ApiSessionInvalidHandler invalid) {
    return new NotificationController(client, invalid);
  }
}
