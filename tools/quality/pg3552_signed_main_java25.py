"""Read signed current project Jars: every one of1643 Main classes targets Java25."""
import hashlib
import json
from pathlib import Path
import zipfile
from pg3420_outbox_signed_candidate import NEXT
from pg3520_outbox_owned_sources_v2 import SOURCE, BOM
from pg1446_current_cold_stage import W


def java25_class(value):
    if type(value)is not bytes or len(value)<8 or value[:4]!=b'\xca\xfe\xba\xbe'or int.from_bytes(value[6:8],'big')!=69:
        raise ValueError('genuine Java25 class header required')
    return True


def main():
    manifest=(NEXT/'RELEASE-MANIFEST.json').read_bytes()
    if hashlib.sha256(manifest).hexdigest()!=BOM:raise ValueError('actual signed current BOM required')
    records=json.loads(manifest)['artifacts'];by_path={v['path']:v for v in records}
    full=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes())['result']
    if full['productionSource']!=SOURCE or full['tests']!=3712:raise ValueError('current qualified whole required')
    modules={};seen=set()
    for module in ['protocol','storage','bootstrap','api','web','batch']:
        if module in {'api','web','batch'}:
            relative={'api':'api/api.jar','web':'web/web.jar','batch':'operations/batch.jar'}[module]
        else:
            candidates=[p for p in by_path if Path(p).name==f'schubert-nk-{module}-0.1.0-SNAPSHOT.jar']
            if not candidates or len({by_path[p]['sha256']for p in candidates})!=1:raise ValueError('same common Jar in all roles required')
            relative=sorted(candidates)[0]
        p=NEXT/relative;raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=by_path[relative]['sha256']:raise ValueError('BOM Jar bytes required')
        with zipfile.ZipFile(p)as z:
            names=[n for n in z.namelist()if n.endswith('.class')]
            if len(names)!=len(set(names))or len(names)!=full['modules'][module]['mainClasses']:raise ValueError('complete unique module class inventory required')
            for name in names:
                value=z.read(name)
                java25_class(value)
                if name in seen:raise ValueError('unique genuine Java25 Main class required')
                seen.add(name)
        modules[module]={'signedJarPath':relative,'jarSha256':by_path[relative]['sha256'],'classes':len(names),'majorVersion':69}
    if len(seen)!=1643:raise ValueError('all1643 signed Main classes required')
    value={'actualExit':0,'productionSource':SOURCE,'BOM':BOM,'modules':modules,'all1643MainJava25':True,
           'methodBodyOrCoverageChanged':False,'newPtCredit':0,'formalUpdated':False,'F02Accepted':False}
    out=Path(__file__).resolve().parents[2]/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3552-signed-main-java25';out.mkdir(parents=True)
    with(out/'manifest.json').open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'actualExit':0,'signedMainClasses':1643,'allMajor69':True,'manifestSha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'F02Accepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
