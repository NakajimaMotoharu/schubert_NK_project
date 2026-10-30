"""Original question pure UTC-boundary3; full Source passive counters, no Product replay."""
import pg15362_question_time_three_pt as original
from reviewed_whole_pure_source_post_v2 import verify_profile

PROFILE={
  "rawFolder": "PG15362-question-time-three-pt-v1",
  "rawSha256": "509aab8f920fe36b73391b707ad285bc4dbc346842e97965e96e74be53808f22",
  "postFolder": "PG15364-question-time-three-post-v2",
  "sources": {
    "dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata.java",
      "sha256": "c62cea835ecc09e2e811cdf704d2e8c562b207f802a50c8f1789868fff3cfc1c",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/application/question/QuestionCommandMetadata"
      ],
      "owner": "WBS-P011-03"
    }
  },
  "kind": "REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES",
  "originalTestsAlreadyCounted": False
}
if __name__=='__main__':verify_profile(original,PROFILE)
