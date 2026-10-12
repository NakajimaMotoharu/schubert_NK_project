"""Fresh business-day admission investigation; never starts a VM/Unit or rewrites rows."""
import hashlib
import json
import os
import subprocess
from pg1731_current_bootstrap_independent_post import payload as post_payload
from pg1446_current_cold_stage import W,SSH,P
from pg1674_critical_management_gate import management_gate

SLOT='pg1757-next-business-day-before-v1'
EXTRA=r'''
declaration_raw=after['configuration']['schubert-nk-morning-controller.service']['ExecStart']
parse_raw=(base/'pg477-completed-tools-v1/pg477_unit_references.py').read_bytes()
require(hashlib.sha256(parse_raw).hexdigest()=='b198cecd883e9a2f8cf2406dd2c92b0dca369ebd9ce3701c087205ef19311ca4')
node=next(n for n in ast.parse(parse_raw).body if isinstance(n,ast.FunctionDef)and n.name=='exec_record')
parser_scope={'re':re};exec(compile(ast.Module(body=[node],type_ignores=[]),'<pinned ordinary declaration>','exec'),parser_scope)
declaration=parser_scope['exec_record'](declaration_raw)
require(declaration is not None and declaration[1].endswith('dev.codex.schubert.nk.batch.file.MorningProcessMain')and '--resume'not in declaration[1])
require(not pathlib.Path('/var/lib/schubert-nk/maintenance/active').exists())
require(not pathlib.Path('/run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg1160-once-resume.conf').exists())
day=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date().isoformat()
require(day=='2026-10-13')
today_rows=[r for r in after['rows']['schubert.batch_runs']if r['business_date']==day]
require(not today_rows)
require(os.statvfs('/var/lib/pgpt-s1-preservation').f_bavail*os.statvfs('/var/lib/pgpt-s1-preservation').f_frsize>=10737418240)
value={**value,'investigationBusinessDay':day,'todayBatchRows':0,'ordinaryNoargs':True,'priorDoneNotResumed':True,'native':native}
'''

def payload():
    raw=post_payload()
    marker=" save=base/'pg1731-current-bootstrap-full-post-v1'"
    if raw.count(marker)!=1:raise ValueError('one new-only save point required')
    raw=raw.replace(marker,'\n'.join(' '+l if l else l for l in EXTRA.splitlines())+'\n'+marker.replace('pg1731-current-bootstrap-full-post-v1',SLOT))
    raw=raw.replace("'formalAccepted':False", "'investigationBusinessDay':day,'todayBatchRows':0,'ordinaryNoargs':True,'startAuthority':False,'formalAccepted':False")
    from pyflakes.api import check
    if check(raw,'<actual next business day readonly scope>'):raise ValueError('static gate refused')
    compile(raw,'<next business day original-scope verification>','exec');return raw

def main():
    os.umask(0o077);raw=payload().encode();out=W/SLOT;out.mkdir(mode=0o700)
    (out/'payload.private.py').write_bytes(raw)
    with management_gate(P/'current-management-critical.lock'):
        r=subprocess.run(SSH+['sudo','-n','python3','-'],input=raw,capture_output=True,timeout=90)
    (out/'stderr.private.log').write_bytes(r.stderr)
    v={'actualExit':r.returncode,'payloadSha256':hashlib.sha256(raw).hexdigest(),'formalAccepted':False}
    if r.returncode==0:v['guest']=json.loads(r.stdout)
    with(out/'manifest.safe.json').open('x')as f:json.dump(v,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(v));return r.returncode

if __name__=='__main__':raise SystemExit(main())
