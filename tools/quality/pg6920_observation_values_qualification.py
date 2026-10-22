"""Actual branchless record counters, no synthetic branch percentage or runtime authority."""
from pathlib import Path
import pg6916_observation_values_selected as profile
from pg5940_private_lock_compile import BASE
from unchanged_selected_evidence import qualify

QSHA = '32118884012095e87885c0246f083a27193f2d56394842e8459eed4d770145f4'
REASON = 'Public data record constructor uses Objects.requireNonNull and toString returns fixed literal; actual class XML has no BRANCH counter, no new exclusion/filter.'


def main():
    return qualify(profile, 'PG6918-observation-values-original-v1', QSHA, (17, 9),
      BASE / 'PG6890-current4213-cases/qualification.json', '80ad328f6e4f20d2f53f0e6ac4c314c1f698842a7b9b031b14d47592d19123ce',
      {'batch:dev/codex/schubert/nk/batch/file/RootServiceFacts$Facts.class': REASON,
       'batch:dev/codex/schubert/nk/batch/file/MorningBrokerExecution$Observations.class': REASON},
      {profile.TEST: {
       'obsdata001FactsRetainPublicInputsButDiagnosticNeverRendersYamlOrBinding': 'PT-OPS-OBSDATA-001',
       'obsdata002BrokerWrapperRetainsImmutablePublicDataButDiagnosticHasNoNestedDetails': 'PT-OPS-OBSDATA-002'}},
      'PG6920-observation-values-qualification-v1', Path(__file__))


if __name__ == '__main__':
    main()
