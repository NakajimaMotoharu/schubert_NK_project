"""Retain raw1840; source-bound technical context decisions with actual current independent XML."""
import hashlib
import inspect
import json
import os
import subprocess
from lan_server import run,copy
from pmd_contract_disposition import classify_contract
from git_source_contract import last_main_source,POM_PATHSPEC
from pg3734_hygiene_full_six import ROOT,W,SOURCE,require

PREFIX='src/schubert-nk-'
SPECS=[
 ('UnusedReturnValue','api','api/logging/RequestLogDetails','api/logging/RequestLogDetailsTest','unsafeMalformedDuplicateAndWrongTypesAreRejected','reader.peek();','VALIDATING_PEEK_SIDE_EFFECT','Pinned Gson STRICT final peek after root consumes whitespace and rejects every trailing value by exception. Its only successful value is END_DOCUMENT, not a validation result that can silently be ignored.'),
 ('UnusedReturnValue','batch','batch/platform/BrokerJournalEvidence','batch/platform/BrokerJournalEvidenceTest','bj2478002CanonicalAndStrictJsonBoundariesDoNotNormalizeUnavailableEvidence','reader.peek();','VALIDATING_PEEK_SIDE_EFFECT','Pinned STRICT final peek verifies EOF; independent malformed/trailing evidence cannot prove journal success. Do not remove the validating read or introduce an unreachable result branch.'),
 ('UnusedReturnValue','bootstrap','bootstrap/ReleaseInventory','bootstrap/ReleaseInventoryTest','bomProfile003ByteUtf8AndDocumentBounds','reader.peek();','VALIDATING_PEEK_SIDE_EFFECT','Pinned STRICT final peek rejects extra BOM document before returning an inventory. Independent malformed/trailing bytes are rejected, not silently accepted.'),
 ('UnusedReturnValue','web','web/session/SessionAttributeCodec','web/session/SessionAttributeCodecTest','web012MalformedUtf8AndBoundedDocumentsRejectSafely','reader.peek();','VALIDATING_PEEK_SIDE_EFFECT','Pinned STRICT final peek rejects trailing saved-session data by exception; every success already means EOF. No ignored status/code permits malformed input.'),
 ('NullAssignment','api','api/idempotency/CanonicalField','api/idempotency/OperationFingerprintTest','nfcNormalizationAndNullEmptyDistinctionAreStable','value = value == null ? null : value.clone();','REQUIRED_NULL_WIRE_SENTINEL','Approved SS324 section3.1 requires null lengthFFFFFFFF versus empty length0; nullable defensive copy must preserve this distinction.'),
 ('ReturnEmptyCollectionRatherThanNull','api','api/idempotency/CanonicalField','api/idempotency/OperationFingerprintTest','nfcNormalizationAndNullEmptyDistinctionAreStable','return value == null ? null : value.clone();','REQUIRED_NULL_WIRE_SENTINEL','Empty-array substitution would change approved canonical bytes and HMAC. Explicit @Nullable return and independent null/empty golden preserve data compatibility.'),
 ('NullAssignment','batch','batch/platform/LinuxSystemdQuery','batch/platform/LinuxSystemdQueryTest','everyBoundaryIoRuntimeFatalAndUnknownCloseRemainFailure','if (session.closed()) pending = null;','EXPLICIT_OWNERSHIP_TRANSFER_SENTINEL','Clear pending capability only after the original session positively reports closed; unknown close retains ownership/isolation and fresh capability creation is refused. Null denotes no retained session, not a nullable return dereferenced as success.'),
 ('NullAssignment','bootstrap','api/maintenance/InspectorAesCredential','api/maintenance/InspectorAesCredentialTest','consumedInputAndCopiedKeysDoNotAlias','decoded = null;','EXPLICIT_OWNERSHIP_TRANSFER_SENTINEL','Transfer exclusive decoded buffer ownership to the credential. Clearing the local reference prevents finally wiping a live transferred key; input/encoded buffers still wipe and destruction/copies are independently tested.')]


def server(data):
    from collections import Counter
    import datetime
    import hashlib
    import json
    import os
    from pathlib import Path
    import xml.etree.ElementTree as E
    os.umask(0o077);b=Path('/home/mini/schubert-nk-pgpt');out=b/'runs/PG3744-pmd-contract-classification-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();fixed=b/'runs/PG3730-octal-candidate-static-v1';require(sha(fixed/'manifest.safe.json')==data['staticManifestSha256'],'actual current fixed raw1840 authority');s=json.loads((fixed/'manifest.safe.json').read_bytes());require(sha(fixed/'pmd.xml')==s['pmd']['reportSha256'],'original current raw warnings unchanged')
    fullpath=b/'runs/PG3738-hygiene-whole-qualified-v1/manifest.safe.json';require(sha(fullpath)==data['wholeQualificationSha256'],'actual current independent3714 authority');full=json.loads(fullpath.read_bytes());require(full['productionSource']==data['source']and full['actualExit']==0 and full['tests']==3714,'genuine current source and independent full XML required')
    root=b/'runs/PG3726-octal-candidate-v1/candidate';source=b/'source-full-PG3734';binding=s['octalDelta']['allSourceSha256'];require(binding==data['architecture']['sourceSha256'],'all849 exact current source')
    for p,h in binding.items():require(sha(root/p)==sha(source/p)==h,'actual PMD/current whole all849 exact bytes')
    vendor=b/'runs/PG3706-pmd-inventory-v1/vendor-rules.private.json';require(sha(vendor)==data['vendorRulesSha256'],'original canonical vendor explanations');rules=json.loads(vendor.read_bytes())
    context=data['architecture'];context['vendorExplicitJ2ee']={n:'J2EE'in rules[n]['description']for n in ['DoNotUseThreads','UseProperClassLoader']};require(all(context['vendorExplicitJ2ee'].values()),'both primary vendor premises expressly J2EE')
    rows=[]
    for file in E.parse(fixed/'pmd.xml').getroot().findall('{*}file'):
        p=str(Path(file.get('name')).relative_to(root));require(p in binding,'bound report path')
        for v in file.findall('{*}violation'):rows.append({'path':p,'sourceSha256':binding[p],'rule':v.get('rule'),'priority':v.get('priority'),'coordinates':{k:int(v.get(k))for k in ['beginline','endline','begincolumn','endcolumn']},'message':(v.text or '').strip(),'disposition':'UNCLASSIFIED'})
    require(len(rows)==1840,'all original1840 findings retained')
    rows.sort(key=lambda r:(r['path'],r['coordinates']['beginline'],r['rule'],r['coordinates']['begincolumn']));contracts={}
    for spec in data['specs']:
        rule,path,testclass,method,needle,disposition,basis=spec;items=[r for r in rows if r['rule']==rule and r['path']==path];require(len(items)==1,'one exact manually reviewed statement per contract');line=items[0]['coordinates']['beginline'];text=(source/path).read_text();require(needle in text.splitlines()[line-1],'exact actual reviewed statement')
        if rule=='UnusedReturnValue':require('reader.setStrictness(Strictness.STRICT);'in text and 'reader.endObject();'in text,'pinned STRICT closed-root side-effect, never lenient')
        module=path.split('/')[1].removeprefix('schubert-nk-');xml=b/'runs/PG3734-six-v1'/module/'surefire-reports'/('TEST-'+testclass+'.xml');require(sha(xml)==full['modules'][module]['xmlHashes'][xml.name],'same qualified actual current XML');xr=E.parse(xml).getroot();case=[c for c in xr.findall('testcase')if c.get('name')==method];require(len(case)==1 and not any(c.tag in {'failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'}for c in case[0].iter()),'named independent positive/negative witness actually passed')
        contracts[(rule,path)]={'sourceSha256':binding[path],'wholeSource':data['source'],'independentXmlQualified':True,'exactFindingLines':[line],'evidence':[{'testId':testclass+'#'+method,'currentSuiteXmlSha256':sha(xml),'wholeQualificationSha256':data['wholeQualificationSha256']},*data['contractDesignEvidence']],'disposition':disposition,'basis':basis}
    # Revalidate the original validation-label FP only when exact code/Test bytes remain unchanged.
    label=data['label'];items=[r for r in rows if r['rule']=='HardCodedCryptoKey'];require(len(items)==1,'one exact label finding');r=items[0];require(r['path']==label['finding']['file']and r['sourceSha256']==label['sourceSha256'],'exact unchanged label source, not relabeled modified code')
    testclass='dev.codex.schubert.nk.api.idempotency.ResponseSnapshotCodecTest';xml=b/'runs/PG3734-six-v1/api/surefire-reports'/('TEST-'+testclass+'.xml');require(sha(xml)==full['modules']['api']['xmlHashes'][xml.name]and any(c.get('name')==label['existingActualWitness']['method']for c in E.parse(xml).getroot().findall('testcase')),'actual current same independent JCE golden witness')
    contracts[(r['rule'],r['path'])]={'sourceSha256':r['sourceSha256'],'wholeSource':data['source'],'independentXmlQualified':True,'exactFindingLines':[r['coordinates']['beginline']],'evidence':[data['labelProofSha256'],label['sameRuleCanaryManifestSha256'],sha(xml)],'disposition':'FALSE_POSITIVE_VALIDATION_LABEL_NOT_KEY','basis':label['basis']}
    for i,row in enumerate(rows,1):
        row['id']='PMD-7fff-'+str(i).zfill(4);decision=classify_contract(row,context,contracts)
        if decision:row.update(decision)
    counts=dict(Counter(r['disposition']for r in rows));require(counts=={'CONTEXT_NOT_APPLICABLE_J2EE_RULE':239,'FALSE_POSITIVE_VALIDATION_LABEL_NOT_KEY':1,'VALIDATING_PEEK_SIDE_EFFECT':4,'REQUIRED_NULL_WIRE_SENTINEL':2,'EXPLICIT_OWNERSHIP_TRANSFER_SENTINEL':2,'UNCLASSIFIED':1592},'exact technical248/1840 partition, no warning suppressed')
    out.mkdir();(out/'dispositions.safe.json').write_text(json.dumps(rows,sort_keys=True));result={'actualExit':0,'productionCandidateSource':data['source'],'rawFindings':1840,'technicalDispositions':248,'unclassified':1592,'applicableViolationCount':None,'dispositions':counts,'all1840SourceAndCoordinatesRetained':True,'actualCurrentWholeTestRefs':9,'staticReportSha256':s['pmd']['reportSha256'],'wholeQualificationSha256':data['wholeQualificationSha256'],'architectureProofSha256':data['architectureProofSha256'],'dispositionSha256':sha(out/'dispositions.safe.json'),'rulesChanged':False,'sourceExcluded':False,'suppressionAdded':False,'MainChanged':False,'pmdReissued':False,'businessOrVmReplay':False,'F03Accepted':False,'formalAccepted':False,'recordedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};(out/'manifest.safe.json').write_text(json.dumps(result,sort_keys=True));result['serverManifestSha256']=sha(out/'manifest.safe.json');print(json.dumps(result))


def main():
    require(last_main_source(ROOT)==SOURCE,'current Main remains exact7fff while no new behavior is changed');whole=json.loads((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes());require(whole['actualExit']==0,'genuine independent full0 before disposition')
    fixed=json.loads((W/'pg3730-octal-candidate-static-v1/manifest.safe.json').read_bytes());s=fixed['result'];files=s['octalDelta']['allSourceSha256'];require(files=={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in ROOT.glob('src/*/src/main/java/**/*.java')},'all current849 exact')
    prior=json.loads((W/'pg3708-pmd-first-dispositions-v1/architecture.safe.json').read_bytes());docs=list(prior['approvedDocumentSha256']);docs+=['documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md','documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md'];require(not subprocess.check_output(['git','diff','origin/main','HEAD','--',*docs],cwd=ROOT),'current approved designs match origin/main')
    require(not subprocess.check_output(['git','diff','5224dd641976df502f3d1f278d73ec55f5ff9711','HEAD','--','src/deployment','pom.xml',POM_PATHSPEC],cwd=ROOT),'same standalone dependency/deployment contract')
    architecture={**prior,'source':SOURCE,'sourceSha256':files,'architectureEvidence':[{'path':p,'originMainSha256':hashlib.sha256(subprocess.check_output(['git','show','origin/main:'+p],cwd=ROOT)).hexdigest()}for p in docs[:2]]};architecture.pop('qualityGatePass',None)
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';labelpath=public/'PG3426-crypto-finding-disposition/manifest.json';label=json.loads(labelpath.read_bytes());test=ROOT/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodecTest.java';require(hashlib.sha256(test.read_bytes()).hexdigest()==label['testSourceSha256'],'exact immutable independent JCE fixture')
    specs=[]
    for rule,module,code,testname,method,needle,disposition,basis in SPECS:
        path=PREFIX+module+'/src/main/java/dev/codex/schubert/nk/'+code+'.java';specs.append([rule,path,'dev.codex.schubert.nk.'+testname.replace('/','.'),method,needle,disposition,basis])
    inventory=json.loads((W/'pg3706-pmd-applicability-inventory-v1/manifest.safe.json').read_bytes())['result']
    data={'source':SOURCE,'staticManifestSha256':s['serverManifestSha256'],'wholeQualificationSha256':whole['result']['qualificationManifestSha256'],'vendorRulesSha256':inventory['vendorRulesSha256'],'architecture':architecture,'architectureProofSha256':hashlib.sha256(json.dumps(architecture,sort_keys=True).encode()).hexdigest(),'specs':specs,'label':label,'labelProofSha256':hashlib.sha256(labelpath.read_bytes()).hexdigest(),'contractDesignEvidence':[{'path':p,'originMainSha256':hashlib.sha256(subprocess.check_output(['git','show','origin/main:'+p],cwd=ROOT)).hexdigest()}for p in docs]}
    os.umask(0o077);out=W/'pg3744-pmd-contract-classification-v1';out.mkdir();(out/'architecture.safe.json').write_text(json.dumps(architecture,sort_keys=True));script=out/'classify.private.py';script.write_text('\n'.join(inspect.getsource(x)for x in [require,classify_contract,server])+'\nserver('+repr(data)+')\n');dest='/home/mini/schubert-nk-pgpt/transfer/PG3744-pmd-contract-classification-v1';rc,_=run('test ! -e /home/mini/schubert-nk-pgpt/runs/PG3744-pmd-contract-classification-v1 && mkdir -m700 '+dest,timeout=30);require(rc==0,'new-only source contract index');rc,_=copy(script,dest+'/',timeout=60);require(rc==0,'exact independent scope tools');rc,text=run('python3 -B '+dest+'/classify.private.py',timeout=90);(out/'observer.private.log').write_text(text);value={'actualExit':rc,'source':SOURCE,'payloadSha256':hashlib.sha256(script.read_bytes()).hexdigest(),'formalAccepted':False}
    if rc==0:value['result']=json.loads(next(x for x in reversed(text.splitlines())if x.startswith('{')))
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return rc


if __name__=='__main__':raise SystemExit(main())
