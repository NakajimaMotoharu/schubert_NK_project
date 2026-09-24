package dev.codex.schubert.nk.web.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/**
 * Login/common MVC with Scenario search and Log screens in one Web process. NK-WEB-002; RD
 * FUN-004/008, AUT-002; UI221..225/235; SS311/313/314/342; PG262/PT-SCR-135.
 */
@Configuration(proxyBeanMethods = false)
@Import({ScenarioMvcConfiguration.class, LogMvcConfiguration.class})
public class ScenarioLogMvcConfiguration {}
