"""Fixed unmodified PMD/Checkstyle on actual isolated private190 source, no Main apply."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run
from pg3696_hygiene_pmd_diagnosis import server,require
from git_source_contract import last_main_source

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    import sys
    require(sys.argv[1:]in [[],['--octal187']],'only qualified semantic stages');octal=bool(sys.argv[1:]);candidate_job='PG3726-octal-candidate-v1'if octal else 'PG3720-private-field-candidate-v2';static_job='PG3730-octal-candidate-static-v1'if octal else 'PG3722-private-candidate-static-v1'
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean operator before fixed analyzers')
    prior=json.loads((W/candidate_job.lower()/'manifest.safe.json').read_bytes());require(prior['actualExit']==0,'actual full6 candidate finished')
    original=W/'pg3422-candidate-static-v1/manifest.safe.json'
    # The exact complete candidate hash map is materialized from its proven base plus90 deltas.
    files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    for name,item in prior['result']['changes'].items():require(files[name]==item['before'],'base source not changed');files[name]=item['candidate']
    source=last_main_source(ROOT);require(source==prior['baseCandidateSource'],'same immutable base Main')
    data={'source':source,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'candidateJob':candidate_job,'staticJob':static_job,'includeCheckstyle':True,'candidateManifestSha256':prior['result']['serverManifestSha256'],'originalStaticManifestSha256':hashlib.sha256(original.read_bytes()).hexdigest(),'sourceSha256':files}
    if octal:data.update(semanticKind='OCTAL_EXPLICIT_BASE',baseStaticManifestSha256=json.loads((W/'pg3722-private-candidate-static-v1/manifest.safe.json').read_bytes())['result']['serverManifestSha256'])
    os.umask(0o077);out=W/data['staticJob'].lower();out.mkdir();script=out/'static.private.py';script.write_text(inspect.getsource(require)+'\n'+inspect.getsource(server)+'\nserver('+repr(data)+')\n')
    dest='/home/mini/schubert-nk-pgpt/transfer/'+data['staticJob'];rc,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/'+data['staticJob']+' && mkdir -m700 '+dest,timeout=30);require(rc==0,'new-only fixed analysis')
    rc,_=copy(script,dest+'/',timeout=60);require(rc==0,'fixed operator copied')
    rc,text=run('python3 -B '+dest+'/static.private.py',timeout=360);(out/'observer.private.log').write_text(text)
    value={'actualExit':rc,'baseCandidateSource':source,'operatorHead':data['head'],'payloadSha256':hashlib.sha256(script.read_bytes()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(text.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if rc==0:print(json.dumps({k:v for k,v in value['result'].items()if k in {'pmd','checkstyle','serverManifestSha256'}}))
    return rc


if __name__=='__main__':raise SystemExit(main())
