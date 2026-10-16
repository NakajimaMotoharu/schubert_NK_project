"""Exact JDK self-suppression contract assessments; raw warnings and gate failure remain."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from lan_server import copy,run
from git_source_contract import last_main_source
from pg3744_pmd_contract_classification import require
from pg3798_hygiene_current_observer import SOURCE
from source_suppression_identity_inventory_test import facts,FIXTURE

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
BASE='/home/mini/schubert-nk-pgpt';SLOT='pg3864-suppression-identity-review-v1'


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import subprocess
    import xml.etree.ElementTree as E
    base=Path('/home/mini/schubert-nk-pgpt');out=base/'runs/PG3864-suppression-identity-review-v1';out.mkdir();classes=out/'classes';classes.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=base/'source-full-PG3734'
    qualified=base/'runs/PG3738-hygiene-whole-qualified-v1/manifest.safe.json';require(sha(qualified)==data['qualificationSha256'],'original current3714 qualification');q=json.loads(qualified.read_bytes());require(q['actualExit']==0 and q['productionSource']==data['source'] and q['tests']==3714,'genuine current whole')
    previous=base/'runs/PG3744-pmd-contract-classification-v1';require(sha(previous/'manifest.safe.json')==data['priorManifestSha256'],'exact technical248 authority');prior=json.loads((previous/'manifest.safe.json').read_bytes());path=previous/'dispositions.safe.json';require(sha(path)==prior['dispositionSha256'],'all original1840 records unchanged');rows=json.loads(path.read_bytes());require(len(rows)==1840,'raw1840 retained')
    require({str(p.relative_to(source)):sha(p)for p in source.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all849 actual current exact')
    scope=base/'transfer/PG3864-suppression-identity-review-v1';tool=scope/'SourceSuppressionIdentityInventory.java';fixture=scope/'Fixture.java';require(sha(tool)==data['toolSha256']and sha(fixture)==data['fixtureSha256'],'frozen tool and independent JDK vectors')
    jdk=base/'tools/jdk-25.0.4/bin';phases=[]
    for name,command in [('compile-tool',[str(jdk/'javac'),'-Xlint:all','-Werror','-d',str(classes),str(tool)]),('compile-fixture',[str(jdk/'javac'),'-d',str(classes),str(fixture)]),('independent-jdk-fixture',[str(jdk/'java'),'-cp',str(classes),'Fixture'])]:
        r=subprocess.run(command,capture_output=True,text=True,timeout=30);(out/(name+'.private.log')).write_text(r.stdout+r.stderr);require(r.returncode==0,'actual independent JDK fixture/compile');phases.append({'name':name,'exitCode':r.returncode,'stdoutSha256':hashlib.sha256(r.stdout.encode()).hexdigest()})
        if name=='independent-jdk-fixture':require(r.stdout=='JDK_IDENTITY_CONTRACT_OK\n','same identity rejects; distinct overridden-equals object allowed')
    authority=base/'runs/PG3690-import-candidate-v1/manifest.safe.json';require(sha(authority)==data['classpathAuthoritySha256'],'fixed resolved classpath');cpmeta=json.loads(authority.read_bytes());allfacts=[];suite_hashes={}
    targets=[r for r in rows if r['rule']=='CompareObjectsWithEquals'];require(len(targets)==65,'all65 exact object equality warnings')
    for module,item in cpmeta['modules'].items():
        selected=[r for r in targets if r['path'].split('/')[1]=='schubert-nk-'+module]
        if not selected:continue
        cp=item['phases']['after']['command'][-1]
        def cp_hash():
            values={}
            for p in map(Path,cp.split(':')):
                require(p.is_absolute()and p.exists(),'qualified type dependency')
                values[str(p)]={str(x.relative_to(p)):sha(x)for x in p.rglob('*')if x.is_file()and x.suffix in {'.java','.class'}}if p.is_dir()else sha(p)
            return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
        require(cp_hash()==item['classpathInputsSha256'],'all dependency inputs unchanged')
        r=subprocess.run([str(jdk/'java'),'-Xmx1536m','-cp',str(classes),'SourceSuppressionIdentityInventory',str(source/('src/schubert-nk-'+module+'/src/main/java')),cp],capture_output=True,text=True,timeout=180);(out/(module+'-identity.safe.tsv')).write_text(r.stdout);(out/(module+'-identity.private.log')).write_text(r.stderr);require(r.returncode==0,'resolved exact identity facts')
        actual=facts(r.stdout);allfacts.extend([{'module':module,**f}for f in actual]);require(cp_hash()==item['classpathInputsSha256'],'type classpath remains byte-identical')
        for row in selected:
            relative=str(Path(row['path']).relative_to('src/schubert-nk-'+module+'/src/main/java'));line=row['coordinates']['beginline'];column=row['coordinates']['begincolumn']
            matches=[f for f in actual if f['path']==relative and (int(f['firstLine']),int(f['firstColumn']))<=(line,column)<=(int(f['lastLine']),int(f['lastColumn']))]
            require(len(matches)<=1,'at most one exact resolved comparison')
            if not matches:continue
            require(row['disposition']=='UNCLASSIFIED'and sha(source/row['path'])==row['sourceSha256'],'only exact unresolved finding assessed')
            cls='dev.codex.schubert.nk.'+relative.removeprefix('dev/codex/schubert/nk/').removesuffix('.java').replace('/','.')+'Test'
            xml=base/'runs/PG3734-six-v1'/module/'surefire-reports'/('TEST-'+cls+'.xml')
            # A narrow language/API-contract assessment is not a functional
            # exemption. Keep exact actual owning-suite witnesses if present.
            witnesses=[]
            if xml.exists():
                require(sha(xml)==q['modules'][module]['xmlHashes'][xml.name],'genuine same-source owning suite')
                tree=E.parse(xml).getroot();cases=tree.findall('testcase');require(cases and not any(n.tag in {'failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'}for n in tree.iter()),'actual clean owning suite')
                witnesses=[cls+'#'+c.get('name')for c in cases];suite_hashes[str(xml.relative_to(base))]=sha(xml)
            row.update(disposition='REQUIRED_JDK_SELF_SUPPRESSION_IDENTITY_GUARD',basis='JDK Throwable.addSuppressed rejects exactly self identity. Distinct Throwables may override equals to compare equal. Resolved positive-conjunct local-variable != guard protects the actual final JDK addSuppressed receiver/argument, without reassignment; replacing it by value equality changes secondary-failure retention.',scope='EXACT_LANGUAGE_API_CONTRACT_ONLY_NOT_FUNCTIONAL_GATE',qualityGatePass=False,typedIdentityFact=matches[0],independentJdkFixtureSha256=data['fixtureSha256'],currentWholeQualificationSha256=data['qualificationSha256'],owningTestIds=witnesses)
    counts=dict(Counter(r['disposition']for r in rows));new=counts.get('REQUIRED_JDK_SELF_SUPPRESSION_IDENTITY_GUARD',0);require(0<new<=65 and counts['UNCLASSIFIED']==1592-new,'only exact new assessments; raw1840 fixed')
    require({str(p.relative_to(source)):sha(p)for p in source.glob('src/*/src/main/java/**/*.java')}==data['sourceSha256'],'all Main unchanged after read')
    (out/'all1840-dispositions.safe.json').write_text(json.dumps(rows,sort_keys=True));(out/'resolved-identity-facts.safe.json').write_text(json.dumps(allfacts,sort_keys=True));(out/'owning-suite-hashes.safe.json').write_text(json.dumps(suite_hashes,sort_keys=True))
    result={'actualExit':0,'productionSource':data['source'],'rawFindings':1840,'newTechnicalAssessments':new,'technicalDispositions':248+new,'unclassified':1592-new,'applicableViolationCount':None,'dispositions':counts,'all65CompareFindingsRetained':True,'resolvedGuardFacts':len(allfacts),'independentJdkPhases':phases,'dispositionsSha256':sha(out/'all1840-dispositions.safe.json'),'factsSha256':sha(out/'resolved-identity-facts.safe.json'),'suiteHashesSha256':sha(out/'owning-suite-hashes.safe.json'),'MainChanged':False,'pmdReissued':False,'regressionReissued':False,'vmActions':0,'suppressionAdded':False,'F03Accepted':False,'formalAccepted':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};(out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    require(not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT),'clean current fact review');require(last_main_source(ROOT)==SOURCE,'same fixed Main while existing Root runs')
    q=json.loads((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes());prior=json.loads((W/'pg3744-pmd-contract-classification-v1/manifest.safe.json').read_bytes());cp=json.loads((W/'pg3690-import-candidate-stage-v1/manifest.safe.json').read_bytes())
    data={'source':SOURCE,'qualificationSha256':q['result']['qualificationManifestSha256'],'priorManifestSha256':prior['result']['serverManifestSha256'],'classpathAuthoritySha256':cp['result']['serverManifestSha256'],'sourceSha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'toolSha256':hashlib.sha256((ROOT/'tools/quality/SourceSuppressionIdentityInventory.java').read_bytes()).hexdigest(),'fixtureSha256':hashlib.sha256(FIXTURE.encode()).hexdigest()}
    os.umask(0o077);out=W/SLOT;out.mkdir();fixture=out/'Fixture.java';fixture.write_text(FIXTURE);script=out/'review.private.py';script.write_text('\n'.join(inspect.getsource(x)for x in [require,facts,server])+'\nserver('+repr(data)+')\n');compile(script.read_text(),'<exact current JDK self-suppression review>','exec');dest=BASE+'/transfer/PG3864-suppression-identity-review-v1'
    code,_=run('test ! -e '+BASE+'/runs/PG3864-suppression-identity-review-v1 && mkdir -m700 '+dest,timeout=30);require(code==0,'new-only read-only host review')
    for p in [script,fixture,ROOT/'tools/quality/SourceSuppressionIdentityInventory.java']:
        code,_=copy(p,dest+'/',timeout=60);require(code==0,'exact frozen tool fixture transfer')
    code,output=run('python3 -B '+dest+'/review.private.py',timeout=1000);(out/'observer.private.log').write_text(output);value={'actualExit':code,'productionSource':SOURCE,'payloadSha256':hashlib.sha256(script.read_bytes()).hexdigest(),'formalAccepted':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return code


if __name__=='__main__':raise SystemExit(main())
