"""Final91 after BUG1345, same running observer, canonical entry only; no VM action."""
import hashlib
import inspect
import json
from pyflakes.api import check,checkPath
import pg4190_partial_recovery_qualification as previous
import pg4220_same_peer_current_observer as observer
import pg4234_canonical_fresh_noargs_once as entry
import pg4224_same_parent_stack_sample as sample


def main():
    extra=['pg4200_metadata_continuation_test','pg4214_quiescent_ten_ref_observation_test','pg4216_same_peer_observer_manager_test','pg4220_same_peer_current_observer_test','pg4222_fresh_current_noargs_once_test','pg4234_canonical_fresh_noargs_once_test']
    ns={**vars(previous),'EXTRA':previous.EXTRA+extra}
    raw=inspect.getsource(previous.main).replace('pg4190-partial-recovery-qualification-v1','pg4236-canonical-fresh-qualification-v1')
    exec(compile(raw,'<affected91 canonical full entry>','exec'),ns);ns['main']()
    files=observer.namespace()['files']();hashes={n:hashlib.sha256(raw.encode()).hexdigest()for n,raw in files.items()}
    emitted={**files,'canonical-entry.py':entry.payload(hashes),'stack.py':sample.payload({},'fixture')}
    paths=sorted(p for pattern in ['pg421*.py','pg422*.py','pg423*.py']for p in(previous.ROOT/'tools/quality').glob(pattern))
    findings=sum(check(raw,'<'+n+'>')for n,raw in emitted.items())+sum(checkPath(str(p))for p in paths)
    if findings:raise ValueError('all host/emitted static closure required')
    value={'actualExit':0,'source':observer.SOURCE,'files':hashes,'freshOnceSha256':hashlib.sha256(emitted['canonical-entry.py'].encode()).hexdigest(),
           'hostSourceHashes':{str(p.relative_to(previous.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},
           'staticFindings':0,'productionPtAdded':0,'formalAccepted':False,'rootStartIssued':False,'observerReissued':False}
    (previous.W/'pg4236-canonical-fresh-qualification-v1/complete.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='hostSourceHashes'}));return 0


if __name__=='__main__':raise SystemExit(main())
