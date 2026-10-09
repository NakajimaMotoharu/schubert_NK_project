"""Fresh independent immutable post-probe full24/trees/Unit/kernel/resource0 capture."""
import inspect
from pg787_retired_post import PAYLOAD,preserved
from pg785_exec_history import accepted
import pg784_stopped_baseline as transport

def payload():
    raw=PAYLOAD.replace('pg787-retired-post-v1','pg800-probe-post-v1')
    raw=raw.replace("assert b'Pg783ExistingPairRetirement'not in args and not any(a.endswith(b'/pg783_refs.py')for a in args)","assert not any(a in args for a in (b'Pg783ExistingPairRetirement',b'Pg797DatabaseProbe',b'Pg798DatabaseProbe'))and not any(a.endswith((b'/pg783_refs.py',b'/pg797_refs.py',b'/pg798_refs.py'))for a in args)")
    marker='with CaptureReferences():';assert raw.count(marker)==1
    raw=raw.replace(marker,r'''probe=base/'pg798-scope-probe-v1'
complete=(probe/'complete.private').read_bytes()
assert complete==b'allNewScopesReturnedNormally=true\nsameTwoServersOver75s=true\ndbClosedConfirmed=true\noldCloseNotInferred=true\nstartsStopsRevokeRetire0=true\n'
probeObserved={}
for line in(probe/'observations.private').read_text().splitlines():
 key,value=line.split('=');assert key not in probeObserved and value.isdigit();probeObserved[key]=int(value)
assert probeObserved.keys()=={'count','maxGapNanos','maxGapBoundNanos'}and probeObserved['count']>=15 and 0<probeObserved['maxGapNanos']<probeObserved['maxGapBoundNanos']==30000000000
'''+marker)
    raw=raw.replace("'snapshotSha256':hashlib.sha256", "'maxObservationGapNanos':probeObserved['maxGapNanos'],'observationCount':probeObserved['count'],'probeCompleteSha256':hashlib.sha256(complete).hexdigest(),'snapshotSha256':hashlib.sha256")
    return inspect.getsource(accepted)+'\n'+inspect.getsource(preserved)+'\n'+raw

if __name__=='__main__':
    raw=inspect.getsource(transport.main).replace('pg784-stopped-current-v1','pg800-probe-post-v1')
    context={**transport.__dict__,'PAYLOAD':payload()}
    exec(compile(raw,'<800 fresh independent post-probe>', 'exec'),context);context['main']()
