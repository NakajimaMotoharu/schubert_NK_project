"""Original API inputs4 passive full two-class Source coverage; no Product replay."""
import pg15340_api_startup_inputs_four_pt as original
from reviewed_whole_pure_source_post_v2 import verify_profile

PROFILE={
 'rawFolder':'PG15340-api-startup-inputs-four-pt-v1',
 'rawSha256':'40ecce1446324f21b6c9f260aa102dcf6d57409a0479c0e7f38c50c6054a9fc7',
 'postFolder':'PG15342-api-startup-inputs-four-post-v2',
 'sources':{'dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs':{
  'path':'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs.java',
  'sha256':'e6d69bfa6580bba22f2558c37d0ab43799ee5cc515e00a8d64370168333648e6',
  'module':'api',
  'closure':['dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs','dev/codex/schubert/nk/api/bootstrap/ApiStartupInputs$Values'],
  'owner':'WBS-P018-05'}},
 'kind':'REVIEWED_WHOLE_PURE_VALUES_NO_RESOURCE_FIXTURES',
 'originalTestsAlreadyCounted':False}
if __name__=='__main__':verify_profile(original,PROFILE)
