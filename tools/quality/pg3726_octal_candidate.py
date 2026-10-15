"""187 integer tokens: independent base8 value check, full typed structure proof, new-only source."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run
from git_source_contract import last_main_source
from pg3714_private_field_candidate import require

ROOT=Path(__file__).resolve().parents[2];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def server(data):
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG3726-octal-candidate-v1';out.mkdir();(out/'classes').mkdir();candidate=out/'candidate';root=b/'runs/PG3720-private-field-candidate-v2/candidate';transfer=b/'transfer/PG3726-octal-candidate-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    require(sha(root.parent/'manifest.safe.json')==data['privateProofSha256'],'actual complete prior190 semantic proof')
    require({str(p.relative_to(root)):sha(p)for p in root.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all849 actual current4c9 base bytes')
    for name,h in data['toolSha256'].items():require(sha(transfer/name)==h,'fixed new tools and formatter')
    oldpath=b/'runs/PG3690-import-candidate-v1/manifest.safe.json';require(sha(oldpath)==data['classpathProofSha256'],'qualified exact actual six typed dependencies');prior=json.loads(oldpath.read_bytes())
    java=b/'tools/jdk-25.0.4/bin/java';javac=java.parent/'javac';r=subprocess.run([str(javac),'-Xlint:all','-Werror','-d',str(out/'classes'),*[str(transfer/n)for n in data['toolSha256']if n.endswith('.java')]],capture_output=True,timeout=30);(out/'compile.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'all compiler tools lint0')
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'begin.safe.json').write_text(json.dumps({'source':data['source'],'operatorHead':data['head'],'startUTC':start,'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'vmActions':0}))
    r=subprocess.run([str(java),'-cp',str(out/'classes'),'SourceOctalLiteralExpansion',str(root),str(candidate)],capture_output=True,text=True,timeout=90);(out/'literals.safe.tsv').write_text(r.stdout);(out/'proposal.private.log').write_text(r.stderr);require(r.returncode==0,'actual octal-token proposal0');rows=r.stdout.splitlines();require(rows[-1]=='OCTAL\t187'and sum(x.startswith('LITERAL\t')for x in rows)==187,'exact all187 actual tokens')
    files=sorted(candidate.glob('src/*/src/main/java/**/*.java'));require(len(files)==849,'all849 source regular copies')
    r=subprocess.run([str(java),'-Xmx1536m','-jar',str(transfer/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',*map(str,files)],capture_output=True,timeout=120);(out/'format.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'fixed project format0')
    def cp_hash(cp):
        values={}
        for p in map(Path,cp.split(':')):
            require(p.is_absolute()and p.exists(),'all absolute frozen dependencies')
            values[str(p)]={str(x.relative_to(p)):sha(x)for x in p.rglob('*')if x.is_file()and x.suffix in {'.java','.class'}}if p.is_dir()else sha(p)
        return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
    modules={}
    for module,item in prior['modules'].items():
        relative='src/schubert-nk-'+module+'/src/main/java';cp=item['phases']['after']['command'][-1];require(cp_hash(cp)==item['classpathInputsSha256'],'exact old qualified classpath, no implicit current cwd')
        r=subprocess.run([str(java),'-Xmx1536m','-cp',str(out/'classes'),'SourceSemanticEquivalence',str(root/relative),str(candidate/relative),cp],capture_output=True,text=True,timeout=180);(out/(module+'-proof.safe.tsv')).write_text(r.stdout);(out/(module+'-proof.private.log')).write_text(r.stderr);require(r.returncode==0,'all unchanged resolved symbol/type/capture/AST/literal/ABI '+module)
        require(len(r.stdout.splitlines())==item['sourceFiles']and all(x.startswith('PROOF\t')for x in r.stdout.splitlines()),'all compilation units proof');require(cp_hash(cp)==item['classpathInputsSha256'],'typed inputs remained unchanged');modules[module]={'actualExit':0,'sourceFiles':item['sourceFiles'],'proofSha256':sha(out/(module+'-proof.safe.tsv'))};(out/'progress.safe.json').write_text(json.dumps({'verified':list(modules),'mainApplied':False}))
    changes={str(p.relative_to(candidate)):{'before':data['sourceSha256'][str(p.relative_to(candidate))],'candidate':sha(p)}for p in files if sha(p)!=data['sourceSha256'][str(p.relative_to(candidate))]}
    require(0<len(changes)<=187 and {str(p.relative_to(root)):sha(p)for p in root.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'actual finite delta and all source originals unchanged')
    result={'actualExit':0,'baseCandidateSource':data['source'],'operatorHead':data['head'],'sourceFiles':849,'octalIntegerTokens':187,'changedFiles':len(changes),'changes':changes,'modules':modules,'normalizedFullSemanticBindingsTreeLiteralsAndPublicAbiIdentical':True,'inputRegularAndOriginalsUnchanged':True,'canonicalOutputDisjoint':True,'tokenReportSha256':sha(out/'literals.safe.tsv'),'formatExit':0,'mainApplied':False,'fixedSastPending':True,'newWholeAndNativePending':True,'formalAccepted':False,'F03Accepted':False,'vmActions':0,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed octal operator');source=last_main_source(ROOT);prior=json.loads((W/'pg3720-private-field-candidate-v2/manifest.safe.json').read_bytes());typed=json.loads((W/'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes());applied=json.loads((W/'pg3724-private-candidate-material-v1/apply.safe.json').read_bytes());require(applied['actualExit']==0 and applied['changedMainFiles']==90,'genuine exact prior190 Main apply')
    names=['SourceOctalLiteralExpansion.java','SourceSemanticEquivalence.java','SourcePrivateFieldRename.java','IsolatedSourceOutput.java'];tools=[*[ROOT/'tools/quality'/n for n in names],Path('/home/mini/codex/project1/work/toolchain/google-java-format-1.36.1-all-deps.jar')]
    data={'source':source,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'privateProofSha256':prior['result']['serverManifestSha256'],'classpathProofSha256':typed['result']['serverManifestSha256'],'toolSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in tools}}
    require(data['toolSha256']['google-java-format-1.36.1-all-deps.jar']=='25b400f003089d23cc5320cdaf1a16cabee19b8aa3434d0ff021b3d9f42154b4','approved fixed formatter')
    os.umask(0o077);out=W/'pg3726-octal-candidate-v1';out.mkdir();script=out/'candidate.private.py';script.write_text(inspect.getsource(require)+'\n'+inspect.getsource(server)+'\nserver('+repr(data)+')\n');dest='/home/mini/schubert-nk-pgpt/transfer/PG3726-octal-candidate-v1';rc,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3726-octal-candidate-v1 && mkdir -m700 '+dest,timeout=30);require(rc==0,'new-only candidate')
    for p in [*tools,script]:
        rc,_=copy(p,dest+'/',timeout=60);require(rc==0,'every fixed tool transferred')
    rc,text=run('python3 -B '+dest+'/candidate.private.py',timeout=1800);(out/'observer.private.log').write_text(text);value={'actualExit':rc,'baseCandidateSource':source,'operatorHead':data['head'],'payloadSha256':hashlib.sha256(script.read_bytes()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(text.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if rc==0:print(json.dumps({k:v for k,v in value['result'].items()if k not in {'changes','modules'}}))
    return rc


if __name__=='__main__':raise SystemExit(main())
