"""Independent SS331/324 before-image selectors; no actual DB result as oracle.

NK-OPS-001; SS331/341/V010-013/324 section12.2; PT-OPS-DAY1766.
Only missing immutable AUTH_SESSION references are classified here. Unknown
candidate types require another independent oracle, never assumed deletable.
"""
import hashlib
import inspect
import json
import os
import subprocess

from pg1446_current_cold_stage import P,SSH,W
from pg1674_critical_management_gate import management_gate
from pg1762_next_day_done_receipt import EXPECTED
from pg478_cleanup_oracle import candidates,instant,older


def classify_inbox(rows,selected):
    ids=set(selected)
    found={r['message_id']:r for r in rows['schubert.request_inbox']if r['message_id']in ids}
    if set(found)!=ids:raise ValueError('all candidate rows required')
    sessions={r['id'] for r in rows['schubert.auth_sessions']}
    for row in found.values():
        if (row['request_layout_id'],row['response_layout_id'],row['processing_state'],row['result_ref_type'],row['owner_user_id']) != ('LGNREQ01','LGNRSP01','COMPLETED','AUTH_SESSION',None):
            raise ValueError('separate independent route oracle required')
        if row['result_ref_uuid']is None or row['result_ref_uuid']in sessions:
            raise ValueError('missing immutable session not proven')
    return {'deleted':[],'protected':sorted(ids),'basis':'SS324 section12.2 missing immutable AUTH_SESSION; no decryption/output needed'}


def payload():
    raw='import datetime,json\n'+inspect.getsource(instant)+'\n'+inspect.getsource(older)+'\n'+inspect.getsource(candidates)+'\n'+inspect.getsource(classify_inbox)
    raw+='\nCUT='+repr(EXPECTED['cutoff'])+'\n'
    raw+=r'''
import hashlib,os,pathlib
if os.geteuid()!=0:raise ValueError('root private required')
p=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1759-next-day-ordinary-once-v1/before.private.json')
raw=p.read_bytes();before=json.loads(raw);expected=candidates(before['rows'],CUT)
inbox=classify_inbox(before['rows'],expected['inbox_scan_candidates'])
counts={k:len(v)for k,v in expected.items()}
result={'cutoff':CUT,'beforeSha256':hashlib.sha256(raw).hexdigest(),'candidateCounts':counts,'expectedInbox':inbox,'productionCalls':0,'actualDbRowsRead':0,'startsStopsSqlWrites':0,'wholeAccepted':False}
out=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1766-next-day-independent-candidates-v1');os.umask(0o077);out.mkdir(mode=0o700)
private={**result,'expected':expected}
with(out/'oracle.private.json').open('x')as f:json.dump(private,f,sort_keys=True);f.flush();os.fsync(f.fileno())
fd=os.open(out,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
result['expectedInbox']={'deleted':len(inbox['deleted']),'protected':len(inbox['protected']),'basis':inbox['basis']}
result['privateOracleSha256']=hashlib.sha256((out/'oracle.private.json').read_bytes()).hexdigest()
print(json.dumps(result))
'''
    compile(raw,'<independent before selectors>','exec');return raw


def main():
    os.umask(0o077);out=W/'pg1766-next-day-independent-candidates-v1';out.mkdir(mode=0o700)
    raw=payload().encode()
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    result={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'wholeAccepted':False}
    if r.returncode==0:result['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(result,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(result));return r.returncode


if __name__=='__main__':raise SystemExit(main())
