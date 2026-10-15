package dev.codex.schubert.nk.web.config;

import dev.codex.schubert.nk.web.controller.QuestionController;
import dev.codex.schubert.nk.web.messaging.QuestionWireClient;
import dev.codex.schubert.nk.web.receipt.ReceiptReferenceRepository;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import dev.codex.schubert.nk.web.session.SessionOperationTokenLifecycle;
import org.jspecify.annotations.NullMarked;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** Explicit SCR018019022023 composition; UI224; SS313/314; QA048049; RCPT006A..H. */
@Configuration(proxyBeanMethods = false)
@Import(WebMvcConfiguration.class)
@NullMarked
public class QuestionAcceptanceMvcConfiguration {
  @Bean
  public QuestionController questionController(
      QuestionWireClient client,
      ApiSessionInvalidHandler invalid,
      ReceiptReferenceRepository receipts,
      SessionOperationTokenLifecycle tokens) {
    return new QuestionController(client, invalid, receipts, tokens);
  }
}
