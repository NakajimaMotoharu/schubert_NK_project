"""Fresh legal JST day whole before, startup must remain empty; no operator INVALID."""
import ast
import hashlib
import inspect
import json
import os
import subprocess
from pg1453_current_cold_post import payload as post_payload
from pg1450_current_cold_retry import W
from pg1446_current_cold_stage import SSH
from pg1454_current_day_observer import R
from pg870_ordinary_policy import ordinary_argv


def payload():
    raw=post_payload().replace('PG1453-current-cold-independent-post-v1','PG1455-current-day-before-v1').replace('pg1453-current-cold-independent-post-v1','pg1455-current-day-before-v1')
    marker='print(json.dumps(result,sort_keys=True))'
    assert raw.count(marker)==1
    publication="with(SAVE/'result.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())"
    assert raw.count(publication)==1
    raw=raw.replace(publication,'')
    raw=raw.replace(marker,inspect.getsource(ordinary_argv)+'\n'+EXTRA)
    ast.parse(raw);return raw


EXTRA=r'''
release=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG1292')
argv=ordinary_argv((release/'systemd/schubert-nk-morning-controller.service').read_bytes(),pathlib.Path('/etc/systemd/system/schubert-nk-morning-controller.service.d/pg477-native-coverage.conf').read_bytes())
declaration=exec_record(first['configuration']['schubert-nk-morning-controller.service']['ExecStart'])
require(declaration is not None and declaration[:3]==('/usr/bin/java',argv,'no')and '--resume'not in argv)
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg492-once-resume.conf').exists())
day=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
same_day=[r for r in first['rows']['schubert.batch_runs']if r['business_date']==day and r['step']=='CLEAN_INBOX_OUTBOX'and r['status']in['SUCCESS','WARNING']]
require(len(same_day)==0)
available={str(p):os.statvfs(p).f_bavail*os.statvfs(p).f_frsize for p in[BASE,pathlib.Path('/srv/schubert-nk/backup')]}
require(min(available.values())>=805306368)
value={'current':first,'runtime':runtime,'ordinaryNoargs':True,'newJstDate':day,'existingSuccessfulInspectorStepsForDate':0,'availableBytes':available,'requiredGuestWriteAndCloseBytes':805306368}
encoded=json.dumps(value,sort_keys=True).encode()
with(SAVE/'before.private.json').open('xb')as f:f.write(encoded);f.flush();os.fsync(f.fileno())
fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);os.fsync(fd);os.close(fd)
result.update(privateBeforeSha256=hashlib.sha256(encoded).hexdigest(),ordinaryNoargs=True,newJstDate=day,existingSuccessfulInspectorStepsForDate=0,availableBytes=available,operatorInvalidIssued=False)
with(SAVE/'result.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
print(json.dumps(result,sort_keys=True))
'''


def main():
    os.umask(0o077);out=W/'pg1455-current-day-before-v1';out.mkdir(mode=0o700)
    raw=payload().encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    with(out/'observer.private.log').open('xb')as f:r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,stdout=f,stderr=f);f.flush();os.fsync(f.fileno())
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:result['guest']=json.loads((out/'observer.private.log').read_bytes())
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True));return r.returncode


if __name__=='__main__':raise SystemExit(main())
