package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.NotificationController;
import dev.codex.schubert.nk.web.messaging.NotificationWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Full SCR020021/UI224236/SS313314, QA049; PG-D368/NTC-BIZ. Legacy config is not co-imported. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class NotificationBusinessMvcConfiguration {
  @Bean
  public NotificationController notificationController(
      NotificationWireClient client,
      ApiSessionInvalidHandler invalid,
      SessionOperationTokenLifecycle tokens) {
    return new NotificationController(client, invalid, tokens);
  }
}
