"""Independent current-day genuine Inspector journal/SQL/native provenance.

Still not whole parent, native counters or formal acceptance. Copies both
streams for preservation; only later closing stream is eligible for counters.
"""
import ast
import hashlib
import json
import os
import subprocess
from pg1454_current_day_observer import R
from pg1450_current_cold_retry import W
from pg1446_current_cold_stage import SSH
from pg1241_fresh_inspector_provenance import PAYLOAD as original


def payload():
    live=json.loads((W/'pg1457-current-day-live-binding-v1/manifest.safe.json').read_bytes());assert live['actualExit']==0
    b=live['binding'];before=json.loads((W/'pg1455-current-day-before-v1/manifest.safe.json').read_bytes());assert before['actualExit']==0
    changes=[('cbca8738-3b24-4090-b77c-bf029677cdd6','3d69f5af-6bac-46b1-a540-7591c4a79a0d'),('9f651096-aef9-4fba-90b0-a653e99f035a',b['run']),('2026-10-10T20:03:22.718197Z',b['cutoff']),('99c487c7c9444c81bf20813d03875565','d69f0f99b48a47a5b51ad571ac996c31'),('pg1241-fresh-inspector-provenance-v1','pg1462-current-day-inspector-v1'),('PG1241-fresh-inspector-provenance-v1','PG1462-current-day-inspector-v1'),('pg1238-fresh-day-ordinary-before-v1','pg1455-current-day-before-v1'),('57a5889403d752e2558f144b41e9ddd702451d78bf0deab5b6f2fd462b02966e',before['guest']['privateBeforeSha256']),('0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d','ecae1310716f356d763b346528988ccdbfad0eccf0b2b27b1f3e77ed546afc99'),('d5b00104280028d9ea81b44c1d1c805f3c2861ed','769ddb15cd735c25fef581b5f9850ef9d0053c0f'),('2026-10-11\'and step',before['guest']['newJstDate']+"'and step"),('101554','13787'),('101701','13934'),('61234139496',str(b['start'])),('63034139496',str(b['start']+1800000000))]
    raw=original
    for old,new in changes:
        if old not in raw:raise ValueError('explicit current Inspector binding absent')
        raw=raw.replace(old,new)
    marker='require(len(eligible)==0) # This fixture only. Future nonempty candidates require full cipher/reference oracle.'
    assert raw.count(marker)==1
    raw=raw.replace(marker,marker+'\n'+EXPECTED_OUTBOX)
    old="all(type(step[k])is int and step[k]==0 for k in ['target_count','success_count','failure_count','byte_count'])"
    assert raw.count(old)==1
    raw=raw.replace(old,"all(type(step[k])is int and step[k]==(outbox_count if k in ['target_count','success_count']else 0) for k in ['target_count','success_count','failure_count','byte_count'])")
    old="for suffix,digest in [('terminal.exec','330c868ea20828a2fff3666a6cbedd77f06fcf30095d7de711412ce47183025f'),('closing.exec','47910f38118892b0c7618714514a0017ee51d1549e3eb9d37ab339b6606daae6')]:"
    assert raw.count(old)==1
    raw=raw.replace(old,"for suffix in ['terminal.exec','closing.exec']:")
    raw=raw.replace("now=p.lstat();metadata=lambda s:","digest=hashlib.sha256(b).hexdigest();now=p.lstat();metadata=lambda s:")
    raw=raw.replace('and len(b)==17228 and hashlib.sha256(b).hexdigest()==digest','and 0<len(b)<=33554432 and hashlib.sha256(p.read_bytes()).hexdigest()==digest')
    raw=raw.replace("require(str(p)not in before['native']);", "require(before['runtime']['children']['ordinary-inspector196'][2:6]==[991,976,stat.S_IFDIR|0o700,2]);")
    raw=raw.replace("'nativeBytes':34456", "'nativeBytes':sum(len(v[1])for v in copies),'nativeCounterAccepted':False,'sameSessionUnionForbidden':True,'outboxPruneExpectedCount':outbox_count")
    ast.parse(raw);return raw


EXPECTED_OUTBOX=r'''
def expired_outbox(row):
 if row['status']!='SENT' or row['sent_at']is None:return False
 sent=datetime.datetime.fromisoformat(row['sent_at']);lease=None if row['lease_until']is None else datetime.datetime.fromisoformat(row['lease_until'])
 require(sent.tzinfo is not None and(lease is None or lease.tzinfo is not None))
 return sent<cut-datetime.timedelta(hours=168)and(lease is None or lease<cut)
outbox_count=sum(expired_outbox(r)for name in['schubert.mq_outbox','schubert_web_session.web_log_outbox']for r in before['current']['rows'][name])
require(outbox_count==9) # Fixed before: API0 + Web9, independent SS331/V011 predicate.
'''


def main():
    os.umask(0o077);out=W/'pg1462-current-day-inspector-v1';out.mkdir(mode=0o700)
    raw=payload().encode()
    with(out/'payload.private.py').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
    r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=60)
    with(out/'observer.private.log').open('xb')as f:f.write(r.stderr);f.flush();os.fsync(f.fileno())
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False,'wholeParentAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result,sort_keys=True));return r.returncode


if __name__=='__main__':raise SystemExit(main())
