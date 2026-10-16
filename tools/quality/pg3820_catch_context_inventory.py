"""Read-only compiler facts for all573 source-bound generic catches; no dispositions or reruns."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run
from git_source_contract import last_main_source
from source_catch_context_inventory_test import facts
from pg3744_pmd_contract_classification import require
from pg3798_hygiene_current_observer import SOURCE,BOM

ROOT=Path(__file__).resolve().parents[2];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379');SLOT='pg3820-catch-context-inventory-v1';BASE='/home/mini/schubert-nk-pgpt'


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E
    os.umask(0o077);base=Path('/home/mini/schubert-nk-pgpt');out=base/'runs/PG3820-catch-context-inventory-v1';out.mkdir();(out/'classes').mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=base/'source-full-PG3734'
    require({str(p.relative_to(source)):sha(p)for p in source.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all849 exact current frozen Main')
    qualification=base/'runs/PG3738-hygiene-whole-qualified-v1/manifest.safe.json';require(sha(qualification)==data['qualificationSha256'],'genuine current whole authority unchanged')
    q=json.loads(qualification.read_bytes());require(q['actualExit']==0 and q['productionSource']==data['source']and q['tests']==3714,'current3714 authority')
    static=base/'runs/PG3730-octal-candidate-static-v1';require(sha(static/'manifest.safe.json')==data['staticManifestSha256'],'actual fixed static authority');meta=json.loads((static/'manifest.safe.json').read_bytes());report=static/'pmd.xml';require(sha(report)==meta['pmd']['reportSha256'],'same raw1840 PMD no rerun')
    candidates=base/'runs/PG3726-octal-candidate-v1/candidate';rows=[]
    for file in E.parse(report).getroot().findall('{*}file'):
        path=str(Path(file.get('name')).relative_to(candidates));require(path in data['sourceSha256'],'all source paths known')
        for v in file.findall('{*}violation'):
            if v.get('rule')=='AvoidCatchingGenericException':rows.append({'path':path,'rule':v.get('rule'),'beginline':int(v.get('beginline')),'endline':int(v.get('endline')),'begincolumn':int(v.get('begincolumn')),'endcolumn':int(v.get('endcolumn')),'sourceSha256':data['sourceSha256'][path]})
    require(len(rows)==573,'all573 exact genericcatch findings')
    prior=base/'runs/PG3690-import-candidate-v1';require(sha(prior/'manifest.safe.json')==data['classpathAuthoritySha256'],'unchanged qualified semantic type classpath');cpmeta=json.loads((prior/'manifest.safe.json').read_bytes())
    tool=base/'transfer/PG3820-catch-context-inventory-v1/SourceCatchContextInventory.java';require(sha(tool)==data['toolSha256'],'exact compiler-fact tool')
    java=base/'tools/jdk-25.0.4/bin/java';javac=base/'tools/jdk-25.0.4/bin/javac';compiled=subprocess.run([str(javac),'-Xlint:all','-Werror','-d',str(out/'classes'),str(tool)],capture_output=True,timeout=30);(out/'compile.private.log').write_bytes(compiled.stdout+compiled.stderr);require(compiled.returncode==0,'compiler fact tool lint0')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'begin.safe.json').write_text(json.dumps({'startUTC':started,'pid':os.getpid(),'ticks':int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]),'source':data['source'],'MainChanged':False,'vmActions':0}));joined=[];modules={}
    for module,item in cpmeta['modules'].items():
        targets=[r for r in rows if r['path'].split('/')[1]=='schubert-nk-'+module]
        if not targets:continue
        cp=item['phases']['after']['command'][-1]
        def cp_hash():
            values={}
            for p in map(Path,cp.split(':')):
                require(p.is_absolute()and p.exists(),'exact qualified type dependencies')
                values[str(p)]={str(x.relative_to(p)):sha(x)for x in p.rglob('*')if x.is_file()and x.suffix in {'.java','.class'}}if p.is_dir()else sha(p)
            return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
        require(cp_hash()==item['classpathInputsSha256'],'actual prior classpath unchanged')
        scope=source/('src/schubert-nk-'+module+'/src/main/java');r=subprocess.run([str(java),'-Xmx1536m','-cp',str(out/'classes'),'SourceCatchContextInventory',str(scope),cp],capture_output=True,text=True,timeout=180);(out/(module+'-catch.safe.tsv')).write_text(r.stdout);(out/(module+'-catch.private.log')).write_text(r.stderr);require(r.returncode==0,'all actual catch symbols resolve')
        values=facts(r.stdout)
        for row in targets:
            path=str(Path(row['path']).relative_to('src/schubert-nk-'+module+'/src/main/java'));matches=[f for f in values if f['path']==path and int(f['firstLine'])<=row['beginline']<=int(f['lastLine'])]
            require(len(matches)==1,'one exact resolved catch per finding coordinate')
            row['facts']=matches[0];row['classification']='FACTS_ONLY_NOT_DISPOSITION';joined.append(row)
        require(cp_hash()==item['classpathInputsSha256'],'all dependency bytes remain unchanged');modules[module]={'targetFindings':len(targets),'allCatchFacts':len(values),'factSha256':sha(out/(module+'-catch.safe.tsv')),'actualExit':0};(out/'progress.safe.json').write_text(json.dumps({'modules':list(modules),'findingsJoined':len(joined)}))
    require(len(joined)==573,'no warning lost');require({str(p.relative_to(source)):sha(p)for p in source.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all849 unchanged')
    (out/'joined-facts.safe.json').write_text(json.dumps(joined,sort_keys=True))
    modes=Counter('FINAL_SAME_PARAMETER_NO_ASSIGNMENT'if r['facts']['finalDirect']=='true'and r['facts']['assignments']=='0'else'OTHER_REQUIRES_REVIEW'for r in joined)
    value={'actualExit':0,'productionSource':data['source'],'currentBOM':data['BOM'],'matchedFindings':573,'modules':modules,'controlShapeFacts':dict(modes),'factsSha256':sha(out/'joined-facts.safe.json'),'rawPmdFindings':1840,'technicalDispositionsUnchanged':248,'unclassifiedUnchanged':1592,'applicableViolationCount':None,'F03Accepted':False,'formalAccepted':False,'MainChanged':False,'pmdReissued':False,'newRegressionIssued':False,'vmActions':0,'startedUTC':started,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));value['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(value))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean fixed source for host-only fact discovery');require(last_main_source(ROOT)==SOURCE,'current Main fixed while Root running')
    whole=json.loads((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes());static=json.loads((W/'pg3730-octal-candidate-static-v1/manifest.safe.json').read_bytes());prior=json.loads((W/'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes())
    data={'source':SOURCE,'BOM':BOM,'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'qualificationSha256':whole['result']['qualificationManifestSha256'],'staticManifestSha256':static['result']['serverManifestSha256'],'classpathAuthoritySha256':prior['result']['serverManifestSha256'],'toolSha256':hashlib.sha256((ROOT/'tools/quality/SourceCatchContextInventory.java').read_bytes()).hexdigest()}
    os.umask(0o077);out=W/SLOT;out.mkdir();payload='\n'.join(inspect.getsource(x)for x in [require,facts,server])+'\nserver('+repr(data)+')\n';compile(payload,'<readonly source-bound573catch facts>','exec');script=out/'facts.private.py';script.write_text(payload);dest=BASE+'/transfer/PG3820-catch-context-inventory-v1'
    code,_=run('test ! -e '+BASE+'/runs/PG3820-catch-context-inventory-v1 && mkdir -m700 '+dest,timeout=30);require(code==0,'new-only host fact discovery')
    for p in [script,ROOT/'tools/quality/SourceCatchContextInventory.java']:
        code,_=copy(p,dest+'/',timeout=60);require(code==0,'exact host fact input transfer')
    code,output=run('python3 -B '+dest+'/facts.private.py',timeout=1000);(out/'observer.private.log').write_text(output)
    value={'actualExit':code,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'formalAccepted':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
