"""Original pure policy15; complete four Sources passive coverage without credential or login operations."""
import pg15368_pure_login_policy_fifteen_pt as original
from reviewed_whole_pure_source_post_v2 import verify_profile

PROFILE={
  "rawFolder": "PG15368-pure-login-policy-fifteen-pt-v1",
  "rawSha256": "6fc42e8a80b710e436d00baa52256dd8aa1ed30b84ff46a1d60af56bb15efc1e",
  "postFolder": "PG15370-pure-login-policy-fifteen-post-v2",
  "sources": {
    "dev/codex/schubert/nk/api/security/LoginUsername": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginUsername.java",
      "sha256": "970b0b15993f72f0881cdf64b00839cb1fdf4f601a6c4b0827e2adc0bb4e0359",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/LoginUsername"
      ],
      "owner": "WBS-P018-09"
    },
    "dev/codex/schubert/nk/api/security/PasswordPolicy": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/PasswordPolicy.java",
      "sha256": "6d8ffe5b35fc04f4056999d5a4a4a73ce6c3103a62b4b2cd87fbcfbeb1c8e608",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/PasswordPolicy"
      ],
      "owner": "WBS-P007-01"
    },
    "dev/codex/schubert/nk/api/security/LoginAttemptState": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptState.java",
      "sha256": "393f52726e83c3ea52fe34c7385c0da413d49306a476894255602fe82880c352",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/LoginAttemptState"
      ],
      "owner": "WBS-P007-01"
    },
    "dev/codex/schubert/nk/api/security/LoginAttemptKind": {
      "path": "src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/security/LoginAttemptKind.java",
      "sha256": "493c8b03e7791a044be87f4fadeb1c7c7c95588aba1174cb38baa0b5a3b56f7b",
      "module": "api",
      "closure": [
        "dev/codex/schubert/nk/api/security/LoginAttemptKind"
      ],
      "owner": "WBS-P007-01"
    }
  },
  "kind": "REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES",
  "originalTestsAlreadyCounted": False
}
if __name__=='__main__':verify_profile(original,PROFILE)
