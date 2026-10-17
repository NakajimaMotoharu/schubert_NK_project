"""Conservative current-source technical dispositions; no rule suppression or quality acceptance."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import copy,run
from pmd_contract_disposition import classify_contract
from pg4844_ssc301_302_full import ROOT,W,SOURCE

SLOT='pg4854-current-static-requalified-v1'
OLD='7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4035-current-static-assessments-v1'
DOCS=('documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md','documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md')


def require(v,why):
    if not v:raise ValueError(why)


def witness_ids(row):
    ids=[]
    for item in row.get('currentAssessmentProof',{}).get('currentOwningTests',[]):
        if isinstance(item,dict)and isinstance(item.get('testId'),str):ids.append(item['testId'])
    for item in row.get('owningTestIds',[]):
        if isinstance(item,str):ids.append(item)
        elif isinstance(item,dict)and isinstance(item.get('testId'),str):ids.append(item['testId'])
    if isinstance(row.get('owningTestId'),str):ids.append(row['owningTestId'])
    return sorted(set(ids))


def same_finding(old,new):
    return all(old.get(k)==new.get(k)for k in ('path','sourceSha256','rule','priority','coordinates','message'))


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    from pathlib import Path
    import xml.etree.ElementTree as E
    b=Path('/home/mini/schubert-nk-pgpt');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    static_root=b/'runs/PG4856-static-completion-v1';s=json.loads((static_root/'manifest.safe.json').read_bytes())
    require(sha(static_root/'manifest.safe.json')==data['staticSha256']and s['mainGitSource']==data['source']and s['sameCurrentSixJarAbi']is True and s['rulesSuppressed']is False,'actual exact current static report/source/unchanged rules')
    require(sha(static_root/'pmd.xml')==s['pmd']['reportSha256']and s['pmd']['processingErrors']==0,'actual full raw PMD rows, no errors')
    # The independently qualified manifest is saved in the transfer tool result,
    # not in the whole's directory; the host supplies its actual result SHA too.
    q=data['qualified'];require(q['productionSource']==data['source']and q['tests']==3761 and q['mainClasses']==1647 and q['allOriginalCaseIdentitiesRetained']is True,'actual current independent full scope first')
    require(sha(b/'runs/PG4844-six-v1/manifest.safe.json')==q['serverManifestSha256'],'same actual whole manifest')
    source=b/'source-full-PG4844';candidate=b/'runs/PG4850-ssc301-302-static-input-v1/candidate'
    actual={str(p.relative_to(source)):sha(p)for p in source.glob('src/*/src/main/java/**/*.java')}
    require(len(actual)==849 and actual==s['allMainSha256']==data['sourceSha256'],'all actual current source files')
    require(all(sha(source/p)==h for p,h in data['pomHashes'].items()),'actual current package/dependency graph')
    vendor=b/'runs/PG3706-pmd-inventory-v1/vendor-rules.private.json'
    require(sha(vendor)==data['vendorSha256'],'pinned primary vendor context definitions')
    rules=json.loads(vendor.read_bytes());context=data['context'];context['sourceSha256']=actual
    context['vendorExplicitJ2ee']={r:'J2EE'in rules[r]['description']for r in ('DoNotUseThreads','UseProperClassLoader')}
    require(all(context['vendorExplicitJ2ee'].values()),'vendor requires J2EE premise')
    rows=[]
    for f in E.parse(static_root/'pmd.xml').getroot().findall('{*}file'):
        path=str(Path(f.get('name')).relative_to(candidate));require(path in actual,'every reported path in actual current scope')
        for finding in f.findall('{*}violation'):
            rows.append({'path':path,'sourceSha256':actual[path],'rule':finding.get('rule'),'priority':finding.get('priority'),'coordinates':{k:int(finding.get(k))for k in ('beginline','endline','begincolumn','endcolumn')},'message':(finding.text or '').strip(),'disposition':'UNCLASSIFIED','qualityGatePass':False,'rawWarningRemoved':False})
    require(len(rows)==s['pmd']['rawFindings'],'all raw warnings preserved')
    rows.sort(key=lambda r:(r['path'],r['coordinates']['beginline'],r['rule'],r['coordinates']['begincolumn']))
    for i,row in enumerate(rows,1):row['id']='PMD-04bb-'+str(i).zfill(4)
    context_rows=[]
    for row in rows:
        if row['rule']not in ('DoNotUseThreads','UseProperClassLoader'):continue
        decision=classify_contract(row,context,{})
        require(decision is not None and decision['qualityGatePass']is False,'current approved standalone premise only')
        row.update(decision,currentStandaloneProof={'source':data['source'],'contextSha256':data['contextSha256'],'vendorSha256':data['vendorSha256'],'currentWholeSha256':q['serverManifestSha256']});context_rows.append(row['id'])
    require(len(context_rows)==sum(s['pmd']['ruleCounts'].get(r,0)for r in ('DoNotUseThreads','UseProperClassLoader')),'all current vendor-context rows individually evaluated')
    requalified=[];held=[]
    for old in data['historical']:
        if old['disposition']in ('UNCLASSIFIED','CONTEXT_NOT_APPLICABLE_J2EE_RULE'):continue
        matches=[row for row in rows if same_finding(old,row)]
        if len(matches)!=1:
            held.append({'priorId':old['id'],'reason':'NO_EXACT_UNCHANGED_SOURCE_RULE_COORDINATE_MATCH'});continue
        row=matches[0];ids=witness_ids(old)
        if not ids or any(i not in data['testHashes']or data['testHashes'][i]['old']!=data['testHashes'][i]['current']for i in ids):
            held.append({'priorId':old['id'],'reason':'NAMED_UNCHANGED_OWNING_WITNESS_REQUIRED'});continue
        design=old.get('design')
        if design and data['approvedDocs'].get(design['path'])!=design['sha256']:
            held.append({'priorId':old['id'],'reason':'APPROVED_DESIGN_CHANGED_REQUIRES_NEW_ORACLE'});continue
        witnesses=[]
        for identity in ids:
            cls,method=identity.split('#');module=data['testHashes'][identity]['module'];path=data['testHashes'][identity]['path']
            require(sha(source/path)==data['testHashes'][identity]['current'],'actual unchanged current owning Test source')
            xml=source/('src/schubert-nk-'+module+'/target/surefire-reports/TEST-'+cls+'.xml')
            require(sha(xml)==q['modules'][module]['xmlHashes'][xml.name],'actual current independent owning XML')
            tree=E.parse(xml).getroot();require(all(tree.get(k)=='0'for k in ('failures','errors','skipped'))and any(c.get('name')==method and not any(c.find(k)is not None for k in ('failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'))for c in tree.findall('testcase')),'owning case genuinely passed in current whole')
            witnesses.append({'testId':identity,'testSourceSha256':data['testHashes'][identity]['current'],'currentXmlSha256':sha(xml)})
        require(row['disposition']=='UNCLASSIFIED','no new warning claimed twice')
        row.update(disposition=old['disposition'],basis=old.get('basis','Exact immutable source and unchanged independent current owning tests reconfirm the recorded narrow assessment.'),currentAssessmentProof={'source':data['source'],'currentWholeSha256':q['serverManifestSha256'],'currentOwningTests':witnesses,'fullSourceUnchanged':True,'priorPublicManifestSha256':data['priorPublicManifestSha256'],'priorFindingId':old['id']},qualityGatePass=False,rawWarningRemoved=False)
        requalified.append(row['id'])
    counts=dict(Counter(r['disposition']for r in rows));out=b/'runs/PG4854-current-static-requalified-v1';out.mkdir(mode=0o700)
    (out/'all-findings.safe.json').write_text(json.dumps(rows,sort_keys=True));(out/'held.safe.json').write_text(json.dumps(held,sort_keys=True))
    result={'actualExit':0,'productionSource':data['source'],'rawFindings':len(rows),'technicalDispositions':len(context_rows)+len(requalified),'unclassified':counts.get('UNCLASSIFIED',0),'dispositions':counts,'currentContextIndividuallyRechecked':len(context_rows),'exactSourceWitnessRequalified':len(requalified),'historicalNonContextHeld':held,'allFindingsSha256':sha(out/'all-findings.safe.json'),'heldSha256':sha(out/'held.safe.json'),'staticManifestSha256':data['staticSha256'],'wholeQualificationSha256':data['wholeQualificationSha256'],'priorPublicManifestSha256':data['priorPublicManifestSha256'],'applicableViolationCount':None,'F03Accepted':False,'formalAccepted':False,'rulesChanged':False,'suppressionAdded':False,'rawWarningsRemoved':False,'pmdReissued':False,'vmActions':0,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    require(result['technicalDispositions']+result['unclassified']==len(rows),'no raw finding removed')
    (out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    qualified=json.loads((W/'pg4846-ssc301-302-whole-qualified-v1/manifest.safe.json').read_bytes())
    static=json.loads((W/'pg4856-static-completion-v1/manifest.safe.json').read_bytes())
    require(qualified['actualExit']==static['actualExit']==0 and qualified['source']==static['productionSource']==SOURCE,'same actual full and static first')
    require(not subprocess.check_output(['git','diff',SOURCE,'--','src','pom.xml','.mvn','mvnw'],cwd=ROOT),'unchanged fixed source')
    prior=json.loads((PUBLIC/'manifest.json').read_bytes())
    require(prior['actualExit']==0 and prior['productionSource']==OLD and prior['technicalDispositions']==304,'actual historical304, not a current acceptance')
    require(sha(PUBLIC/'all-1653-findings.json')==prior['files']['all-1653-findings.json'],'exact immutable historical finding records')
    historical=json.loads((PUBLIC/'all-1653-findings.json').read_bytes())
    docs={}
    for path in DOCS:
        old=subprocess.check_output(['git','show',OLD+':'+path],cwd=ROOT);current=subprocess.check_output(['git','show','origin/main:'+path],cwd=ROOT)
        require(old==current and current==(ROOT/path).read_bytes(),'unchanged exact approved standalone architecture')
        docs[path]=hashlib.sha256(current).hexdigest()
    require(not subprocess.check_output(['git','diff',OLD,SOURCE,'--','src/deployment','pom.xml',':(glob)src/*/pom.xml'],cwd=ROOT),'unchanged direct-Java dependencies/deployment')
    require('Executable jar'in (ROOT/DOCS[0]).read_text()and 'Java processを直接ExecStart'in (ROOT/DOCS[1]).read_text(),'explicit approved standalone execution')
    roles={};poms={}
    import xml.etree.ElementTree as E
    for m in ('protocol','storage','bootstrap','api','web','batch'):
        path='src/schubert-nk-'+m+'/pom.xml';node=E.fromstring((ROOT/path).read_bytes());ns={'m':'http://maven.apache.org/POM/4.0.0'}
        require(node.findtext('m:packaging','jar',ns)=='jar','no WAR/EJB deployment')
        deps=[x.findtext('m:groupId','',ns)+':'+x.findtext('m:artifactId','',ns)for x in node.findall('m:dependencies/m:dependency',ns)]
        require(not any(x.startswith(('jakarta.platform:','jakarta.ejb:','javax.ejb:','javax:javaee'))for x in deps),'no managed platform dependency')
        roles['schubert-nk-'+m]='STANDALONE_JAVA_SERVICE'if m in ('api','web','batch')else'LIBRARY_ONLY_IN_STANDALONE_GRAPH';poms[path]=sha(ROOT/path)
    require(not any(p.name in ('ejb-jar.xml','application.xml')for p in (ROOT/'src').rglob('*.xml')),'no managed deployment descriptor')
    test_hashes={};approved={}
    for row in historical:
        if row['disposition']in ('UNCLASSIFIED','CONTEXT_NOT_APPLICABLE_J2EE_RULE'):continue
        if row.get('design'):approved[row['design']['path']]=hashlib.sha256(subprocess.check_output(['git','show','origin/main:'+row['design']['path']],cwd=ROOT)).hexdigest()
        for identity in witness_ids(row):
            if identity.count('#')!=1 or not identity.startswith('dev.codex.schubert.nk.'):continue
            cls,method=identity.split('#')
            paths=[p for p in (ROOT/'src').glob('*/src/test/java/'+cls.replace('.','/')+'.java')]
            if len(paths)!=1:continue
            path=paths[0];relative=path.relative_to(ROOT).as_posix()
            try:old=subprocess.check_output(['git','show',OLD+':'+relative],cwd=ROOT,stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:continue
            test_hashes[identity]={'path':relative,'module':relative.split('/')[1].removeprefix('schubert-nk-'),'current':sha(path),'old':hashlib.sha256(old).hexdigest()}
    context={'source':SOURCE,'approvedDirectJavaProcess':True,'externalJavaEEManaged':False,'noManagedDeploymentDescriptors':True,'moduleRoles':roles,'architectureEvidence':[{'path':p,'originMainSha256':h}for p,h in docs.items()]}
    vendor=json.loads((W/'pg3706-pmd-applicability-inventory-v1/manifest.safe.json').read_bytes())['result']
    data={'source':SOURCE,'qualified':qualified['result'],'wholeQualificationSha256':sha(W/'pg4846-ssc301-302-whole-qualified-v1/manifest.safe.json'),'staticSha256':static['result']['serverManifestSha256'],'sourceSha256':{p.relative_to(ROOT).as_posix():sha(p)for p in ROOT.glob('src/*/src/main/java/**/*.java')},'historical':historical,'priorPublicManifestSha256':sha(PUBLIC/'manifest.json'),'testHashes':test_hashes,'approvedDocs':approved,'pomHashes':poms,'context':context,'contextSha256':hashlib.sha256(json.dumps(context,sort_keys=True).encode()).hexdigest(),'vendorSha256':vendor['vendorRulesSha256']}
    raw='\n'.join(inspect.getsource(f)for f in (require,witness_ids,same_finding,classify_contract,server))+'\nDATA='+repr(data)+'\nserver(DATA)\n'
    from pyflakes.api import check
    require(check(raw,'<current exact raw findings/source/witness requalification>')==0,'complete emitted static0')
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);path=out/'review.private.py';path.write_text(raw)
    remote='/home/mini/schubert-nk-pgpt/transfer/PG4854-current-static-requalified-v1'
    code,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG4854-current-static-requalified-v1 && mkdir -m700 '+remote,timeout=30);require(code==0,'new-only assessment namespace, no replay')
    code,_=copy(path,remote+'/',timeout=60);require(code==0,'complete frozen assessment transfer')
    code,output=run('python3 -B '+remote+'/review.private.py',timeout=180);(out/'observer.private.log').write_text(output)
    value={'actualExit':code,'source':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'payloadSha256':sha(path),'F03Accepted':False,'formalAccepted':False}
    if code==0:value['result']=json.loads(next(line for line in reversed(output.splitlines())if line.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps({k:v for k,v in value.items()if k!='result'}));return code


if __name__=='__main__':raise SystemExit(main())
