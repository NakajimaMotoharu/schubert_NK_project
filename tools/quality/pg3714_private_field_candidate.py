"""Isolated190-symbol alpha candidate plus fixed-format/full normalized semantic proof."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
from lan_server import copy,run
from git_source_contract import last_main_source

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
    import subprocess
    import shutil
    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/('runs/'+data['job']);out.mkdir();(out/'classes').mkdir();candidate=out/'candidate';candidate.mkdir();root=b/'runs/PG3692-hygiene-candidate-v1/candidate';transfer=b/('transfer/'+data['job']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    require({str(p.relative_to(root)):sha(p)for p in root.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all849 actual current source bytes')
    fieldroot=b/'runs/PG3712-field-inventory-v1';require(sha(fieldroot/'manifest.safe.json')==data['fieldManifestSha256'],'actual253 symbol/risk inventory');meta=json.loads((fieldroot/'manifest.safe.json').read_bytes());require(sha(fieldroot/'targets.private.json')==meta['targetMatrixSha256'],'immutable all253 exact target facts')
    rows=json.loads((fieldroot/'targets.private.json').read_bytes());targets=[r for r in rows if r['risk']=='PRIVATE_SYMBOL_CANDIDATE_NOT_YET_APPROVED'];held=[r for r in rows if r['risk']=='SERIALIZED_FIELD_NAME'];require(len(targets)==190 and len(held)==63,'all190/63 exact partition')
    prior=b/'runs/PG3690-import-candidate-v1/manifest.safe.json';require(sha(prior)==data['importManifestSha256'],'qualified actual module classpaths');old=json.loads(prior.read_bytes())
    for p,h in data['toolSha256'].items():require(sha(transfer/p)==h,'all fixed compiler/formatter source inputs')
    java=b/'tools/jdk-25.0.4/bin/java';javac=b/'tools/jdk-25.0.4/bin/javac';argv=[str(javac),'-Xlint:all','-Werror','-d',str(out/'classes'),str(transfer/'SourcePrivateFieldRename.java'),str(transfer/'IsolatedSourceOutput.java')]
    r=subprocess.run(argv,capture_output=True,timeout=30);(out/'compile.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'both private rename compiler tools lint0')
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'begin.safe.json').write_text(json.dumps({'productionCandidateSource':data['source'],'operatorHead':data['head'],'startUTC':start,'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'targetFindings':190,'serializedHeld':63,'MainApplied':False,'vmActions':0}))
    modules={};mapping={}
    def cp_hash(cp):
        values={}
        for p in map(Path,cp.split(':')):
            require(p.is_absolute()and p.exists(),'all exact actual type dependencies')
            values[str(p)]={str(x.relative_to(p)):sha(x)for x in p.rglob('*')if x.is_file()and x.suffix in {'.java','.class'}}if p.is_dir()else sha(p)
        return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
    for module,prior in old['modules'].items():
        selected=[r for r in targets if r['path'].split('/')[1]=='schubert-nk-'+module];require(selected,'all six selected module scopes')
        scope=root/('src/schubert-nk-'+module+'/src/main/java');output=candidate/('src/schubert-nk-'+module+'/src/main/java');cp=prior['phases']['after']['command'][-1]
        require(cp_hash(cp)==prior['classpathInputsSha256'],'all original classpath inputs exact')
        lines=[]
        for row in selected:
            require(len(row['facts'])==1 and row['sourceSha256']==data['sourceSha256'][row['path']],'exact selected source facts')
            f=row['facts'][0];relative=str(Path(row['path']).relative_to('src/schubert-nk-'+module+'/src/main/java'));require(f['path']==relative and f['nameStart']>=0,'exact field token coordinate')
            lines.append('\t'.join([relative,f['owner'],f['name'],str(f['nameStart'])]))
        require(len(set(lines))==len(lines),'all190 unique target symbols, no duplicated fee/rename')
        request=out/(module+'-requests.safe.tsv');request.write_text('\n'.join(lines)+'\n')
        reused=module in data.get('reuseModules',[])
        if reused:
            previous=b/'runs/PG3714-private-field-candidate-v1';progress=json.loads((previous/'progress.safe.json').read_bytes());require(progress=={'proposed':['api','batch','bootstrap'],'mainApplied':False},'original successful proposals only, failed protocol excluded')
            oldoutput=previous/'candidate'/('src/schubert-nk-'+module+'/src/main/java');report=(previous/(module+'-propose.safe.tsv')).read_text().splitlines()
            require(not(previous/(module+'-propose.private.log')).read_bytes(),'original successful proposal stderr empty')
            require(all(p.is_file()and not p.is_symlink()for p in oldoutput.rglob('*')if not p.is_dir()),'regular isolated previous proposal only')
            shutil.copytree(oldoutput,output)
            (out/(module+'-propose.safe.tsv')).write_bytes((previous/(module+'-propose.safe.tsv')).read_bytes())
        else:
            argv=[str(java),'-Xmx1536m','-cp',str(out/'classes'),'SourcePrivateFieldRename','propose',str(scope),cp,str(request),str(output)]
            r=subprocess.run(argv,capture_output=True,text=True,timeout=180);(out/(module+'-propose.safe.tsv')).write_text(r.stdout);(out/(module+'-propose.private.log')).write_text(r.stderr);require(r.returncode==0,'actual private source proposal and whole normalized proof0 '+module)
            report=r.stdout.splitlines()
        require(sum(x.startswith('PROOF\t')for x in report)==prior['sourceFiles']and report[-1]=='FIELDS\t'+str(len(selected)),'every unit and target symbol positive proof')
        mapping[module]=(output/'.private-field-map.tsv').read_text();require(len(mapping[module].splitlines())==len(selected),'every new declaration/old disappearance mapped')
        require(cp_hash(cp)==prior['classpathInputsSha256'],'all type inputs unchanged')
        modules[module]={'targetFindings':len(selected),'proposeExit':0,'proposalOrigin':'PG3714-original-success'if reused else data['job'],'proposeProofSha256':sha(out/(module+'-propose.safe.tsv')),'mappingSha256':sha(output/'.private-field-map.tsv'),'allCompilationUnits':prior['sourceFiles']};(out/'progress.safe.json').write_text(json.dumps({'proposed':list(modules),'mainApplied':False}))
    files=sorted(candidate.glob('src/*/src/main/java/**/*.java'));require(len(files)==849,'all actual candidate sources')
    argv=[str(java),'-Xmx1536m','-jar',str(transfer/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',*map(str,files)]
    r=subprocess.run(argv,capture_output=True,timeout=120);(out/'format.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'fixed project formatter0')
    for module,prior in old['modules'].items():
        scope=root/('src/schubert-nk-'+module+'/src/main/java');output=candidate/('src/schubert-nk-'+module+'/src/main/java');cp=prior['phases']['after']['command'][-1]
        require(cp_hash(cp)==prior['classpathInputsSha256'],'exact pre-verify classpath')
        request=out/(module+'-requests.safe.tsv');argv=[str(java),'-Xmx1536m','-cp',str(out/'classes'),'SourcePrivateFieldRename','verify',str(scope),cp,str(request),str(output)]
        r=subprocess.run(argv,capture_output=True,text=True,timeout=180);(out/(module+'-verify.safe.tsv')).write_text(r.stdout);(out/(module+'-verify.private.log')).write_text(r.stderr);require(r.returncode==0,'after-format all bindings/tree/literal/ABI/actual new fields proof0 '+module)
        report=r.stdout.splitlines();require(sum(x.startswith('PROOF\t')for x in report)==prior['sourceFiles']and report[-1]=='FIELDS\t'+str(modules[module]['targetFindings']),'same complete positive proof after formatting')
        require((output/'.private-field-map.tsv').read_text()==mapping[module]and cp_hash(cp)==prior['classpathInputsSha256'],'all fixed field mapping and classpath remain unchanged')
        modules[module].update(verifyExit=0,verifyProofSha256=sha(out/(module+'-verify.safe.tsv')))
        (out/'progress.safe.json').write_text(json.dumps({'proposed':list(modules),'verified':[k for k,v in modules.items()if v.get('verifyExit')==0],'mainApplied':False}))
    changes={}
    for p in files:
        rel=str(p.relative_to(candidate));h=sha(p)
        if h!=data['sourceSha256'][rel]:changes[rel]={'before':data['sourceSha256'][rel],'candidate':h}
    require(len(changes)==90 and sum(m['targetFindings']for m in modules.values())==190,'exact actual90 source/190 symbol delta')
    require({str(p.relative_to(root)):sha(p)for p in root.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all originals byte unchanged after complete proof')
    result={'actualExit':0,'baseCandidateSource':data['source'],'operatorHead':data['head'],'sourceFiles':849,'changedFiles':90,'renamedPrivateSymbols':190,'serializedFindingsUnchanged':63,'modules':modules,'changes':changes,'normalizedFullSemanticBindingsTreeLiteralsAndPublicAbiIdentical':True,'allNewFieldsPresentOldFieldsAbsent':True,'canonicalOutputDisjoint':True,'inputRegularAndOriginalsUnchanged':True,'formatExit':0,'mainApplied':False,'fixedSastPending':True,'newWholeAndNativePending':True,'F03Accepted':False,'formalAccepted':False,'vmActions':0,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    import sys
    require(sys.argv[1:]in [[],['--continue-after-protocol-proof-rejection']],'only original or explicitly continued new-only phase')
    continued=bool(sys.argv[1:]);job='PG3720-private-field-candidate-v2'if continued else 'PG3714-private-field-candidate-v1'
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed private candidate operator')
    source=last_main_source(ROOT);require(source=='5224dd641976df502f3d1f278d73ec55f5ff9711','exact input source still current')
    field=json.loads((W/'pg3712-field-naming-inventory-v1/manifest.safe.json').read_bytes());prior=json.loads((W/'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes());require(field['actualExit']==prior['actualExit']==0,'actual risk/classpath authorities')
    tools=[ROOT/'tools/quality/SourcePrivateFieldRename.java',ROOT/'tools/quality/IsolatedSourceOutput.java',Path('/home/mini/codex/project1/work/toolchain/google-java-format-1.36.1-all-deps.jar')]
    data={'source':source,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'fieldManifestSha256':field['result']['serverManifestSha256'],'importManifestSha256':prior['result']['serverManifestSha256'],'toolSha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in tools}}
    data.update(job=job,reuseModules=['api','batch','bootstrap']if continued else [])
    if continued:
        original=json.loads((W/'pg3714-private-field-candidate-v1/manifest.safe.json').read_bytes());require(original['actualExit']==1 and original['baseCandidateSource']==source,'original refused, not unknown/running job')
        data['originalRejectedManifestSha256']=hashlib.sha256((W/'pg3714-private-field-candidate-v1/manifest.safe.json').read_bytes()).hexdigest()
    require(data['toolSha256']['google-java-format-1.36.1-all-deps.jar']=='25b400f003089d23cc5320cdaf1a16cabee19b8aa3434d0ff021b3d9f42154b4','same approved project formatter')
    os.umask(0o077);out=W/job.lower();out.mkdir();payload=inspect.getsource(require)+'\n'+inspect.getsource(server)+'\nINPUT='+repr(data)+'\nserver(INPUT)\n';compile(payload,'<isolated190 field candidate>','exec');script=out/'candidate.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/'+job+' && mkdir -m700 '+BASE+'/transfer/'+job,timeout=30);require(rc==0,'new-only isolated private candidate')
    for p in [*tools,script]:
        rc,_=copy(p,BASE+'/transfer/'+job+'/',timeout=60);require(rc==0,'every fixed candidate tool')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/'+job+'/candidate.private.py'),timeout=2400);(out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'baseCandidateSource':source,'operatorHead':data['head'],'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(output.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if rc==0:print(json.dumps({k:v for k,v in value['result'].items()if k not in {'modules','changes'}}))
    return rc


if __name__=='__main__':raise SystemExit(main())
