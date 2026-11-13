"""Require the actual registered group before any producer call. Never repeat a terminal producer."""
from pathlib import Path
import json,hashlib,subprocess,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'PMO/pgpt-completion-stage-20261102'
def require_registered(state,config,terminal_exists,mutate):
 if state.get('ordinaryActiveGroup')!=config['groupId'] or not state.get('ordinaryGroupNotYetClosed'):
  raise ValueError('REGISTERED_ACTIVE_GROUP_REQUIRED_BEFORE_ANY_PRODUCER_OR_FILE_READ')
 if state.get('productionCoreMain')!=config['source']:
  raise ValueError('REGISTERED_FIXED_MAIN_SOURCE_REQUIRED')
 if mutate and terminal_exists:
  raise ValueError('OWNED_PRODUCER_ALREADY_TERMINAL_NO_REPEAT')
if __name__=='__main__':
 mode=sys.argv[1];c=json.loads((B/'input/2166_runref_one_source_start.json').read_text());state=json.loads((S/'checkpoint.json').read_text());mfile=B/'evidence/PG28636-runref-one-source-static-v1/manifest.json';require_registered(state,c,mfile.exists(),mode=='produce')
 if mode=='produce':raise SystemExit(subprocess.call([sys.executable,'-B',str(B/'input/2167_runref_one_source_static.py')],cwd=R))
 if mode!='verify':raise ValueError('registered verify or new-only produce')
 m=json.loads(mfile.read_text());assert m['actualExit']==0 and m['originalSourceInverseExact'];assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==v for p,v in m['inputHashes'].items());assert hashlib.sha256((B/'input/2167_runref_one_source_static.py').read_bytes()).hexdigest()==m['verifierSha256'];print(json.dumps(dict(actualExit=0,registeredGroup=True,existingSourcePGOnlyVerified=True,producerNotReplayed=True,productTestsExecuted=0)))
