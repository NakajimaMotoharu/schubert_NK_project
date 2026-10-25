package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.NoSuchFileException;
import org.junit.jupiter.api.Test;

/** PT-ROOT-2118-001; SS343/SSC137; fixed disappearance truth table, not an OS authority grant. */
final class RootGenerationTruthTableTest {
  static final class Sequence extends RootStartupContextTest.LaunchFixture {
    final boolean firstMissing;
    final boolean secondMissing;
    boolean armed;
    int observed;

    Sequence(boolean firstMissing, boolean secondMissing) {
      this.firstMissing = firstMissing;
      this.secondMissing = secondMissing;
    }

    @Override
    public byte[] stat(long pid) throws IOException {
      if (armed && pid == 200) {
        assertTrue(observed < 2, "only the two captured-generation observations");
        boolean missing = observed++ == 0 ? firstMissing : secondMissing;
        if (missing) throw new NoSuchFileException("FIXED_PUBLIC_PROC");
      }
      return super.stat(pid);
    }
  }

  @Test
  void root2118001AllFourDisappearancePairsKeepRaceRejectionAndTwoReads() throws Exception {
    // independent tuple: first missing, second missing, rejects, successful return value
    for (boolean[] row :
        new boolean[][] {
          {false, false, false, false},
          {false, true, false, false},
          {true, false, true, false},
          {true, true, false, true}
        }) {
      var io = new Sequence(row[0], row[1]);
      var root = io.context();
      var morning = root.capture(RootStartupContext.Service.MORNING);
      var child = root.captureServiceRoot(morning, RootStartupContext.Service.API);
      io.armed = true;
      if (row[2]) {
        assertThrows(IOException.class, () -> root.serviceGenerationExited(morning, child));
      } else {
        assertEquals(row[3], root.serviceGenerationExited(morning, child));
      }
      assertEquals(2, io.observed);
    }
  }
}
