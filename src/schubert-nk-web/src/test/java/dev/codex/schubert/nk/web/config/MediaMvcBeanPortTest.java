package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.controller.MediaController;
import dev.codex.schubert.nk.web.logging.WebMediaAudit;
import dev.codex.schubert.nk.web.media.MediaRangeService;
import dev.codex.schubert.nk.web.messaging.MediaDescriptorWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import java.time.Duration;
import java.util.Arrays;
import java.util.ResourceBundle;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-MED-MVC-BEAN001..002; UI223237 SS313333. No endpoint, file source, stream or audit call. */
final class MediaMvcBeanPortTest {
  @Test
  void publicConfigurationAndFourPortBeanSignatureMatchMediaComposition() throws Exception {
    var configuration = MediaMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = MediaMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        MediaMvcConfiguration.class.getDeclaredMethod(
            "mediaController",
            MediaDescriptorWireClient.class,
            ApiSessionInvalidHandler.class,
            MediaRangeService.class,
            WebMediaAudit.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(MediaController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(MediaMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRejectsEachMissingPortAndReturnsFreshMediaControllers() {
    try (var ports = new MvcBeanPortFixture()) {
      var client =
          new MediaDescriptorWireClient(
              ports.requester(),
              ports.sender(),
              ports.clock(),
              ports.identifiers(),
              Duration.ofSeconds(1));
      var invalid = ports.invalid();
      var service =
          new MediaRangeService(
              (descriptor, operation) -> {
                throw new AssertionError("file-source call forbidden");
              });
      var audit = new WebMediaAudit(new NoLog(), ports.clock(), "fixture", "fixture");
      var factory = new MediaMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.mediaController(null, invalid, service, audit))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.mediaController(client, null, service, audit))
              .getMessage());
      assertEquals(
          "service",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.mediaController(client, invalid, null, audit))
              .getMessage());
      assertEquals(
          "audit",
          assertThrows(
                  NullPointerException.class,
                  () -> factory.mediaController(client, invalid, service, null))
              .getMessage());
      var first = factory.mediaController(client, invalid, service, audit);
      var second = factory.mediaController(client, invalid, service, audit);
      assertNotSame(first, second);
      assertEquals(MediaController.class, first.getClass());
      assertEquals(MediaController.class, second.getClass());
    }
  }

  private static final class NoLog implements System.Logger {
    @Override
    public String getName() {
      return "public-fixture";
    }

    @Override
    public boolean isLoggable(Level level) {
      return false;
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String message, Throwable thrown) {
      throw new AssertionError("media audit output forbidden");
    }

    @Override
    public void log(Level level, ResourceBundle bundle, String format, Object... parameters) {
      throw new AssertionError("media audit output forbidden");
    }
  }
}
