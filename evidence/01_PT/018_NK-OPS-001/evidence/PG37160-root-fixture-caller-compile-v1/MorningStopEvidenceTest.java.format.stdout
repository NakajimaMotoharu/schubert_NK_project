package dev.codex.schubert.nk.batch.platform;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.file.MorningGateEvidence;
import dev.codex.schubert.nk.batch.file.StartupPermitRecords;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.HexFormat;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** ISSSTOP005: persisted SS literal golden, never generated through production codec. */
final class MorningStopEvidenceTest {
  static MorningUnitTerminals.Snapshot snapshot(boolean present) throws Exception {
    var f = new RootStartupContextTest.Fixture();
    f.group = "0::/system.slice/schubert-nk-morning-controller.service\n";
    f.unitValues = RootStartupContextTest.unit(RootStartupContext.Service.MORNING);
    var context = f.context();
    var parent = context.capture(RootStartupContext.Service.MORNING);
    return MorningUnitTerminals.capture(
        context,
        parent,
        unit -> {
          var terminal = new MaintenanceUnitTerminationTest.Fixture();
          terminal.target = unit;
          terminal.name = unit.serviceName();
          terminal.kernel.present = present;
          var actual = terminal.adapter().quiescentObservation();
          terminal.closed();
          return actual;
        });
  }

  static StartupPermitRecords.Epoch epoch(UUID boot) {
    return new StartupPermitRecords.Epoch(
        StartupPermitRecords.State.INVALID,
        boot,
        UUID.fromString("22222222-2222-4333-8444-555555555555"),
        new MaintenanceActivation(
            new BatchRun(
                UUID.fromString("33333333-2222-4333-8444-555555555555"),
                Instant.parse("2026-09-27T15:00:00Z")),
            UUID.fromString("44444444-2222-4333-8444-555555555555")),
        Optional.empty());
  }

  static byte[] fixture(String name) throws Exception {
    try (var input =
        Objects.requireNonNull(
            MorningStopEvidenceTest.class.getResourceAsStream("/ops/" + name),
            "independent fixture")) {
      return input.readAllBytes();
    }
  }

  @Test
  void issstop005EightActualUnitsKernelShapesAndNativeOrHistoryMatchGolden() throws Exception {
    for (boolean present : List.of(false, true)) {
      var initial = snapshot(present);
      UUID boot = UUID.fromString(initial.parent().boot());
      for (boolean nativeInterval : List.of(false, true)) {
        var f = new MorningPreviousBrokerTest.Fixture();
        f.bootHex = boot.toString().replace("-", "");
        assertArrayEquals(
            fixture("issuer-stop-journal.jsonl"),
            f.full
                .replace("11111111111141118111111111111111", f.bootHex)
                .getBytes(StandardCharsets.UTF_8));
        var old =
            MorningPreviousBroker.collect(
                boot,
                nativeInterval
                    ? MorningPreviousBrokerTest.stopped()
                    : MorningPreviousBrokerTest.cold(),
                f,
                () -> 1_000_000_000L);
        assertEquals(
            HexFormat.of()
                .formatHex(
                    java.security.MessageDigest.getInstance("SHA-256")
                        .digest(fixture("issuer-stop-journal-content-golden.txt"))),
            old.contentSha256());
        byte[] expected =
            fixture(
                "issuer-stop-"
                    + (present ? "present" : "absent")
                    + "-"
                    + (nativeInterval ? "native" : "boot")
                    + "-golden.txt");
        byte[] actual =
            MorningGateEvidence.stop(epoch(boot), "1".repeat(32), "2".repeat(32), initial, old);
        assertArrayEquals(expected, actual);
        actual[0] = 0;
        assertArrayEquals(
            expected,
            MorningGateEvidence.stop(epoch(boot), "1".repeat(32), "2".repeat(32), initial, old));
        old.recheck();
        f.erased();
      }
    }
  }

  @Test
  void issstop006BindingNullAndOldGenerationCannotBecomeCurrentBroker() throws Exception {
    var initial = snapshot(false);
    UUID boot = UUID.fromString(initial.parent().boot());
    var f = new MorningPreviousBrokerTest.Fixture();
    f.bootHex = boot.toString().replace("-", "");
    var old =
        MorningPreviousBroker.collect(
            boot, MorningPreviousBrokerTest.cold(), f, () -> 1_000_000_000L);
    assertThrows(
        IOException.class,
        () -> MorningGateEvidence.stop(epoch(boot), "3".repeat(32), "2".repeat(32), initial, old));
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.stop(
                epoch(UUID.randomUUID()), "1".repeat(32), "2".repeat(32), initial, old));
    assertThrows(
        IOException.class,
        () -> MorningGateEvidence.stop(epoch(boot), "1".repeat(32), "7".repeat(32), initial, old));
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.stop(
                epoch(boot).issued("a".repeat(64)), "1".repeat(32), "2".repeat(32), initial, old));
    assertThrows(
        NullPointerException.class,
        () -> MorningGateEvidence.stop(null, "1".repeat(32), "2".repeat(32), initial, old));
    assertThrows(
        NullPointerException.class,
        () -> MorningGateEvidence.stop(epoch(boot), "1".repeat(32), "2".repeat(32), null, old));
    assertThrows(
        NullPointerException.class,
        () -> MorningGateEvidence.stop(epoch(boot), "1".repeat(32), "2".repeat(32), initial, null));
    var foreign =
        MorningPreviousBroker.collect(
            BrokerJournalEvidenceTest.BOOT,
            MorningPreviousBrokerTest.cold(),
            new MorningPreviousBrokerTest.Fixture(),
            () -> 1_000_000_000L);
    assertThrows(
        IOException.class,
        () ->
            MorningGateEvidence.stop(
                epoch(boot), "1".repeat(32), "2".repeat(32), initial, foreign));
    var anchor =
        BrokerJournalEvidence.anchor(
            MorningPreviousBrokerTest.STOP.getBytes(StandardCharsets.UTF_8),
            BrokerJournalEvidenceTest.BOOT,
            false);
    assertEquals("BrokerJournalAnchor[redacted]", anchor.toString());
  }

  @Test
  void issstop007FullContentNotJsonMemberOrderAndSurrogateCannotBeNormalized() throws Exception {
    byte[] raw = fixture("issuer-stop-journal.jsonl");
    String original = new String(raw, StandardCharsets.UTF_8);
    String reordered =
        original
            .replace("\"PRIORITY\":\"6\",", "")
            .replace("{\"MESSAGE\"", "{\"PRIORITY\":\"6\",\"MESSAGE\"");
    assertNotEquals(original, reordered);
    String digest = BrokerJournalEvidence.contentSha256(raw);
    assertEquals("e3a86812641c1394772a2e492a72624fb2c504b8b033358558e8ee6d79a74a5e", digest);
    assertEquals(
        digest, BrokerJournalEvidence.contentSha256(reordered.getBytes(StandardCharsets.UTF_8)));
    for (String change :
        List.of(
            original.replace("uptime 2 hours", "uptime 3 hours"),
            original.replace("1790780400000000", "1790780400000001"),
            original.replace("{\"MESSAGE\"", "{\"__SEQNUM\":\"9\",\"MESSAGE\"")))
      assertNotEquals(
          digest, BrokerJournalEvidence.contentSha256(change.getBytes(StandardCharsets.UTF_8)));
    assertThrows(
        IOException.class,
        () ->
            BrokerJournalEvidence.contentSha256(
                original
                    .replace("Using NIO Journal", "Using NIO Journal\\ud800")
                    .getBytes(StandardCharsets.UTF_8)));
    assertThrows(IOException.class, () -> BrokerJournalEvidence.contentSha256(new byte[0]));
    assertThrows(NullPointerException.class, () -> BrokerJournalEvidence.contentSha256(null));
  }
}
