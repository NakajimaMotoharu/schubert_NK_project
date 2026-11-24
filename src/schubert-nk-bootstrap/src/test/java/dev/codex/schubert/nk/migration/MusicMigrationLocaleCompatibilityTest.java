package dev.codex.schubert.nk.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Isolated;

/** SS343 music pairing, PT-MIG-MUSICPAIR027. */
@Isolated("sets and restores the test JVM locale")
final class MusicMigrationLocaleCompatibilityTest {
  private static final String MAIN = "theme.flac";
  private static final String SECOND = "theme_inst.flac";

  @Test
  void preservesCurrentDefaultLocaleAndShadowingRules() {
    Locale original = Locale.getDefault();
    Locale originalDisplay = Locale.getDefault(Locale.Category.DISPLAY);
    Locale originalFormat = Locale.getDefault(Locale.Category.FORMAT);
    var tracks = Map.of(MAIN, "THEME", SECOND, "THEME INSTRUMENTAL");
    try {
      Locale.setDefault(Locale.US);
      var english = new MusicMigrationPairing().plan(tracks);
      assertEquals(1, english.pairs().size());
      var paired = english.pairs().getFirst();
      assertEquals("theme", paired.key());
      assertEquals(Optional.of(MAIN), paired.mainDisplayPath());
      assertEquals(Optional.of(SECOND), paired.instrumentalDisplayPath());
      assertTrue(english.shadowedPaths().isEmpty());

      Locale.setDefault(Locale.forLanguageTag("tr-TR"));
      var turkish = new MusicMigrationPairing().plan(tracks);
      assertEquals(1, turkish.pairs().size());
      var unpaired = turkish.pairs().getFirst();
      assertEquals("theme", unpaired.key());
      assertEquals(Optional.of(SECOND), unpaired.mainDisplayPath());
      assertTrue(unpaired.instrumentalDisplayPath().isEmpty());
      assertEquals(List.of(MAIN), turkish.shadowedPaths());
    } finally {
      Locale.setDefault(original);
      Locale.setDefault(Locale.Category.DISPLAY, originalDisplay);
      Locale.setDefault(Locale.Category.FORMAT, originalFormat);
    }
  }
}
