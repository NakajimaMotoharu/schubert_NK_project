package dev.codex.schubert.nk.web.config;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.web.controller.MusicController;
import dev.codex.schubert.nk.web.messaging.MusicWireClient;
import dev.codex.schubert.nk.web.security.ApiSessionInvalidHandler;
import java.time.Duration;
import java.util.Arrays;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;

/** PT-SCR-MUSIC-BEAN001..002 / SCR011012 FUN007 UI223235 SS311313. No controller invocation. */
final class MusicMvcBeanPortTest {
  @Test
  void publicConfigurationImportsAndBeanSignatureMatchMusicComposition() throws Exception {
    var configuration = MusicMvcConfiguration.class.getDeclaredAnnotation(Configuration.class);
    assertNotNull(configuration);
    assertFalse(configuration.proxyBeanMethods());
    var imports = MusicMvcConfiguration.class.getDeclaredAnnotation(Import.class);
    assertNotNull(imports);
    assertArrayEquals(new Class<?>[] {WebMvcConfiguration.class}, imports.value());
    var method =
        MusicMvcConfiguration.class.getDeclaredMethod(
            "musicController", MusicWireClient.class, ApiSessionInvalidHandler.class);
    assertNotNull(method.getDeclaredAnnotation(Bean.class));
    assertEquals(MusicController.class, method.getReturnType());
    assertEquals(
        1L,
        Arrays.stream(MusicMvcConfiguration.class.getDeclaredMethods())
            .filter(member -> !member.isSynthetic())
            .count());
  }

  @Test
  void directFactoryRequiresBothSuppliedDependenciesAndReturnsFreshMusicControllers() {
    try (var ports = new MvcBeanPortFixture()) {
      var client =
          new MusicWireClient(
              ports.requester(),
              ports.sender(),
              ports.clock(),
              ports.identifiers(),
              Duration.ofSeconds(1));
      var invalid = ports.invalid();
      var factory = new MusicMvcConfiguration();
      assertEquals(
          "client",
          assertThrows(NullPointerException.class, () -> factory.musicController(null, invalid))
              .getMessage());
      assertEquals(
          "invalid",
          assertThrows(NullPointerException.class, () -> factory.musicController(client, null))
              .getMessage());
      var first = factory.musicController(client, invalid);
      var second = factory.musicController(client, invalid);
      assertNotSame(first, second);
      assertEquals(MusicController.class, first.getClass());
      assertEquals(MusicController.class, second.getClass());
    }
  }
}
