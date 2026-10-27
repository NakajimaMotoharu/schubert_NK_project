package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation;
import dev.codex.schubert.nk.batch.platform.BrokerJournalEvidence;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageRootLayout;
import java.nio.file.Path;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-OPS-OBSDATA-001/002: public value objects only; no real observation or authority. */
final class ObservationValueRedactionTest {
  private static final String PUBLIC_FIELD = "public";

  @Test
  void obsdata001FactsRetainPublicInputsButDiagnosticNeverRendersYamlOrBinding() {
    for (String marker : new String[] {"PUBLIC-DATA-A", "PUBLIC-DATA-B"}) {
      var contents = new ServiceConfigFiles.Contents(marker + " common", marker + " service");
      var roots =
          new StorageRootLayout(
              Path.of("/public-data/asset"),
              Path.of("/public-data/transfer"),
              Path.of("/public-data/backup"),
              Path.of("/public-data/log"),
              Path.of("/public-data/artemis"),
              Path.of("/public-data/staging"));
      var configurations =
          new RootReleaseAdmission.EffectiveConfigurations(
              "a".repeat(64), "b".repeat(64), roots, contents, contents);
      String binding = marker.endsWith("A") ? "d".repeat(64) : "e".repeat(64);
      var value = new RootServiceFacts.Facts(configurations, binding);
      assertSame(configurations, value.configurations());
      assertSame(binding, value.rootsSha256());
      assertEquals("RootServiceFacts[public=<redacted>]", value.toString());
      assertThrows(NullPointerException.class, () -> new RootServiceFacts.Facts(null, binding));
      assertThrows(
          NullPointerException.class, () -> new RootServiceFacts.Facts(configurations, null));
    }
  }

  @Test
  void obsdata002BrokerWrapperRetainsImmutablePublicDataButDiagnosticHasNoNestedDetails() {
    for (String marker : new String[] {"PUBLIC-DATA-A", "PUBLIC-DATA-B"}) {
      var evidence =
          new ArtemisStartupObservation.Evidence(
              Map.of(marker, Map.of(PUBLIC_FIELD, "value")), Map.of(PUBLIC_FIELD, marker),
              Map.of(marker, Map.of(PUBLIC_FIELD, "setting")), Map.of(PUBLIC_FIELD, marker),
              Map.of(marker, Map.of("public-role", Map.of("read", true))), Map.of());
      var journal = new BrokerJournalEvidence.Summary(5, "c".repeat(64));
      var value = new MorningBrokerExecution.Observations(evidence, journal);
      assertSame(evidence, value.values());
      assertSame(journal, value.journal());
      assertEquals("BrokerObservations[actual=<redacted>]", value.toString());
      assertThrows(
          NullPointerException.class, () -> new MorningBrokerExecution.Observations(null, journal));
      assertThrows(
          NullPointerException.class,
          () -> new MorningBrokerExecution.Observations(evidence, null));
    }
  }
}
