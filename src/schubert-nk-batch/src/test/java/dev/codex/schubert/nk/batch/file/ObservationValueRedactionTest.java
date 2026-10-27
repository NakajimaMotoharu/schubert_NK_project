package dev.codex.schubert.nk.batch.file;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

import dev.codex.schubert.nk.batch.mq.ArtemisStartupObservation;
import dev.codex.schubert.nk.batch.platform.BrokerJournalEvidence;
import dev.codex.schubert.nk.batch.platform.RootReleaseAdmission;
import dev.codex.schubert.nk.storage.ServiceConfigFiles;
import dev.codex.schubert.nk.storage.StorageRootLayout;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** PT-OPS-OBSDATA-001..004: public value objects only; no real observation or authority. */
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

  @Test
  void obsdata003ConfigurationAndJournalDiagnosticsHideIndependentPublicCanaries() {
    for (String marker : List.of("PUBLIC-RECORD-CANARY-ALPHA", "PUBLIC-RECORD-CANARY-BETA")) {
      String apiDigest = "a".repeat(64);
      String webDigest = "b".repeat(64);
      String journalDigest = "c".repeat(64);
      String commonYaml = marker + " COMMON-YAML-CANARY";
      String serviceYaml = marker + " SERVICE-YAML-CANARY";
      var contents = new ServiceConfigFiles.Contents(commonYaml, serviceYaml);
      var configurations =
          new RootReleaseAdmission.EffectiveConfigurations(
              apiDigest, webDigest, diagnosticRoots(marker), contents, contents);
      String configurationText = configurations.toString();
      String journalText = new BrokerJournalEvidence.Summary(5, journalDigest).toString();
      assertEquals("EffectiveConfigurations[non-secret=<redacted>]", configurationText);
      assertEquals("BrokerJournalSummary[redacted]", journalText);
      for (String forbidden :
          List.of(marker, apiDigest, webDigest, journalDigest, commonYaml, serviceYaml)) {
        assertFalse(configurationText.contains(forbidden));
        assertFalse(journalText.contains(forbidden));
      }
      for (String leaf : List.of("asset", "transfer", "backup", "log", "artemis", "staging")) {
        String absolutePath = "/public-diagnostic/" + marker + "/" + leaf;
        assertFalse(configurationText.contains(absolutePath));
        assertFalse(journalText.contains(absolutePath));
      }
    }
  }

  @Test
  void obsdata004NonNullConfigurationValuesRejectEachMissingFieldBeforeOwnership() {
    String apiDigest = "a".repeat(64);
    String webDigest = "b".repeat(64);
    var roots = diagnosticRoots("PUBLIC-NULL-FIELD-CANARY");
    String commonYaml = "PUBLIC-NULL-COMMON";
    String serviceYaml = "PUBLIC-NULL-SERVICE";
    var contents = new ServiceConfigFiles.Contents(commonYaml, serviceYaml);
    for (int missing = 0; missing < 5; missing++) {
      int field = missing;
      assertThrows(
          NullPointerException.class,
          () ->
              new RootReleaseAdmission.EffectiveConfigurations(
                  field == 0 ? null : apiDigest,
                  field == 1 ? null : webDigest,
                  field == 2 ? null : roots,
                  field == 3 ? null : contents,
                  field == 4 ? null : contents));
    }
    assertThrows(
        NullPointerException.class, () -> new ServiceConfigFiles.Contents(null, serviceYaml));
    assertThrows(
        NullPointerException.class, () -> new ServiceConfigFiles.Contents(commonYaml, null));
  }

  private static StorageRootLayout diagnosticRoots(String marker) {
    String prefix = "/public-diagnostic/" + marker + "/";
    return new StorageRootLayout(
        Path.of(prefix + "asset"),
        Path.of(prefix + "transfer"),
        Path.of(prefix + "backup"),
        Path.of(prefix + "log"),
        Path.of(prefix + "artemis"),
        Path.of(prefix + "staging"));
  }
}
