"""Original Mapper3 full Source passive qualification; synthetic wire only, no authentication."""
import pg15384_auth_response_mapper_three_pt as original
from reviewed_whole_pure_source_post_v2 import verify_profile

PROFILE={
  "rawFolder": "PG15384-auth-response-mapper-three-pt-v1",
  "rawSha256": "f32bdb8fa5350ca001c9454587ba5cc3140500fb92d74672fe7b5b69e83ea492",
  "postFolder": "PG15386-auth-response-mapper-three-post-v2",
  "sources": {
    "dev/codex/schubert/nk/api/security/AuthenticationResponseMapper": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/AuthenticationResponseMapper.java",
      "sha256": "50338664a18e23204f238395928749ee9be293161ae6dc88d0cf3db98aaf23a2",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/AuthenticationResponseMapper"
      ],
      "owner": "WBS-P007-04"
    }
  },
  "kind": "REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES",
  "originalTestsAlreadyCounted": False
}
if __name__=='__main__':verify_profile(original,PROFILE)
