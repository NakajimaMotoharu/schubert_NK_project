"""PG-D936 exact current11 artifact responsibility candidates; never OS/runtime ownership or permission."""
from trace_owner_join import canonical as legacy_canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
DECISION='PG-D936'
RULES={
  "src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfigTest.java": {
    "sha256": "c48aaae03b6901d3511ac2cda416c0f184044b6baefcf307d64c69997937a63c",
    "owner": "WBS-P018-01",
    "anchor": "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfig.java",
    "subjects": [
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiNonSecretConfig.java"
    ],
    "tokens": [
      "ApiNonSecretConfig.parse(",
      "opsApiCfg001",
      "GOLDEN"
    ],
    "originalTests": 7,
    "post": "PG15224-nonsecret-config-fourteen-post-v1",
    "postSha256": "5d714d963f1183844fb41f46e41ebd2e3ecece0a37d3c6d7700ca18f9a218c53",
    "record": "2870",
    "reason": "SS343 §4–5; nonsecret API parser is the explicit subject"
  },
  "src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfigTest.java": {
    "sha256": "d56e00afaac0bfe0dd269d689b10df907a0f04a31e6021837a180ccea7f0b78b",
    "owner": "WBS-P018-01",
    "anchor": "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfig.java",
    "subjects": [
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebNonSecretConfig.java"
    ],
    "tokens": [
      "WebNonSecretConfig.parse(",
      "opsWebCfg001",
      "GOLDEN"
    ],
    "originalTests": 7,
    "post": "PG15224-nonsecret-config-fourteen-post-v1",
    "postSha256": "5d714d963f1183844fb41f46e41ebd2e3ecece0a37d3c6d7700ca18f9a218c53",
    "record": "2870",
    "reason": "SS343 §4–5; nonsecret Web parser is the explicit subject"
  },
  "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java": {
    "sha256": "6ae561e25cfcdcce0b6b61641b3b2afd7867cf0eaa646059c8b3606dd915e28b",
    "owner": "WBS-P018-05",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java"
    ],
    "tokens": [
      "final class ApiStopBudget",
      "void begin()",
      "long remainingNanos()"
    ],
    "originalTests": 0,
    "post": "PG15242-api-stop-budget-eighteen-post-v1",
    "postSha256": "242a987a6b39aa0365fa0b479e41ffe12b6b5d01cfc9e49c4f6e3a7945da1001",
    "record": "2874",
    "reason": "SS342/351; baseline API lifetime owns first-stop budget and delegates begin/remaining"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudgetTest.java": {
    "sha256": "50062a11dda9bac2eac52fa71a92ab75cd8b8bcbcd499c2f1a8fb8c077fcb15c",
    "owner": "WBS-P018-05",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessLifetime.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStopBudget.java"
    ],
    "tokens": [
      "new ApiStopBudget(",
      "apiStop001",
      "apiStop018"
    ],
    "originalTests": 18,
    "post": "PG15242-api-stop-budget-eighteen-post-v1",
    "postSha256": "242a987a6b39aa0365fa0b479e41ffe12b6b5d01cfc9e49c4f6e3a7945da1001",
    "record": "2874",
    "reason": "The explicit subject is the API lifetime first-stop budget, not generic clock/G03"
  },
  "src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedServiceExecArgumentsTest.java": {
    "sha256": "a6661ae17848c62d35fafed8804e220c5b673bb4437c2f5e73ce81c64651b569",
    "owner": "WBS-P018-04",
    "anchor": "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedServiceExecArguments.java",
    "subjects": [
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedServiceExecArguments.java"
    ],
    "tokens": [
      "new FixedServiceExecArguments(",
      "rexec001",
      "rexec193"
    ],
    "originalTests": 5,
    "post": "PG15261-fixed-service-argv-five-post-v2",
    "postSha256": "330db5435a282e0f6d4c72af0f536871871f2ad20f7fc0760b91bbeebba9a6c8",
    "record": "2878",
    "reason": "SS342 §4.2 fixed ordinary argv policy, not an exec operation"
  },
  "src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfileTest.java": {
    "sha256": "0896cf1e70a529ccb40d31e6a9d48b6298ea4694060de8a7a4eb0edabb7c1c88",
    "owner": "WBS-P018-08",
    "anchor": "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile.java",
    "subjects": [
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile.java"
    ],
    "tokens": [
      "FixedNativeCoverageProfile.parse(",
      "nc193001",
      "nc193005"
    ],
    "originalTests": 5,
    "post": "PG15278-profile-terminal-fourteen-post-v1",
    "postSha256": "0dde7b7d8ff705d5466522d43072e16f294838a5ec4cbfdc144c7f5e33af79f5",
    "record": "2882",
    "reason": "SSC193 profile parsing and role labels; runtime/native authority remains separate"
  },
  "src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/TerminalNativeCoverageProfileTest.java": {
    "sha256": "9d34bf77fe53febec5e7da54557428516a81e8c5289ba68c95aa2799da49df2f",
    "owner": "WBS-P018-08",
    "anchor": "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile.java",
    "subjects": [
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile.java",
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint.java"
    ],
    "tokens": [
      "FixedNativeCoverageProfile.parseTerminal(",
      "identity(f.subject())",
      "nc196004"
    ],
    "originalTests": 4,
    "post": "PG15278-profile-terminal-fourteen-post-v1",
    "postSha256": "0dde7b7d8ff705d5466522d43072e16f294838a5ec4cbfdc144c7f5e33af79f5",
    "record": "2882",
    "reason": "SSC196 terminal profiles/checkpoint are primary; Identity/Map fixture is a shared P01804 reference, cost0"
  },
  "src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageTerminalTest.java": {
    "sha256": "53a37549322bf4cd8e38afb74844a3e7d8d10f0518afe495af5792dc0c009113",
    "owner": "WBS-P018-08",
    "anchor": "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageTerminal.java",
    "subjects": [
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageTerminal.java",
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint.java",
      "src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageProfile.java"
    ],
    "tokens": [
      "new FixedNativeCoverageTerminal(",
      "close743001",
      "close743005"
    ],
    "originalTests": 5,
    "post": "PG15278-profile-terminal-fourteen-post-v1",
    "postSha256": "0dde7b7d8ff705d5466522d43072e16f294838a5ec4cbfdc144c7f5e33af79f5",
    "record": "2882",
    "reason": "SSC234 same-owner terminal/closing control contract, not actual native export"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiAdmittedConfigurationTest.java": {
    "sha256": "63d82faa7692112a050e39ea6a15418f7de3edfb252f059f0220310dd66902cf",
    "owner": "WBS-P018-05",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java"
    ],
    "tokens": [
      "ApiProcessMain.admittedConfiguration(",
      "ssc301001",
      "ssc301008"
    ],
    "originalTests": 8,
    "post": "PG15302-api-config-readiness-eleven-post-v1",
    "postSha256": "ff665193ddb62c0ed11afac98a9bc5465167ad5348552b2d1d093951de59b92b",
    "record": "2886",
    "reason": "SSC301 API Main data port is primary; parser/location/configuration record are shared fixtures"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiReadinessPredicateTest.java": {
    "sha256": "f6331acd7c4afdfa0ff027d3020784605347149b75c3526118c20a8270e67dcc",
    "owner": "WBS-P018-05",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiProcessMain.java"
    ],
    "tokens": [
      "ApiProcessMain.applicationReadiness(",
      "ApiProcessMain.runtimeReadiness(",
      "health003"
    ],
    "originalTests": 3,
    "post": "PG15302-api-config-readiness-eleven-post-v1",
    "postSha256": "ff665193ddb62c0ed11afac98a9bc5465167ad5348552b2d1d093951de59b92b",
    "record": "2886",
    "reason": "API Main readiness predicate is primary; no native promotion/admission is being qualified"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/database/RequiredColumnTest.java": {
    "sha256": "27d0c6689cca24bba7735330ab00b8211a89475a3bc23dae04b77f9ee11f118a",
    "owner": "WBS-P004-05",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/RequiredColumn.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/database/RequiredColumn.java"
    ],
    "tokens": [
      "RequiredColumn.requireValue(",
      "requiredValuesRetainIdentityAndNullFailsWithSqlState"
    ],
    "originalTests": 1,
    "post": "PG15309-required-column-one-post-v2",
    "postSha256": "e26d863768b8659de2840b77421fd2f675d66a5dd9418b91a1796e691853d632",
    "record": "2888",
    "reason": "DAT009/SS331332354 required JDBC-result value boundary, not a JDBC connection or business query"
  }
}

def canonical(path,logical):
    # A real original logical row always wins; never rewrite original 941 ownership/costs.
    if path in logical or path not in RULES:
        return legacy_canonical(path,logical)
    rule=RULES[path]
    anchor=logical.get(rule['anchor'])
    if anchor is None or anchor.get('path')!=rule['anchor'] or anchor.get('owner')!=rule['owner'] or anchor.get('costOwner')!=rule['owner']:
        raise ValueError('PG-D936 explicit original subject anchor/owner/cost pair required')
    return dict(canonicalOwner=rule['owner'],canonicalCostOwner=rule['owner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='PGD936_EXACT_CURRENT11_REVIEWED_SUBJECT_CONTRACT_NOT_CHANGE_OWNER; ORIGINAL_SCOPE_COST_RUN_AND_ACCEPTANCE_UNCHANGED')
