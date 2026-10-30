"""Original authorization2 complete three pure Sources; no authentication, DB or graph."""
import pg15390_pure_authorization_two_pt as original
from reviewed_whole_pure_source_post_v2 import verify_profile

PROFILE={
  "rawFolder": "PG15390-pure-authorization-two-pt-v1",
  "rawSha256": "a089e2fca2e137e95e64431b841ab6af80bd93d4f2c025e0e52f5d77a1c6a122",
  "postFolder": "PG15392-pure-authorization-two-post-v2",
  "sources": {
    "dev/codex/schubert/nk/api/security/AuthorizationService": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthorizationService.java",
      "sha256": "8aa174fe39b5d71afe07443beb133063418edd1de095c16b3e288ac26d1faebb",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/AuthorizationService"
      ],
      "owner": "WBS-P007-03"
    },
    "dev/codex/schubert/nk/api/security/AuthorizationException": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthorizationException.java",
      "sha256": "d380238db3295ef027da57f23eb88cc7ade4c319aefe5f73d7bd71392bce4ffa",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/AuthorizationException"
      ],
      "owner": "WBS-P007-03"
    },
    "dev/codex/schubert/nk/api/security/AuthenticatedActor": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticatedActor.java",
      "sha256": "830a87635d2782354fe9c03e5d7612a2ab88364cdc31157b501fbf7baf361469",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/AuthenticatedActor"
      ],
      "owner": "WBS-P007-03"
    }
  },
  "kind": "REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES",
  "originalTestsAlreadyCounted": False
}
if __name__=='__main__':verify_profile(original,PROFILE)
