package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.google.gson.Gson;
import dev.codex.schubert.nk.batch.mq.ArtemisQueuePressureClient;
import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation;
import dev.codex.schubert.nk.batch.platform.BrokerJournalEvidence;
import dev.codex.schubert.nk.batch.repository.BatchRun;
import dev.codex.schubert.nk.batch.repository.MaintenanceActivation;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.Test;

/** SSC130/ISSBROKER002: persisted independent SS321/343 literal vectors, no expected encoder. */
final class MorningGateEvidenceBrokerTest {
  private static final StartupPermitRecords.Epoch EPOCH =
      new StartupPermitRecords.Epoch(
          StartupPermitRecords.State.INVALID,
          UUID.fromString("11111111-2222-4333-8444-555555555555"),
          UUID.fromString("22222222-2222-4333-8444-555555555555"),
          new MaintenanceActivation(
              new BatchRun(
                  UUID.fromString("33333333-2222-4333-8444-555555555555"),
                  Instant.parse("2026-09-27T15:00:00Z")),
              UUID.fromString("44444444-2222-4333-8444-555555555555")),
          Optional.empty());
  private static final BrokerJournalEvidence.Summary JOURNAL =
      new BrokerJournalEvidence.Summary(7, "a".repeat(64));

  private static byte[] resource(String name) throws IOException {
    try (var stream =
        Objects.requireNonNull(
            MorningGateEvidenceBrokerTest.class.getResourceAsStream("/ops/" + name))) {
      return stream.readAllBytes();
    }
  }

  private static ArtemisStartupObservation.Evidence fixture() throws IOException {
    return Objects.requireNonNull(
        new Gson()
            .fromJson(
                new String(resource("issuer-broker-input.json"), StandardCharsets.UTF_8),
                ArtemisStartupObservation.Evidence.class));
  }

  private static byte[] encode(
      ArtemisStartupObservation.Evidence actual, BrokerJournalEvidence.Summary journal)
      throws IOException {
    return MorningGateEvidence.broker(EPOCH, "1".repeat(32), "2".repeat(32), actual, journal);
  }

  @Test
  void issBroker002CompleteLiteralFrameAndIndependentDataCopies() throws Exception {
    byte[] expected = resource("issuer-broker-golden.txt");
    assertEquals(19715, expected.length);
    assertArrayEquals(expected, encode(fixture(), JOURNAL));
    byte[] actual = encode(fixture(), JOURNAL);
    actual[0] = 'X';
    assertArrayEquals(expected, encode(fixture(), JOURNAL));
  }

  @Test
  void issBroker003MissingAdditionalFieldAndWrongAddressNeverFormGate() throws Exception {
    var good = fixture();
    for (int slot = 0; slot < 4; slot++) {
      var broker = new HashMap<>(good.broker());
      var topology = new HashMap<>(good.topology());
      var settings = new HashMap<>(good.settings());
      var acceptor = new HashMap<>(good.acceptor());
      if (slot == 0) broker.remove("name");
      if (slot == 1) topology.remove("nk.expiry");
      if (slot == 2) settings.put("unknown", good.settings().get("nk.expiry"));
      if (slot == 3) acceptor.put("unknown", "value");
      var wrong =
          new ArtemisStartupObservation.Evidence(
              topology, broker, settings, acceptor, good.roles(), good.pressure());
      assertThrows(IOException.class, () -> encode(wrong, JOURNAL));
    }
    for (boolean topologySlot : List.of(true, false)) {
      var topology = new HashMap<>(good.topology());
      var settings = new HashMap<>(good.settings());
      var fields =
          new HashMap<>(topologySlot ? topology.get("nk.expiry") : settings.get("nk.expiry"));
      fields.remove(topologySlot ? "durable" : "maxSizeBytes");
      (topologySlot ? topology : settings).put("nk.expiry", fields);
      var wrong =
          new ArtemisStartupObservation.Evidence(
              topology, good.broker(), settings, good.acceptor(), good.roles(), good.pressure());
      assertThrows(IOException.class, () -> encode(wrong, JOURNAL));
    }
  }

  @Test
  void issBroker004EveryRoleMatchNameAndPermissionAndCriticalPressureAreChecked() throws Exception {
    var good = fixture();
    for (int slot = 0; slot < 4; slot++) {
      var roles = new HashMap<>(good.roles());
      if (slot == 0) roles.remove("mops.#");
      if (slot == 1) roles.put("mops.#", Map.of());
      if (slot == 2)
        roles.put("mops.#", Map.of("unknown", good.roles().get("mops.#").get("nk_ops")));
      if (slot == 3) roles.put("mops.#", Map.of("nk_ops", Map.of("send", true)));
      var wrong =
          new ArtemisStartupObservation.Evidence(
              good.topology(),
              good.broker(),
              good.settings(),
              good.acceptor(),
              roles,
              good.pressure());
      assertThrows(IOException.class, () -> encode(wrong, JOURNAL));
    }
    for (boolean critical : List.of(false, true)) {
      var pressure = new HashMap<>(good.pressure());
      if (critical)
        pressure.put(
            "nk.expiry",
            new ArtemisQueuePressureClient.Value(
                5000, 0, ArtemisQueuePressureClient.Pressure.CRITICAL));
      else pressure.remove("nk.expiry");
      var wrong =
          new ArtemisStartupObservation.Evidence(
              good.topology(),
              good.broker(),
              good.settings(),
              good.acceptor(),
              good.roles(),
              pressure);
      assertThrows(IOException.class, () -> encode(wrong, JOURNAL));
    }
    for (var journal :
        List.of(
            new BrokerJournalEvidence.Summary(0, "a".repeat(64)),
            new BrokerJournalEvidence.Summary(7, "A".repeat(64))))
      assertThrows(IOException.class, () -> encode(good, journal));
    assertThrows(NullPointerException.class, () -> encode(good, null));
    assertThrows(NullPointerException.class, () -> encode(null, JOURNAL));
  }
}
