package dev.codex.schubert.characterization;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** PT-CHR-RAW008..014 / SS355: fake per-call IO, fixed independent sequence oracle. */
class GateOutputFailureContractTest {
  private static final String PHASE_PARENT = "parent";
  private static final String PHASE_WRITE = "write";
  private static final String PHASE_PUBLISH = "publish";
  private static final String PHASE_DELETE = "delete";
  private static final String FIXED_VALUE = "fixture";
  private static final int WRITE_INDEX = 1;
  private static final int PUBLISH_INDEX = 2;
  @TempDir Path root;

  @Test
  void allSixKnownHashCollisionsAreUnknownCommandsBeforeDispatch() {
    String[] known = {
      "verify-source", "preflight", "compare-current", "compare-nk", "report", "promote-current"
    };
    String[] unknown = {
      "wFrify-source", "qSeflight", "dPmpare-current", "dPmpare-nk", "sFport", "qSomote-current"
    };
    for (int index = 0; index < known.length; index++) {
      assertEquals(known[index].hashCode(), unknown[index].hashCode());
      String command = unknown[index];
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> GateCli.main(new String[] {command}));
      assertEquals("unknown command: " + command, failure.getMessage());
    }
  }

  @Test
  void targetHashCollisionsRemainUnknownAfterLowercasing() {
    String[] known = {"current", "nk"};
    String[] unknown = {"b\224rrent", "m\212"};
    for (int index = 0; index < known.length; index++) {
      assertEquals(known[index].hashCode(), unknown[index].hashCode());
      String target = unknown[index];
      IllegalArgumentException failure =
          assertThrows(IllegalArgumentException.class, () -> TargetAdapter.Target.parse(target));
      assertEquals("target must be current or nk", failure.getMessage());
    }
  }

  @Test
  void failureAtEachOutputPhaseDeletesTemporaryAndReleasesClaim() throws IOException {
    List<List<String>> expected =
        List.of(
            List.of(PHASE_PARENT, PHASE_DELETE),
            List.of(PHASE_PARENT, PHASE_WRITE, PHASE_DELETE),
            List.of(PHASE_PARENT, PHASE_WRITE, PHASE_PUBLISH, PHASE_DELETE));
    for (int index = 0; index < 3; index++) {
      Path output = root.resolve("phase" + index + ".json");
      FakeOutput io = new FakeOutput(index, false);
      assertSame(
          io.failure,
          assertThrows(IOException.class, () -> GateCli.writeJson(output, FIXED_VALUE, io)));
      assertEquals(expected.get(index), io.calls);
      FakeOutput retry = new FakeOutput(-1, false);
      GateCli.writeJson(output, FIXED_VALUE, retry);
      assertEquals(List.of(PHASE_PARENT, PHASE_WRITE, PHASE_PUBLISH, PHASE_DELETE), retry.calls);
      assertEquals(output.toAbsolutePath().normalize(), retry.output);
      assertEquals(output.resolveSibling(output.getFileName() + ".part"), retry.temporary);
    }
  }

  @Test
  void cleanupFailureHasExistingFinallyPrecedenceAndClaimIsStillReleased() throws IOException {
    Path output = root.resolve("cleanup.json");
    for (int phase : new int[] {-1, 0, 1, 2}) {
      FakeOutput io = new FakeOutput(phase, true);
      assertSame(
          io.cleanup, assertThrows(IOException.class, () -> GateCli.writeJson(output, null, io)));
      assertEquals(0, io.cleanup.getSuppressed().length);
      FakeOutput retry = new FakeOutput(-1, false);
      GateCli.writeJson(output, null, retry);
      assertEquals(List.of(PHASE_PARENT, PHASE_WRITE, PHASE_PUBLISH, PHASE_DELETE), retry.calls);
    }
  }

  @Test
  void nestedSameOutputIsRejectedWithoutReleasingOuterClaim() throws IOException {
    Path ownedOutput = root.resolve("nested.json");
    FakeOutput outer =
        new FakeOutput(-1, false) {
          @Override
          public void createParent(Path parent) throws IOException {
            super.createParent(parent);
            FakeOutput inner = new FakeOutput(-1, false);
            IllegalStateException actual =
                assertThrows(
                    IllegalStateException.class,
                    () -> GateCli.writeJson(ownedOutput, "nested", inner));
            assertEquals(
                "concurrent write to the same output is not allowed: "
                    + ownedOutput.toAbsolutePath().normalize(),
                actual.getMessage());
            assertTrue(inner.calls.isEmpty());
          }
        };
    GateCli.writeJson(ownedOutput, "outer", outer);
    assertEquals(List.of(PHASE_PARENT, PHASE_WRITE, PHASE_PUBLISH, PHASE_DELETE), outer.calls);
    GateCli.writeJson(ownedOutput, "after", new FakeOutput(-1, false));
  }

  @Test
  void nullPortIsRejectedBeforeAnyOutputClaim() throws IOException {
    Path output = root.resolve("nonnull.json");
    NullPointerException failure =
        assertThrows(
            NullPointerException.class, () -> GateCli.writeJson(output, FIXED_VALUE, null));
    assertEquals("JSON output IO", failure.getMessage());
    GateCli.writeJson(output, FIXED_VALUE, new FakeOutput(-1, false));
  }

  private static class FakeOutput implements GateCli.JsonOutput {
    private final int failedPhase;
    private final boolean failCleanup;
    final List<String> calls = new ArrayList<>();
    final IOException failure = new IOException("fixed-phase");
    final IOException cleanup = new IOException("fixed-cleanup");
    Path temporary;
    Path output;

    FakeOutput(int failedPhase, boolean failCleanup) {
      this.failedPhase = failedPhase;
      this.failCleanup = failCleanup;
    }

    @Override
    public void createParent(Path parent) throws IOException {
      calls.add(PHASE_PARENT);
      if (failedPhase == 0) throw failure;
    }

    @Override
    public void writeTemporary(Path path, Object value) throws IOException {
      temporary = path;
      calls.add(PHASE_WRITE);
      if (failedPhase == WRITE_INDEX) throw failure;
    }

    @Override
    public void publish(Path path, Path destination) throws IOException {
      assertEquals(temporary, path);
      output = destination;
      calls.add(PHASE_PUBLISH);
      if (failedPhase == PUBLISH_INDEX) throw failure;
    }

    @Override
    public void deleteTemporary(Path path) throws IOException {
      assertTrue(path.getFileName().toString().endsWith(".json.part"));
      calls.add(PHASE_DELETE);
      if (failCleanup) throw cleanup;
    }
  }
}
