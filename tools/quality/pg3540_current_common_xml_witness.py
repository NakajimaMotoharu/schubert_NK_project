"""Original3712 common/consumer/config XML witness, no test or VM replay."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
from pyflakes.api import check
from lan_server import run
import pg3312_whole_suite_witness as previous
from pg3520_outbox_owned_sources_v2 import SOURCE
from pg1446_current_cold_stage import W

ROOT=Path(__file__).resolve().parents[2]
SLOT='pg3540-current-common-xml-witness-v1'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3540-current-common-xml-witness'


def payload():
    receipt=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes());full=receipt['result']
    if receipt['actualExit']!=0 or full['productionSource']!=SOURCE or full['tests']!=3712 or full['suites']!=545 or full['FESFlakyNotRun']!=0:
        raise ValueError('actual3712 same-source authority required')
    prior=json.loads((ROOT/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG3356-current-file-media-witness/manifest.json').read_bytes())
    classes={m:None if m in {'protocol','storage'}else sorted(s['class']for s in suites)for m,suites in prior['modules'].items()}
    broker='dev.codex.schubert.nk.api.messaging.config.ArtemisBrokerConfigurationTest'
    classes['api']=sorted(set(classes['api'])|{broker})
    tests={}
    for module,names in classes.items():
        base=ROOT/f'src/schubert-nk-{module}/src/test/java'
        paths=base.rglob('*Test.java')if names is None else[base/(name.replace('.','/')+'.java')for name in names]
        for path in paths:
            relative=str(path.relative_to(ROOT));fixed=subprocess.check_output(['git','show',full['sourceSnapshot']+':'+relative],cwd=ROOT)
            if fixed!=path.read_bytes():raise ValueError('current Test differs from actual3712 snapshot')
            tests[relative]=hashlib.sha256(fixed).hexdigest()
    data={'source':SOURCE,'snapshot':full['sourceSnapshot'],'wholeSha256':full['serverManifestSha256'],
          'classes':classes,'testHashes':tests,'completeModuleCounts':{m:full['modules'][m]for m,names in classes.items()if names is None},'hashCaseArguments':True}
    body=previous.SERVER.replace('PG3302','PG3412')
    condition="sum(s['counts']['tests']for s in result['protocol'])==85"
    if body.count(condition)!=1:raise ValueError('one actual completeProtocol cardinality required')
    body=body.replace(condition,condition[:-2]+'86').replace('original Protocol85/17 required','original Protocol86/17 required')
    raw='INPUT='+repr(data)+'\n'+inspect.getsource(previous.require)+'\n'+inspect.getsource(previous.project_suite)+'\n'+body
    if check(raw,'<same3712 original common witness>'):raise ValueError('complete witness globals required')
    compile(raw,'<current original3712 selected XML>','exec');return raw


def main():
    if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean fixed reader required')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);raw=payload();(out/'witness.private.py').write_text(raw)
    rc,text=run('python3 -B -c '+shlex.quote(raw),timeout=90)
    (out/'observer.private.log').write_text(text)
    if rc!=0:raise ValueError('original3712 XML witness refused; preserve error')
    v=json.loads(next(line for line in text.splitlines()if line.startswith('{')))
    if v['actualExit']!=0 or v['productionSource']!=SOURCE:raise ValueError('actual current witness required')
    PUBLIC.mkdir(parents=True)
    with(PUBLIC/'manifest.json').open('x')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
    safe={'actualExit':0,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(raw.encode()).hexdigest(),
          'publicManifestSha256':hashlib.sha256((PUBLIC/'manifest.json').read_bytes()).hexdigest(),
          'modules':{m:{'suites':len(s),'tests':sum(x['counts']['tests']for x in s)}for m,s in v['modules'].items()},'newPtCredit':0,'vmActions':0}
    with(out/'manifest.safe.json').open('x')as f:json.dump(safe,f,sort_keys=True)
    print(json.dumps(safe));return 0


if __name__=='__main__':raise SystemExit(main())
