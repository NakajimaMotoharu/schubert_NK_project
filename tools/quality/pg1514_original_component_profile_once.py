"""One fresh readonly owner/tenRef component profile, preserve any unknown scope."""
import inspect
import pg1481_partial_original_profile as prior
from pg1512_original_component_profile_sources import CLASS,TOOLS,SAVE

def main():
 raw=inspect.getsource(prior.main)
 for a,b in [('pg1481-partial-original-profile-v1',SAVE),('pg1478-partial-profile-frozen-v1.safe.json','pg1512-original-component-frozen-v1.safe.json'),('pg1478-partial-original-tools-v1',TOOLS),('Pg1478PartialOriginalProfile',CLASS),('PG1481-partial-original-profile-v1','PG1514-original-component-profile-v1')]:
  assert a in raw;raw=raw.replace(a,b)
 marker=TOOLS+':/opt/schubert-nk/current/api/api.jar'
 assert marker in raw;raw=raw.replace(marker,TOOLS+':/var/lib/pgpt-s1-preservation/'+TOOLS+'/original-io-profile.jar:/opt/schubert-nk/current/api/api.jar')
 ns={**prior.__dict__,'OUTNAME':'pg1513-original-component-stage-v1','valid_receipt':lambda data:type(data)is bytes and data==b'PG1292 STAGE PINNED_SIGNATURE_VERIFIED\nPG1292 STAGE FULL_CANDIDATE_BOM_VERIFIED\nPG1514_DONE readonlyProfile=true allScopesReturnedNormally=true originalRetiredOrAuthorityIssued=false\n'}
 exec(compile(raw,'<new actual readonly profile transport>','exec'),ns);return ns['main']()
if __name__=='__main__':raise SystemExit(main())
