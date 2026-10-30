"""Passive full eight Source qualification of original whole13; no Product replay."""
import pg15346_current_outbox_thirteen_pt as original
from reviewed_whole_pure_source_post_v2 import verify_profile

PROFILE={
  "rawFolder": "PG15346-current-outbox-thirteen-pt-v1",
  "rawSha256": "c219fed1f5ef50e0d03a8ea1f6f3496d890c65ffb2d5f27c921745d03738e29d",
  "postFolder": "PG15348-current-outbox-thirteen-post-v2",
  "sources": {
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxDestination": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDestination.java",
      "sha256": "8ab0216109c17c6d5cf96039b6ac968dd2cb6fc401c2f93b0f92cc08c3ed8e80",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxDestination"
      ],
      "owner": "WBS-P006-02"
    },
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxRetrySchedule": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxRetrySchedule.java",
      "sha256": "f565b0413b5e262907e209f523915e3050beb7062fec3b369d178124c58e8854",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxRetrySchedule"
      ],
      "owner": "WBS-P006-02"
    },
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxEntry": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxEntry.java",
      "sha256": "09bb3b7767c6c09c5c8685088a7ef0494898aedc478307cbd44a14cfa7dd0ef4",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxEntry"
      ],
      "owner": "WBS-P006-02"
    },
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxRequest": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxRequest.java",
      "sha256": "564190205500c14866882d60d36d654276562f38593229ef85c14da0ef7ab463",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxRequest"
      ],
      "owner": "WBS-P006-02"
    },
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxDlqMetadata": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDlqMetadata.java",
      "sha256": "ef0be1f11629947394710ce2f537567c19401737e2329a3d54719471ea5b7f53",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxDlqMetadata"
      ],
      "owner": "WBS-P006-02"
    },
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport.java",
      "sha256": "c9ba13a64c580fea33b744134a5534d44142233f72a28c40d5cc0442e2fc472f",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatchReport"
      ],
      "owner": "WBS-P006-02"
    },
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxIntegrityException": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxIntegrityException.java",
      "sha256": "56a5f3af8ccf296acef3aa0991920755756862223d6ea1c111e248448d63941a",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxIntegrityException"
      ],
      "owner": "WBS-P006-02"
    },
    "dev/codex/schubert/nk/api/messaging/outbound/OutboxSendException": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxSendException.java",
      "sha256": "b2dac8539f303d4b2677bf78369f1bc9c77ad5c37c863633b968f187adb8a210",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/messaging/outbound/OutboxSendException"
      ],
      "owner": "WBS-P006-02"
    }
  },
  "kind": "REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES",
  "originalTestsAlreadyCounted": False
}
if __name__=='__main__':verify_profile(original,PROFILE)
