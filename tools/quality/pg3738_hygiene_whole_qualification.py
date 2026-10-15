"""Read original3734 only: actual3714 identities, frozen inputs, XML/static/counters/all physical Main."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
from class_source_file import source_file
from lan_server import run,copy
from pg3734_hygiene_full_six import SOURCE,EXPECTED,NEW_CASES,ROOT,W,require
from pg3348_related_boundary_group import classify


def server(data):
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import xml.etree.ElementTree as E
    import zipfile
    b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG3734-six-v1';source=b/'source-full-PG3734';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    v=json.loads((out/'manifest.safe.json').read_bytes());begin=json.loads((out/'begin.safe.json').read_bytes());require(v['actualExit']==v['mavenExit']==0 and not v['issues']and v['sourceInputsUnchanged'],'genuine original whole terminal0')
    require(v['productionSource']==begin['productionSource']==data['source']and begin['sourceSnapshotHead']==data['snapshot'],'same actual source/snapshot')
    require(sha(b/'transfer/PG3734-source.tar')==begin['sourceArchiveSha256']and all(sha(source/p)==h for p,h in begin['inputs'].items()),'all actual frozen inputs/archive remained unchanged')
    authority=b/'runs/PG3412-six-v1/manifest.safe.json';require(sha(authority)==data['priorManifestSha256'],'immutable actual old3712 authority')
    modules={};coverage={};jars={};all_cases=set();old_cases=set();physical={};changed=[];start=datetime.datetime.fromisoformat(begin['startUTC']).timestamp()
    for module,(nt,ns,nc)in data['expected'].items():
        t=source/('src/schubert-nk-'+module+'/target');paths=sorted((t/'surefire-reports').glob('TEST-*.xml'));roots=[E.parse(p).getroot()for p in paths];require(len(paths)==ns and sum(len(r.findall('testcase'))for r in roots)==nt,'independent exact module counts')
        actual=classify(roots,{r.get('name'):len(r.findall('testcase'))for r in roots});all_cases.update(actual)
        prior=b/'runs/PG3412-six-v1'/module;oldroots=[E.parse(p).getroot()for p in(prior/'surefire-reports').glob('TEST-*.xml')];old_cases.update(classify(oldroots,{r.get('name'):len(r.findall('testcase'))for r in oldroots}))
        require(all(p.stat().st_mtime>=start and sha(p)==sha(out/module/'surefire-reports'/p.name)for p in paths),'all fresh original/saved XML exactly same bytes')
        static=t/'spotbugsXml.xml';require(not E.parse(static).getroot().findall('.//BugInstance'),'six-module existing static0, not all F03')
        jar=t/('schubert-nk-'+module+'-0.1.0-SNAPSHOT.jar');old=prior/jar.name;require(sha(old)==data['priorJarHashes'][module],'original prior physical Jar identity');images=[]
        for p in [old,jar]:
            with zipfile.ZipFile(p)as z:
                require(len(z.namelist())==len(set(z.namelist())),'all physical members unique');images.append({n:z.read(n)for n in z.namelist()})
        require(images[0].keys()==images[1].keys(),'all original physical class/resource inventory retained')
        classes=[n for n in images[1]if n.endswith('.class')];require(len(classes)==nc,'all physical Main cardinality')
        delta=[]
        for name,raw in images[1].items():
            if raw==images[0][name]:continue
            require(name.endswith('.class'),'non-class Main/resource unchanged')
            filename=source_file(raw);require(filename==source_file(images[0][name]),'same actual declaring SourceFile')
            path='src/schubert-nk-'+module+'/src/main/java/'+str(Path(name).parent/filename)
            require(path in data['approvedChangedSources'],'every physical delta belongs to independently proven actual source family')
            item={'module':module,'class':name,'sourcePath':path,'oldSha256':hashlib.sha256(images[0][name]).hexdigest(),'newSha256':hashlib.sha256(raw).hexdigest()};delta.append(item);changed.append(item)
        physical[module]={n:hashlib.sha256(images[1][n]).hexdigest()for n in classes}
        cov=t/'site/jacoco/jacoco.xml';coverage[module]={c.get('type'):{'missed':int(c.get('missed')),'covered':int(c.get('covered'))}for c in E.parse(cov).getroot().findall('counter')}
        report_names={c.get('name')+'.class'for p in E.parse(cov).getroot().findall('package')for c in p.findall('class')};oldcov=prior/'jacoco.xml';require(oldcov.is_file(),'immutable original saved coverage XML authority')
        old_names={c.get('name')+'.class'for p in E.parse(oldcov).getroot().findall('package')for c in p.findall('class')};require(report_names==old_names and report_names<=set(classes),'same exact original JaCoCo analysis class inventory, no new removal/exclusion')
        modules[module]={'tests':nt,'suites':ns,'mainClasses':nc,'xmlHashes':{p.name:sha(p)for p in paths},'staticSha256':sha(static),'coverageXmlSha256':sha(cov),'originalCoverageXmlSha256':sha(oldcov),'jacocoReportClasses':len(report_names),'originalSameJaCoCoUnreportedPhysicalClasses':sorted(set(classes)-report_names),'physicalChangedClasses':len(delta)};jars[module]=sha(jar)
    additions={tuple(x)for x in data['newCases']};require(len(old_cases)==3712 and len(additions)==2 and not old_cases&additions and all_cases==old_cases|additions and len(all_cases)==3714,'all original3712 exact identities retained plus exactly2 actual independent Root tests')
    result={'actualExit':0,'productionSource':data['source'],'sourceSnapshot':data['snapshot'],'sourceArchiveSha256':begin['sourceArchiveSha256'],'run':'PG3734-six-v1','tests':len(all_cases),'suites':sum(m['suites']for m in modules.values()),'mainClasses':sum(m['mainClasses']for m in modules.values()),'modules':modules,'coverage':coverage,'jarHashes':jars,'allPhysicalMainSha256':physical,'changedClasses':changed,'allOriginalCaseIdentitiesRetained':True,'newCases':data['newCases'],'FESFlakyNotRun':0,'staticSixModules':0,'allSixMainBuildsPassed':True,'serverManifestSha256':sha(out/'manifest.safe.json'),'candidateNativePending':True,'oldNativeImported':False,'F03Accepted':False,'formalAccepted':False,'global100':False,'vmActions':0,'startUTC':begin['startUTC'],'endUTC':v.get('endUTC'),'qualifiedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    qualified=b/'runs/PG3738-hygiene-whole-qualified-v1';qualified.mkdir();(qualified/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['qualificationManifestSha256']=sha(qualified/'manifest.safe.json');print(json.dumps(result))


def qualification_inputs(original):
    prior=json.loads((W/'pg3414-outbox-full-qualified-v1/manifest.safe.json').read_bytes())['result'];changed=subprocess.check_output(['git','diff','--name-only',prior['sourceSnapshot'],original['snapshot'],'--',':(glob)src/*/src/main/java/**/*.java'],cwd=ROOT,text=True).splitlines()
    return {'source':SOURCE,'snapshot':original['snapshot'],'expected':EXPECTED,'newCases':NEW_CASES,'priorManifestSha256':prior['serverManifestSha256'],'priorJarHashes':prior['jarHashes'],'approvedChangedSources':changed}


def qualification_payload(original):
    return '\n'.join(inspect.getsource(x)for x in [require,source_file,classify,server])+'\nserver('+repr(qualification_inputs(original))+')\n'


def main():
    original=json.loads((W/'pg3734-server-six-v1/manifest.safe.json').read_bytes());require(original['actualExit']==0 and original['productionSource']==SOURCE,'genuine original whole wrapper0, not duplicate run')
    os.umask(0o077);out=W/'pg3738-hygiene-whole-qualified-v1';out.mkdir();script=out/'qualify.private.py';script.write_text(qualification_payload(original));dest='/home/mini/schubert-nk-pgpt/transfer/PG3738-hygiene-whole-qualified-v1';rc,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3738-hygiene-whole-qualified-v1 && mkdir -m700 '+dest,timeout=30);require(rc==0,'new-only independent qualification');rc,_=copy(script,dest+'/',timeout=60);require(rc==0,'complete independent namespace')
    rc,text=run('python3 -B '+dest+'/qualify.private.py',timeout=180);(out/'observer.private.log').write_text(text);value={'actualExit':rc,'source':SOURCE,'payloadSha256':hashlib.sha256(script.read_bytes()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(text.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}))
    if rc==0:print(json.dumps({k:value['result'][k]for k in ['tests','suites','mainClasses','qualificationManifestSha256','candidateNativePending']}))
    return rc


if __name__=='__main__':raise SystemExit(main())
