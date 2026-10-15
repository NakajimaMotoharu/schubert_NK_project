"""BUG1310: strict canonical row hashes, no mapping values interpreted as counts."""
import collections
import hashlib
import inspect
import json
import os
import subprocess
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate

SLOT='pg3646-root-browser-bridge-diagnostic-v1'


def compare(rows,hashes):
    if type(rows)is not list or type(hashes)is not list:raise ValueError('two explicit row/hash lists required')
    indexed={hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest():r for r in rows}
    if len(indexed)!=len(rows)or len(set(hashes))!=len(hashes):raise ValueError('duplicate row/hash forbidden')
    if any(type(h)is not str or len(h)!=64 or any(c not in '0123456789abcdef'for c in h)for h in hashes):raise ValueError('canonical SHA required')
    a,b=collections.Counter(indexed.keys()),collections.Counter(hashes)
    removed=list((a-b).elements());added=list((b-a).elements())
    return {'rootRows':len(rows),'browserBeforeRows':len(hashes),'rootRowsAbsentFromBrowserBefore':len(removed),'browserBeforeRowsNotInRoot':len(added),'addedHashes':added}


def payload():
    before=json.loads((W/'pg3580-current-browser-business-actual-v1/cases/before-rows.private.json').read_bytes())
    hashes={k:[hashlib.sha256(json.dumps(r,sort_keys=True,separators=(',',':')).encode()).hexdigest()for r in v]for k,v in before.items()}
    root=json.loads((W/'pg3586-current-browser-root-full-seal-v1/manifest.safe.json').read_bytes())
    return 'H='+repr(hashes)+'\nROOT_SHA='+repr(root['privateBeforeSha256'])+'\nimport collections,json,hashlib,datetime\nfrom pathlib import Path\n'+inspect.getsource(compare)+r'''
p=Path('/var/lib/pgpt-s1-preservation/pg3586-current-browser-root-full-seal-v1/before.private.json');raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()==ROOT_SHA
root=json.loads(raw);tables=root['rows'];assert len(tables)==len(H)==24 and set(tables)==set(H)
result={}
for name,rows in tables.items():
 value=compare(rows,H[name])
 if value['rootRowsAbsentFromBrowserBefore']or value['browserBeforeRowsNotInRoot']:result[name]=value
print(json.dumps({'actualExit':0,'observedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'all24Compared':True,'differences':result,'rootSha256':ROOT_SHA,'writes0':True,'rawExported':False}))
'''


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed readonly diagnostic required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'payload.private.py').write_text(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr);value={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),'formalAccepted':False}
    if not r.returncode:value['guest']=json.loads(r.stdout)
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True))
    print(json.dumps(value));return r.returncode


if __name__=='__main__':raise SystemExit(main())
