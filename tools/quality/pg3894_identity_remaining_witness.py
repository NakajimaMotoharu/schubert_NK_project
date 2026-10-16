"""Explicitly join four non-conventional owning test classes to existing qualified XML."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
from lan_server import run
from pg3798_hygiene_current_observer import SOURCE

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
CASES=[
 ('PMD-7fff-0325','api','api/messaging/outbound/OutboxDispatcherTest','idem010r02SameProviderFailureOnSessionModeAndCloseKeepsOriginalCause'),
 ('PMD-7fff-0330','api','api/messaging/outbound/OutboxDispatcherTest','idem010r01SameProviderFailureOnStageAndRollbackKeepsOriginalCause'),
 ('PMD-7fff-1786','web','web/session/LogoutControllerTest','rerun007eFatalWireAndSecondaryInvalidationPreserveOriginalIdentity'),
 ('PMD-7fff-1789','web','web/session/LogoutControllerTest','rerun007gClearFailureAlwaysClearsSecurityAndPreservesFatal')]


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed witness reader')
    public=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional';prior=public/'PG3868-identity-assessment-v1';rows=json.loads((prior/'all-65-identity-findings.json').read_bytes());missing={r['id']:r for r in rows if r['disposition']!='UNCLASSIFIED'and not r.get('owningTestIds')}
    if set(missing)!={c[0]for c in CASES}:raise ValueError('exact four unresolved owning-class mappings')
    q=json.loads((W/'pg3738-hygiene-whole-qualified-v1/manifest.safe.json').read_bytes());expected=q['result']['qualificationManifestSha256'];cases=[]
    for finding,module,test,method in CASES:
        path='src/schubert-nk-'+module+'/src/test/java/dev/codex/schubert/nk/'+test+'.java'
        text=(ROOT/path).read_text()
        if 'void '+method+'('not in text or 'assertSame('not in text:raise ValueError('manually reviewed independent identity witness required')
        cases.append({'findingId':finding,'module':module,'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),'class':'dev.codex.schubert.nk.'+test.replace('/','.'),'method':method,'productionPath':missing[finding]['path'],'productionSha256':missing[finding]['sourceSha256']})
    code="""import hashlib,json,xml.etree.ElementTree as E
from pathlib import Path
base=Path('/home/mini/schubert-nk-pgpt');p=base/'runs/PG3738-hygiene-whole-qualified-v1/manifest.safe.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)==EXPECTED;q=json.loads(p.read_bytes());assert q['actualExit']==0 and q['productionSource']==SOURCE and q['tests']==3714
result=[]
for v in CASES:
 test=base/'source-full-PG3734'/v['path'];source=base/'source-full-PG3734'/v['productionPath'];assert sha(test)==v['sha256'] and sha(source)==v['productionSha256']
 xml=base/'runs/PG3734-six-v1'/v['module']/'surefire-reports'/('TEST-'+v['class']+'.xml');digest=sha(xml);assert digest==q['modules'][v['module']]['xmlHashes'][xml.name]
 tree=E.parse(xml).getroot();items=[c for c in tree.findall('testcase')if c.get('name')==v['method']];assert len(items)==1 and not any(n.tag in {'failure','error','skipped','flakyFailure','flakyError','rerunFailure','rerunError'}for n in items[0].iter())
 result.append({**v,'qualifiedXmlSha256':digest,'testId':v['class']+'#'+v['method'],'originalCaseSuccessful':True})
print(json.dumps({'actualExit':0,'source':SOURCE,'newTestExecutions':0,'newTechnicalDispositions':0,'fourExplicitWitnesses':result,'currentWholeQualificationSha256':EXPECTED,'formalAccepted':False,'F03Accepted':False}))
"""
    payload='EXPECTED='+repr(expected)+'\nSOURCE='+repr(SOURCE)+'\nCASES='+repr(cases)+'\n'+code
    os.umask(0o077);out=W/'pg3894-identity-explicit-witness-v1';out.mkdir();(out/'payload.private.py').write_text(payload)
    status,output=run('python3 -B -c '+shlex.quote(payload),timeout=30);(out/'observer.private.log').write_text(output)
    if status:raise ValueError('original qualified XML/source witness could not be joined')
    value=json.loads(next(l for l in output.splitlines()if l.startswith('{')))
    if value['actualExit']!=0 or len(value['fourExplicitWitnesses'])!=4:raise ValueError('exact four actual witnesses required')
    target=public/'PG3894-identity-explicit-witness-v1';target.mkdir()
    raw=(json.dumps(value,sort_keys=True)+'\n').encode();(target/'four-explicit-witnesses.json').write_bytes(raw)
    manifest={'actualExit':0,'source':SOURCE,'operatorSource':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'priorManifestSha256':hashlib.sha256((prior/'manifest.json').read_bytes()).hexdigest(),'files':{'four-explicit-witnesses.json':hashlib.sha256(raw).hexdigest()},'payloadSha256':hashlib.sha256(payload.encode()).hexdigest(),'assessedFindingsWithWitnessesBefore':26,'assessedFindingsWithWitnessesNow':30,'rawFindings':1840,'technicalDispositions':278,'unclassified':1562,'newTestExecutions':0,'newTechnicalDispositions':0,'vmActions':0,'F03Accepted':False,'formalAccepted':False}
    raw=(json.dumps(manifest,sort_keys=True)+'\n').encode();(target/'manifest.json').write_bytes(raw);(out/'manifest.safe.json').write_bytes(raw)
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(raw).hexdigest(),'fourActualQualifiedWitnesses':True,'assessedFindingsWithWitnesses':30,'newTests':0,'F03Accepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
