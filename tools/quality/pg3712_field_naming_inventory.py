"""Actual compiler field identities/risks for253 naming findings; no automated rename yet."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import shlex
import subprocess
from lan_server import copy,run
from git_source_contract import last_main_source
from source_field_naming_inventory_test import fields

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE='/home/mini/schubert-nk-pgpt'


def require(value,reason):
    if not value:raise ValueError(reason)


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG3712-field-inventory-v1';out.mkdir();(out/'classes').mkdir();root=b/'runs/PG3692-hygiene-candidate-v1/candidate';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    require({str(p.relative_to(root)):sha(p)for p in root.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all849 exact current Main')
    prior=b/'runs/PG3690-import-candidate-v1';require(sha(prior/'manifest.safe.json')==data['importManifestSha256'],'qualified original type classpath authority');meta=json.loads((prior/'manifest.safe.json').read_bytes())
    inv=b/'runs/PG3706-pmd-inventory-v1';require(sha(inv/'findings.private.json')==data['findingsSha256'],'all raw source-bound naming warnings')
    rows=[x for x in json.loads((inv/'findings.private.json').read_bytes())if x['rule']in {'AvoidFieldNameMatchingMethodName','AvoidFieldNameMatchingTypeName'}];require(len(rows)==253,'original250+3 exact naming targets')
    tool=b/'transfer/PG3712-field-inventory-v1/SourceFieldNamingInventory.java';require(sha(tool)==data['toolSha256'],'fixed field fact compiler')
    java=b/'tools/jdk-25.0.4/bin/java';javac=b/'tools/jdk-25.0.4/bin/javac';r=subprocess.run([str(javac),'-Xlint:all','-Werror','-d',str(out/'classes'),str(tool)],capture_output=True,timeout=30);(out/'compile.private.log').write_bytes(r.stdout+r.stderr);require(r.returncode==0,'field fact compiler full lint0')
    matches=[];modules={};start=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'begin.safe.json').write_text(json.dumps({'startUTC':start,'source':data['source'],'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'MainModified':False}))
    for module,item in meta['modules'].items():
        targets=[x for x in rows if x['path'].split('/')[1]=='schubert-nk-'+module]
        if not targets:continue
        cp=item['phases']['after']['command'][-1]
        def cp_hash():
            value={}
            for p in map(Path,cp.split(':')):
                require(p.is_absolute()and p.exists(),'all qualified type dependencies')
                value[str(p)]={str(x.relative_to(p)):sha(x)for x in p.rglob('*')if x.is_file()and x.suffix in {'.java','.class'}}if p.is_dir()else sha(p)
            return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
        require(cp_hash()==item['classpathInputsSha256'],'all exact previous qualified classpath bytes')
        scope=root/('src/schubert-nk-'+module+'/src/main/java');argv=[str(java),'-Xmx1536m','-cp',str(out/'classes'),'SourceFieldNamingInventory',str(scope),cp]
        r=subprocess.run(argv,capture_output=True,text=True,timeout=180);(out/(module+'-fields.safe.tsv')).write_text(r.stdout);(out/(module+'-fields.private.log')).write_text(r.stderr);require(r.returncode==0,'actual compiler field facts0')
        facts=fields(r.stdout)
        for row in targets:
            relative=str(Path(row['path']).relative_to('src/schubert-nk-'+module+'/src/main/java'));name=row['coordinates']['variable'];line=int(row['coordinates']['beginline'])
            found=[f for f in facts if f['path']==relative and f['name']==name and f['nameLine']==line]
            value={'findingId':row['id'],'path':row['path'],'rule':row['rule'],'sourceSha256':row['sourceSha256'],'facts':found,'renameIssued':False}
            if len(found)!=1:value['risk']='UNKNOWN_OR_AMBIGUOUS_SOURCE_TOKEN'
            else:
                f=found[0]
                if 'private'not in f['modifiers']:value['risk']='PUBLIC_PACKAGE_OR_PROTECTED_ABI'
                elif f['record']:value['risk']='RECORD_COMPONENT_API'
                elif f['serializable']:value['risk']='SERIALIZED_FIELD_NAME'
                elif not f['owner']:value['risk']='ANONYMOUS_OWNER_REVIEW'
                elif any(a not in '[]'and not a.startswith(('org.jspecify.','java.lang.'))for a in (f['ownerAnnotations'].strip('[]').split(', ')+f['fieldAnnotations'].strip('[]').split(', '))):value['risk']='ANNOTATED_REFLECTION_BINDING_REVIEW'
                else:value['risk']='PRIVATE_SYMBOL_CANDIDATE_NOT_YET_APPROVED'
            matches.append(value)
        require(cp_hash()==item['classpathInputsSha256'],'all qualified dependency bytes stable')
        modules[module]={'actualExit':0,'targetFindings':len(targets),'allFieldFacts':len(facts),'factsSha256':sha(out/(module+'-fields.safe.tsv'))};(out/'progress.safe.json').write_text(json.dumps({'modules':list(modules),'matchedFindings':len(matches)}))
    require(len(matches)==253 and len({x['findingId']for x in matches})==253,'no naming finding lost')
    require({str(p.relative_to(root)):sha(p)for p in root.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all original sources unchanged')
    (out/'targets.private.json').write_text(json.dumps(matches,sort_keys=True));result={'actualExit':0,'productionCandidateSource':data['source'],'targets':253,'riskCounts':dict(Counter(x['risk']for x in matches)),'modules':modules,'targetMatrixSha256':sha(out/'targets.private.json'),'MainChanged':False,'pmdReissued':False,'vmActions':0,'applicableViolationCount':None,'F03Accepted':False,'formalAccepted':False,'startUTC':start,'endUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean current source before read-only field inventory')
    source=last_main_source(ROOT);require(source=='5224dd641976df502f3d1f278d73ec55f5ff9711','exact source')
    import_proof=json.loads((W/'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes());inventory=json.loads((W/'pg3706-pmd-applicability-inventory-v1/manifest.safe.json').read_bytes());require(import_proof['actualExit']==inventory['actualExit']==0,'actual parent proofs')
    tool=ROOT/'tools/quality/SourceFieldNamingInventory.java';data={'source':source,'toolSha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'importManifestSha256':import_proof['result']['serverManifestSha256'],'findingsSha256':inventory['result']['findingsSha256']}
    os.umask(0o077);out=W/'pg3712-field-naming-inventory-v1';out.mkdir();payload='\n'.join(inspect.getsource(x)for x in [require,fields,server])+'\nINPUT='+repr(data)+'\nserver(INPUT)\n';compile(payload,'<source-bound field risk facts>','exec');script=out/'fields.private.py';script.write_text(payload)
    rc,_=run('test ! -e '+BASE+'/runs/PG3712-field-inventory-v1 && mkdir -m700 '+BASE+'/transfer/PG3712-field-inventory-v1',timeout=30);require(rc==0,'new-only fact inventory')
    for p in [tool,script]:
        rc,_=copy(p,BASE+'/transfer/PG3712-field-inventory-v1/',timeout=60);require(rc==0,'fixed source fact tools')
    rc,output=run('python3 -B '+shlex.quote(BASE+'/transfer/PG3712-field-inventory-v1/fields.private.py'),timeout=1000);(out/'observer.private.log').write_text(output)
    value={'actualExit':rc,'productionCandidateSource':source,'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(output.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return rc


if __name__=='__main__':raise SystemExit(main())
