"""Publish true whole/signed candidate/technical dispositions; no runtime authority or old-native credit."""
import hashlib
import json
from pathlib import Path
import shlex
from lan_server import run

ROOT=Path(__file__).resolve().parents[2];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    qp=W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json';q=json.loads(qp.read_bytes());f=q['result'];signedpath=W/'pg3748-candidate-build-v1.safe.json';signed=json.loads(signedpath.read_bytes());triage=json.loads((W/'pg3744-pmd-contract-classification-v1/manifest.safe.json').read_bytes());t=triage['result'];assert q['actualExit']==signed['actualExit']==triage['actualExit']==0 and f['productionSource']==signed['candidateSource']==t['productionCandidateSource']=='7fffab57a567914956b66452e5e54388642efdec';assert f['tests']==signed['tests']==3714 and f['suites']==545 and f['mainClasses']==1643 and len(f['changedClasses'])==signed['changedClasses']==524
    assert signed['hostGateSha256']==sha(qp)and signed['signatureVerified']and signed['candidateNotDeployed']and t['rawFindings']==1840 and t['technicalDispositions']==248 and t['unclassified']==1592 and not t['F03Accepted']
    code='''from pathlib import Path
import json,hashlib
b=Path('/home/mini/schubert-nk-pgpt/runs');p=b/'PG3744-pmd-contract-classification-v1/dispositions.safe.json';assert hashlib.sha256(p.read_bytes()).hexdigest()==EXPECTED
v=json.loads(p.read_bytes());w=b/'PG3734-six-v1/manifest.safe.json';raw=w.read_bytes();assert hashlib.sha256(raw).hexdigest()==WHOLE
actual=json.loads(raw);print(json.dumps({'classified':[r for r in v if r['disposition']!='UNCLASSIFIED'],'wholeOriginal':{k:actual[k]for k in ['run','actualExit','mavenExit','startUTC','endUTC','elapsedSeconds','sourceSnapshotHead','productionSource','sourceInputsUnchanged','logSha256']}}))
'''
    rc,text=run('python3 -c '+shlex.quote('EXPECTED='+repr(t['dispositionSha256'])+'\nWHOLE='+repr(f['serverManifestSha256'])+'\n'+code),timeout=30);assert rc==0;actual=json.loads(next(x for x in text.splitlines()if x.startswith('{')));assert len(actual['classified'])==248 and actual['wholeOriginal']['actualExit']==actual['wholeOriginal']['mavenExit']==0
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3750-hygiene-whole-signed-v1';out.mkdir();values={'all-six-qualified-results.json':f['modules'],'all-1643-physical-main-sha256.json':f['allPhysicalMainSha256'],'all-524-physical-changes.json':f['changedClasses'],'host-only-counters.json':f['coverage'],'classified-248-findings.json':actual['classified'],'host-signature-receipt.json':signed,'technical-triage.json':t}
    for name,v in values.items():(out/name).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    value={'actualExit':0,'programId':'NK-OPS-001/common K01/F03','testIds':['PT-HYGIENE-WHOLE-3734','PT-HYGIENE-QUAL-3738','PT-HYGIENE-SIGN-3748','PT-F03-CONTRACT-3744'],'source':f['productionSource'],'snapshot':f['sourceSnapshot'],'branch':'dev-foundation','os':'Linux aru dedicated PGPT host','jdk':'25.0.4','maven':'3.9.12 offline, worker1','commandRef':'tools/quality/pg3734_hygiene_full_six.py emitted immutable original Maven argv in PG3734 begin manifest; see source archive/snapshot','wholeOriginal':actual['wholeOriginal'],'all3712OriginalCaseIdentitiesRetained':True,'actualNewCases':f['newCases'],'tests':3714,'suites':545,'mainClasses':1643,'jacocoAnalyzedClasses':1609,'originalSameUnreportedPhysicalClasses':34,'noNewExclusion':True,'uniqueMainSourceFilesChanged':260,'changedPhysicalMainClasses':524,'FESFlakyNotRun':0,'staticSixModules':0,'hostOnlyMissed':{k:sum(v[k]['missed']for v in f['coverage'].values())for k in ['LINE','METHOD','CLASS','BRANCH']},'candidateRelease':signed['release'],'candidateBomSha256':signed['manifestSha256'],'candidateSignatureSha256':signed['signatureSha256'],'artifacts':187,'schema':'028','sql':28,'history':29,'hostSignatureVerified':True,'candidateDeployed':False,'nativePending':True,'oldSourceNativeImported':False,'F03':{'rawPMD':1840,'technicalDispositions':248,'unclassified':1592,'applicableViolationCount':None,'checkstyleFindings':0,'accepted':False,'suppressionAdded':False,'ruleChanged':False},'independentQualificationManifestSha256':f['qualificationManifestSha256'],'independentQualificationPayloadSha256':q['payloadSha256'],'hostSignedReceiptSha256':sha(signedpath),'technicalTriageManifestSha256':t['serverManifestSha256'],'formalRun':'PT-WEB-20260925-24','formalTests':1964,'formalScopes':53,'formalUpdated':False,'individualAccepted':17,'individualTotal':190,'effortCompletionRate':None,'qa051Final':'HELD','globalCoverage100':False,'pgptAllComplete':False,'vmActions':0,'files':{n:sha(out/n)for n in values}}
    (out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+'\n');print(json.dumps({'actualExit':0,'publicFiles':len(values)+1,'source':f['productionSource'],'tests':3714,'suites':545,'mainClasses':1643,'bom':signed['manifestSha256'],'nativePending':True,'rawPMD':1840,'technicalDispositions':248,'manifestSha256':sha(out/'manifest.json')}));return 0


if __name__=='__main__':raise SystemExit(main())
