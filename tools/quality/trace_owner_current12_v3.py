"""PG-D937 exact current12 Test candidates; no runtime identity/authority or original cost changes."""
from trace_owner_current11_v2 import canonical as previous_canonical

SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
DECISION='PG-D937'
RULES={
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/bootstrap/ApiStartupInputsTest.java": {
    "sha256": "3cecaf9d04173e9b973683a95f94a566ac47506654cad33170134814a54be3d5",
    "owner": "WBS-P018-05",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs.java"
    ],
    "tokens": [
      "new ApiStartupInputs(",
      "opsApiInput001",
      "opsApiInput004"
    ],
    "originalTests": 4,
    "post": "PG15342-api-startup-inputs-four-post-v2",
    "postSha256": "22f14eebdb3284e51c67d9b05b4ee8eaf4b01784006a76cae6d73b071c98bcb3",
    "record": "2896",
    "reason": "SS342343 startup composition; nonsecret parser/location are shared references, not reassigned"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxPolicyTest.java": {
    "sha256": "ddd94d17ece3c2ed0861cd21f463920ed5972c39102f60f147ee8c45f2e5abc6",
    "owner": "WBS-P006-02",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxRetrySchedule.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxRetrySchedule.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDestination.java"
    ],
    "tokens": [
      "OutboxDestination.fromAddress(",
      "OutboxRetrySchedule.INSTANCE.",
      "retryJitterUsesIndependent"
    ],
    "originalTests": 4,
    "post": "PG15348-current-outbox-thirteen-post-v2",
    "postSha256": "772cfdd88f5a604232c3aa7c184edc4bfcc9b7f42a3b408a2e130725c18d59d7",
    "record": "2898",
    "reason": "SS324332 destination and application retry are the two explicit same-owner subjects"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxModelTest.java": {
    "sha256": "61827ab290718de21cf8f4c6ec33758d484af5a12638c33efff28d6eaba5fe18",
    "owner": "WBS-P006-02",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxEntry.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxEntry.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxRequest.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxIntegrityException.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxSendException.java"
    ],
    "tokens": [
      "new OutboxEntry(",
      "new OutboxRequest(",
      "reportAndIntegrityExceptionsCoverEveryInvariant"
    ],
    "originalTests": 4,
    "post": "PG15348-current-outbox-thirteen-post-v2",
    "postSha256": "772cfdd88f5a604232c3aa7c184edc4bfcc9b7f42a3b408a2e130725c18d59d7",
    "record": "2898",
    "reason": "SS324331332 immutable outbox value/profile family; all explicit subjects share P00602"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDlqMetadataTest.java": {
    "sha256": "54683e12417a392faffe354584412111e7713da8a17d3b4ac0d4428358c6c47c",
    "owner": "WBS-P006-02",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDlqMetadata.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDlqMetadata.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxEntry.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxRequest.java"
    ],
    "tokens": [
      "new OutboxDlqMetadata(",
      "exactDestinationSpecificProfile",
      "boundsActualCount"
    ],
    "originalTests": 2,
    "post": "PG15348-current-outbox-thirteen-post-v2",
    "postSha256": "772cfdd88f5a604232c3aa7c184edc4bfcc9b7f42a3b408a2e130725c18d59d7",
    "record": "2898",
    "reason": "SSC155 SS331324 original DLQ metadata and exact outbound profile; not broker runtime"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReportBoundaryTest.java": {
    "sha256": "19d79b9b2d1c49b87b1d56df39f6bd4d37103403cca4311541bfdf741e440ffc",
    "owner": "WBS-P006-02",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.java"
    ],
    "tokens": [
      "new OutboxDispatchReport(",
      "mathematicalSums",
      "rejectsEveryNegativeComponent"
    ],
    "originalTests": 3,
    "post": "PG15348-current-outbox-thirteen-post-v2",
    "postSha256": "772cfdd88f5a604232c3aa7c184edc4bfcc9b7f42a3b408a2e130725c18d59d7",
    "record": "2898",
    "reason": "SS324332 exact report count and independent integer overflow oracle"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionCommandTimeBoundaryTest.java": {
    "sha256": "0d2b3fd7a094c51c4009b96c5dfa65081d0924810ce6aecd0dc2c6198c4e4ef0",
    "owner": "WBS-P011-03",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata.java"
    ],
    "tokens": [
      "new QuestionCommandMetadata(",
      "lowerBoundPreservesFloor",
      "preEpochTruncationUsesUtcFloor"
    ],
    "originalTests": 3,
    "post": "PG15364-question-time-three-post-v2",
    "postSha256": "fd66524cfa291b77589113f626484ea540a6fac425a295b222b986681c1f4e0c",
    "record": "2902",
    "reason": "SS332351 command UTC metadata, not generic clock infrastructure"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/LoginUsernameTest.java": {
    "sha256": "1fdb742c0aab4c1be6ce90ca68e2f357c7030a7d5a916df34f9f91a61bfccf00",
    "owner": "WBS-P018-09",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginUsername.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginUsername.java"
    ],
    "tokens": [
      "new LoginUsername(",
      "maximumScalar",
      "Locale.setDefault(original)"
    ],
    "originalTests": 3,
    "post": "PG15370-pure-login-policy-fifteen-post-v2",
    "postSha256": "330c621dc195273b9ba290a7b72b8658b0fd237c42bf2d2c277e7f0ee00a0df2",
    "record": "2904",
    "reason": "SS314SSC014 subject LoginUsername; keep original baseline P01809, never infer P007 from present engineering group"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/PasswordPolicyTest.java": {
    "sha256": "fe466645fdf4739e44df74b3197c1b55631a5b2b0c423d526f005468ac87fc55",
    "owner": "WBS-P007-01",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/PasswordPolicy.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/PasswordPolicy.java"
    ],
    "tokens": [
      "policy.normalizeForLogin(",
      "new char[input.length]",
      "nfcSupplementary"
    ],
    "originalTests": 3,
    "post": "PG15370-pure-login-policy-fifteen-post-v2",
    "postSha256": "330c621dc195273b9ba290a7b72b8658b0fd237c42bf2d2c277e7f0ee00a0df2",
    "record": "2904",
    "reason": "SS314 UI226 pure password input normalization/consumption policy, no hashing or actual credential"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/LoginAttemptStateTest.java": {
    "sha256": "8de7da1fea134d4f1973ac003287dccee971dad697859f6014f0a32743930391",
    "owner": "WBS-P007-01",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptState.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptState.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptKind.java"
    ],
    "tokens": [
      "LoginAttemptState.empty(",
      "currentObservedWindowEndpointVector",
      "retryAfterCeils"
    ],
    "originalTests": 5,
    "post": "PG15370-pure-login-policy-fifteen-post-v2",
    "postSha256": "330c621dc195273b9ba290a7b72b8658b0fd237c42bf2d2c277e7f0ee00a0df2",
    "record": "2904",
    "reason": "SS314 SSC009 immutable failure window/lock policy and same-owner closed thresholds"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/LoginAttemptSequenceTest.java": {
    "sha256": "92d8a79ea0e8089bea9822fd77560998184f0e032bf7f94c5317e43454d3975f",
    "owner": "WBS-P007-01",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptState.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptState.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptKind.java"
    ],
    "tokens": [
      "LoginAttemptState.empty(",
      "everyRetryAfterSecondEdge",
      "everyLockedRetry"
    ],
    "originalTests": 4,
    "post": "PG15370-pure-login-policy-fifteen-post-v2",
    "postSha256": "330c621dc195273b9ba290a7b72b8658b0fd237c42bf2d2c277e7f0ee00a0df2",
    "record": "2904",
    "reason": "SS314 original timed policy histories, same baseline subject as StateTest, no SQL/real login"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthenticationResponseMapperTest.java": {
    "sha256": "d42472923a2399840df438ba00f9cf6e46619bc4fff1f567a8a46e99c98116ec",
    "owner": "WBS-P007-04",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationResponseMapper.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationResponseMapper.java"
    ],
    "tokens": [
      "mapper.login(",
      "put(expected, 133,",
      "assertArrayEquals(expected, actual.copyData())"
    ],
    "originalTests": 3,
    "post": "PG15386-auth-response-mapper-three-post-v2",
    "postSha256": "5aefc24bbc8bbd2ecb6a36bafe8ed439ee3208da641771c8e8787efe54d3b59b",
    "record": "2908",
    "reason": "UI234/SS312322314 auth response wire mapper is primary; actor/context DTO and protocol codecs are shared references at extra0"
  },
  "src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AuthorizationServiceTest.java": {
    "sha256": "f290e044393ebbdd7778fdf474aaff8a211987c8f9c7686cba60591ef1aa465b",
    "owner": "WBS-P007-03",
    "anchor": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthorizationService.java",
    "subjects": [
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthorizationService.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthorizationException.java",
      "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticatedActor.java"
    ],
    "tokens": [
      "service.requireNotificationOwner(",
      "service.requireQuestionOwner(",
      "actorOwnerAndErrorNull"
    ],
    "originalTests": 2,
    "post": "PG15392-pure-authorization-two-post-v2",
    "postSha256": "baa867dc17450ec2c1d8e85d62abc23a7f6ce86543fda6a5d0136b16d622d495",
    "record": "2910",
    "reason": "SS314 section9 application authorization policy/closed denial/actor invariant, all primary subjects same P00703"
  }
}

def canonical(path,logical):
    if path in logical or path not in RULES:
        return previous_canonical(path,logical)
    rule=RULES[path];anchor=logical.get(rule['anchor'])
    if anchor is None or anchor.get('path')!=rule['anchor'] or anchor.get('owner')!=rule['owner'] or anchor.get('costOwner')!=rule['owner']:
        raise ValueError('PG-D937 explicit original subject anchor/owner/cost pair required')
    return dict(canonicalOwner=rule['owner'],canonicalCostOwner=rule['owner'],ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='PGD937_EXACT_CURRENT12_REVIEWED_SUBJECT_CONTRACT_NOT_CHANGE_OWNER; ORIGINAL_SCOPE_COST_RUN_AND_ACCEPTANCE_UNCHANGED')
