"""Single affected tool89/emitted closure; no production regression/signature/VM replay."""
import hashlib
import inspect
import json
from pyflakes.api import check,checkPath
import pg4190_partial_recovery_qualification as prior
import pg4220_same_peer_current_observer as observer
import pg4222_fresh_current_noargs_once as once
import pg4224_same_parent_stack_sample as sample


def main():
    ns={**vars(prior),'EXTRA':prior.EXTRA+['pg4200_metadata_continuation_test','pg4214_quiescent_ten_ref_observation_test','pg4216_same_peer_observer_manager_test','pg4220_same_peer_current_observer_test','pg4222_fresh_current_noargs_once_test']}
    raw=inspect.getsource(prior.main).replace("'pg4190-partial-recovery-qualification-v1'","'pg4226-fresh-observer-qualification-v1'")
    exec(compile(raw,'<affected89 exact host tests>','exec'),ns);ns['main']()
    files=observer.namespace()['files']();hashes={n:hashlib.sha256(raw.encode()).hexdigest()for n,raw in files.items()}
    emitted={**files,'fresh-once.py':once.payload(hashes),'stack.py':sample.payload({},'fixture')}
    findings=sum(check(raw,'<'+name+'>')for name,raw in emitted.items())
    paths=sorted(p for pattern in ['pg421*.py','pg422*.py']for p in(prior.ROOT/'tools/quality').glob(pattern))
    findings+=sum(checkPath(str(p))for p in paths)
    if findings:raise ValueError('all host/emitted static0 required')
    value={'actualExit':0,'source':once.SOURCE,'files':hashes,'freshOnceSha256':hashlib.sha256(emitted['fresh-once.py'].encode()).hexdigest(),
           'staticFindings':0,'hostSourceHashes':{str(p.relative_to(prior.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},
           'productionPtAdded':0,'formalAccepted':False,'rootStartIssued':False}
    (prior.W/'pg4226-fresh-observer-qualification-v1/complete.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='hostSourceHashes'}));return 0


if __name__=='__main__':raise SystemExit(main())
