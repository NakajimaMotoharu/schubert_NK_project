"""Fresh frozen namespaces after BUG1121; never hotpatch/reuse failed profile slot."""
import argparse
import inspect
import pg1512_original_component_profile_compile as compiler
import pg1513_original_component_stage as stage
import pg1514_original_component_profile_once as profile
import pg1512_original_component_profile_sources as sources

TOOLS='pg1517-original-component-tools-v2'
SAVE='pg1519-original-component-profile-v2'
CLASS='Pg1517OriginalComponentProfile'
def remap(raw):
 return raw.replace(sources.TOOLS,TOOLS).replace(sources.SAVE,SAVE).replace(sources.CLASS,CLASS).replace('pg1512_original_component_refs.py','pg1517_original_component_refs.py').replace('PG1514_','PG1519_')
def main(action):
 if action=='compile':
  raw=inspect.getsource(compiler.main).replace('pg1512-original-io-build-v1','pg1517-original-io-build-v2').replace('pg1512-original-component-frozen-v1.safe.json','pg1517-original-component-frozen-v2.safe.json').replace('PG1512-original-component-compile-v1','PG1517-original-component-compile-v2').replace('pg1512_original_component_refs.py','pg1517_original_component_refs.py')
  ns={**compiler.__dict__,'TOOLS':TOOLS,'CLASS':CLASS,'java':lambda:remap(sources.java()),'refs':lambda:remap(sources.refs())}
 elif action=='stage':
  raw=inspect.getsource(stage.main).replace('pg1513-original-component-stage-v1','pg1518-original-component-stage-v2').replace('PG1513-original-component-stage-v1','PG1518-original-component-stage-v2').replace('pg1512-original-component-frozen-v1.safe.json','pg1517-original-component-frozen-v2.safe.json')
  ns={**stage.__dict__,'TOOLS':TOOLS}
 elif action=='profile':
  raw=inspect.getsource(profile.main).replace('pg1512-original-component-frozen-v1.safe.json','pg1517-original-component-frozen-v2.safe.json').replace('pg1513-original-component-stage-v1','pg1518-original-component-stage-v2').replace('PG1514-original-component-profile-v1','PG1519-original-component-profile-v2').replace('PG1514_DONE','PG1519_DONE')
  ns={**profile.__dict__,'TOOLS':TOOLS,'CLASS':CLASS,'SAVE':SAVE}
 else:raise ValueError('fixed owned profile action required')
 exec(compile(raw,'<new-only owned profile phase>','exec'),ns)
 return ns['main']()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['compile','stage','profile']);raise SystemExit(main(p.parse_args().action))
