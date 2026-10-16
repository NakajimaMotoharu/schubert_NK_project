"""Bound independent Root/observer tests and exact actual standalone payload hashes."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check,checkPath
import pg4736_new_normal_root_once as entry
import pg4738_new_normal_live_binding as binding


def main():
    os.umask(0o077);out=entry.W/entry.QUALIFICATION;out.mkdir(mode=0o700)
    names=['pg4730_new_current_readonly_test','pg4734_new_current_same_peer_observer_test',
           'pg4736_new_normal_root_once_test','pg4738_new_normal_live_binding_test',
           'pg4220_same_peer_current_observer_test','pg4216_same_peer_observer_manager_test']
    started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    with(out/'tests.private.log').open('xb')as log:
        result=subprocess.run(['python3','-B','-m','unittest',*names],stdout=log,stderr=log)
    if result.returncode!=0:raise ValueError('selected original tests failed; preserve namespace/no start')
    files=entry.observer.files();hashes={n:hashlib.sha256(v.encode()).hexdigest()for n,v in files.items()}
    raw=entry.payload(hashes)
    findings=sum(check(v,'<'+n+'>')for n,v in {**files,'fresh-once.py':raw,'live.py':'SOURCE="x"\nDIGEST="x"\nEXPECTED={}\n'+binding.body()}.items())
    paths=[Path('tools/quality')/n for n in ['pg4730_new_current_readonly.py','pg4730_new_current_readonly_test.py',
           'pg4734_new_current_same_peer_observer.py','pg4734_new_current_same_peer_observer_test.py',
           'pg4736_new_normal_root_once.py','pg4736_new_normal_root_once_test.py',
           'pg4738_new_normal_live_binding.py','pg4738_new_normal_live_binding_test.py',
           'pg4728_ssc299_publication_post.py','pg4740_new_normal_root_qualification.py']]
    findings+=sum(checkPath(str(p))for p in paths)
    if findings:raise ValueError('all host/emitted static0')
    value={'actualExit':0,'source':entry.SOURCE,'files':hashes,'freshOnceSha256':hashlib.sha256(raw.encode()).hexdigest(),
           'hostSourceHashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},
           'staticFindings':0,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'formalAccepted':False,'productionPtAdded':0,'rootStartIssued':False}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True))
    print(json.dumps({k:v for k,v in value.items()if k!='hostSourceHashes'}));return 0


if __name__=='__main__':raise SystemExit(main())
