package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/** SS343/SSC168/179: public native defaults cannot use synthetic authority to retire originals. */
final class RootRecoveryNativeAuthorityTest {
  @TempDir Path temporary;

  @Test
  void recoveryNative001SinglePublicDefaultsRejectUnprivilegedHostWithoutAnyOriginalMutation()
      throws Exception {
    var owner = new RootFailedStartRecoveryTest();
    owner.temporary = temporary;
    var fixture = owner.new Fixture("API");
    try (fixture) {
      var evidence = fixture.observe();
      var before = snapshot(fixture.f.parent);
      var proofs = new AtomicInteger();
      assertThrows(
          IOException.class, () -> RootFailedStartRecovery.observe(fixture.f.root, fixture.f));
      assertEquals(before, snapshot(fixture.f.parent));
      assertThrows(
          IOException.class,
          () ->
              RootFailedStartRecovery.retire(
                  fixture.f.root, fixture.f, evidence, ignored -> proofs.incrementAndGet()));
      assertEquals(before, snapshot(fixture.f.parent));
      assertThrows(
          IOException.class,
          () -> RootFailedStartRecovery.quarantine(fixture.f.root, fixture.f, evidence));
      assertEquals(before, snapshot(fixture.f.parent));
      assertEquals(0, proofs.get(), "native authority is rejected before borrowed proof or unlink");
      assertEquals(evidence, fixture.observe(), "injected original fixture remains readable");
    }
    assertTrue(fixture.f.descriptors.isEmpty());
  }

  @Test
  void recoveryNative002PairPublicDefaultsRejectBothChildrenAndPreservePublicationFirstQuarantine()
      throws Exception {
    var owner = new RootFailedStartPairRecoveryTest();
    owner.temporary = temporary;
    var fixture = owner.new Fixture();
    try (fixture) {
      var evidence = fixture.observe();
      var before = snapshot(fixture.f.f.parent);
      var proofs = new AtomicInteger();
      assertThrows(
          IOException.class,
          () -> RootFailedStartRecovery.observePair(fixture.f.f.root, fixture.f.f));
      assertEquals(before, snapshot(fixture.f.f.parent));
      assertThrows(
          IOException.class,
          () ->
              RootFailedStartRecovery.retirePair(
                  fixture.f.f.root, fixture.f.f, evidence, ignored -> proofs.incrementAndGet()));
      assertEquals(before, snapshot(fixture.f.f.parent));
      var failure =
          assertThrows(
              IOException.class,
              () ->
                  RootFailedStartRecovery.quarantinePair(fixture.f.f.root, fixture.f.f, evidence));
      assertEquals("failed startup pair quarantine uncertain", failure.getMessage());
      assertEquals(
          3,
          failure.getSuppressed().length,
          "publication and both child attempts are separately retained as uncertain");
      assertEquals(before, snapshot(fixture.f.f.parent));
      assertEquals(0, proofs.get());
      fixture.assertQuarantined();
      assertEquals(evidence, fixture.observe());
    }
    assertTrue(fixture.f.f.descriptors.isEmpty());
  }

  private static Map<String, String> snapshot(Path root) throws IOException {
    var result = new TreeMap<String, String>();
    try (var files = Files.list(root)) {
      for (var p : files.toList())
        result.put(
            p.getFileName().toString(), java.util.HexFormat.of().formatHex(Files.readAllBytes(p)));
    }
    return result;
  }
}
