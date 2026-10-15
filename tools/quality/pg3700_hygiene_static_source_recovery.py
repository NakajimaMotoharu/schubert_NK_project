"""Independently join the original PMD report to all849 actual source bytes; do not re-run it."""
import ast
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
from lan_server import copy,run
from git_source_contract import MAIN_PATHSPEC,last_main_source

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE='/home/mini/schubert-nk-pgpt'


def require(value,reason):
    if not value:raise ValueError(reason)


def server(data):
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');old=b/'runs/PG3696-hygiene-pmd-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    require(sha(old/'manifest.safe.json')==data['originalManifestSha256'],'immutable original blank-source PMD result')
    original=json.loads((old/'manifest.safe.json').read_bytes());require(original['actualExit']==0 and original['productionCandidateSource']==''and original['sourceSnapshot']==data['originalSnapshot'],'exact original metadata gap')
    require(sha(old/'pmd.xml')==original['pmd']['reportSha256']==data['reportSha256']and sha(old/'pmd.private.log')==original['pmd']['logSha256'],'actual original PMD report/log untouched')
    candidate=b/'runs/PG3692-hygiene-candidate-v1/candidate';require({str(p.relative_to(candidate)):sha(p)for p in candidate.glob('src/*/src/main/java/**/*.java')}==data['all849SourceSha256'],'every actually analyzed source byte equals qualified Git Main')
    require(len(data['all849SourceSha256'])==849 and data['source']=='5224dd641976df502f3d1f278d73ec55f5ff9711','exact new Main identity')
    out=b/'runs/PG3700-static-source-recovery-v1';out.mkdir()
    result={'actualExit':0,'productionCandidateSource':data['source'],'originalSourceSnapshot':data['originalSnapshot'],'originalSourceEmptyPreserved':True,'originalManifestSha256':data['originalManifestSha256'],'all849SourceSha256':data['all849SourceSha256'],'all849ByteJoinVerified':True,'pmd':original['pmd'],'checkstyle':{'actualExit':0,'findings':0,'reportSha256':'2c1b438c426339e8759a5f5cec897b42c3527bd6af324f56ea2db3e292af35f7'},'originalCandidateStageSha256':original['candidateManifestSha256'],'oldQualifiedInputsAndRulesUnchanged':original['inputsUnchanged']and not original['rulesSuppressed'],'pmdReissued':False,'wholeOrVmReissued':False,'MainDeployed':False,'F03Accepted':False,'formalAccepted':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean exact recovery operator')
    old=W/'pg3696-hygiene-pmd-diagnosis-v1';v=json.loads((old/'manifest.safe.json').read_bytes());r=v['result'];require(v['actualExit']==0 and r['productionCandidateSource']=='','original blank-source diagnostic preserved')
    tree=ast.parse((old/'pmd.private.py').read_text());assignments=[n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='INPUT'for t in n.targets)];require(len(assignments)==1,'original immutable payload input')
    inputs=ast.literal_eval(assignments[0].value);require(hashlib.sha256((old/'pmd.private.py').read_bytes()).hexdigest()==v['payloadSha256'],'original payload bytes')
    source=last_main_source(ROOT);require(not subprocess.check_output(['git','diff',source,r['sourceSnapshot'],'--',MAIN_PATHSPEC],cwd=ROOT),'actual original snapshot has precisely this Main tree')
    hashes={p:hashlib.sha256(subprocess.check_output(['git','show',source+':'+p],cwd=ROOT)).hexdigest()for p in inputs['sourceSha256']}
    require(hashes==inputs['sourceSha256']and len(hashes)==849,'all original actual source inputs equal this immutable Git source')
    require(hashes=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'all current source bytes unchanged')
    data={'source':source,'originalSnapshot':r['sourceSnapshot'],'originalManifestSha256':r['serverManifestSha256'],'reportSha256':r['pmd']['reportSha256'],'all849SourceSha256':hashes}
    os.umask(0o077);out=W/'pg3700-static-source-recovery-v1';out.mkdir();payload=inspect.getsource(require)+'\n'+inspect.getsource(server)+'\nINPUT='+repr(data)+'\nserver(INPUT)\n';script=out/'recover.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/PG3700-static-source-recovery-v1 && mkdir -m700 '+BASE+'/transfer/PG3700-static-source-recovery-v1',timeout=30);require(rc==0,'new-only read-only result qualification')
    rc,_=copy(script,BASE+'/transfer/PG3700-static-source-recovery-v1/',timeout=60);require(rc==0,'fixed source-qualified recovery proof')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/PG3700-static-source-recovery-v1/recover.private.py'),timeout=45);(out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'productionCandidateSource':source,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(output.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}));return rc


if __name__=='__main__':raise SystemExit(main())
