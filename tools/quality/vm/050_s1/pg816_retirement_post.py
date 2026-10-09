"""New readonly independent current runtime retirement postconditions, no replay."""
import ast,inspect
from pathlib import Path
import pg784_stopped_baseline as transport
from pg814_recovery_post import PAYLOAD as previous
def payload():
 raw=previous.replace("save=base/'pg814-recovered949-post-v1'","save=base/'pg816-runtime-retired-post-v1'").replace("base/'pg813-failed949-tools-v2'","base/'pg815-retirement-tools-v1'").replace('import pg813_owned as h','import pg815_snapshot as h')
 raw=raw.replace("before=h.baseline();root=base/'pg813-failed949-recovery-v2'","root=base/'pg815-runtime-retirement-v1';capture=(root/'after.private.json').read_bytes();assert hashlib.sha256(capture).hexdigest()=='d725011754d5a06d8591b16820b9e272aa41116723df8d6946384d6d1bc13652';before=json.loads(capture);stopped=base/'pg813-failed949-recovery-v2'")
 raw=raw.replace("assert(root/'complete.private').read_text()=='allNewScopesReturnedNormally=true\\noldCloseNotInferred=true\\nexistingPairRetired=true\\ncurrentSameEpochInvalid=true\\nstarts0=true\\n'","assert(root/'complete.private').read_text()=='onceResumeRetired=true\\nallNewScopesReturnedNormally=true\\noriginalPendingUnchanged=true\\ndatabaseUpdates0=true\\nstarts0=true\\n'")
 lines=raw.splitlines(keepends=True);raw=''.join(line for line in lines if not line.startswith('observations='))
 raw=raw.replace("root/(unit+'.stopped.private')","stopped/(unit+'.stopped.private')")
 raw=raw.replace("'maxDbGapNanos':int(observations['maxGapNanos']),'dbObservations':int(observations['count']),'runtimePresent':True", "'maxDbGapNanos':None,'dbObservations':None,'runtimePresent':False")
 raw=raw.replace("save.mkdir(mode=0o700)","assert not list(pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d').iterdir())\nsave.mkdir(mode=0o700)")
 schema=(Path(__file__).resolve().parent/'pg785_exec_history.py').read_text();raw='SCHEMA='+repr(schema)+'\n'+raw;ast.parse(raw);return raw
if __name__=='__main__':
 raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg816-runtime-retired-post-v1');context={**transport.__dict__,'PAYLOAD':payload()}
 exec(compile(raw,'<816 independent once readonly>','exec'),context);context['main']()
