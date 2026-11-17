"""Pure evidence/source binding verifier, not a PT pass/coverage or execution permission."""
from pathlib import Path
import datetime,hashlib,json,re,platform,subprocess
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
mp=b/'evidence/PG37794-p01810-negative-oracle-mapping-v1/manifest.json';m=ld(mp);rows=ld(mp.parent/'negative-case-correspondence.json');planned=ld(mp.parent/'planned93-negative-status.json');assert m['actualExit']==0 and len(rows)==15 and len(planned)==93
assert len({x['id'] for x in rows})==15 and all(x['newExecution'] is False and x['notNewPassOrCoverage'] for x in rows)
assert all(x['sourceReadByThisGroup'] is False and x['actualWholeBoundaryAccepted'] is False for x in planned)
assert all(sha(r/v['path'])==v['sha256'] for v in m['files'])
main={'REQUEST_DETAILS':'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/logging/RequestLogDetails.java','WEB_TRACE':'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestTrace.java','MEDIA_AUDIT':'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebMediaAudit.java'}
source_pins={}
for key,n in main.items():
    proof=m['oldWholeProofs'][key];p=r/proof['independentWholePost']['path'];assert sha(p)==proof['independentWholePost']['sha256'];post=ld(p);prep=ld(r/post['prepare']['path']);pins=prep.get('mainInputHashes',prep.get('inputHashes'));assert n in pins and sha(r/n)==pins[n]
    source_pins[key]=dict(path=n,sha256=sha(r/n),oldPost=proof['independentWholePost'],wholeCurrentSourceQualified=proof['wholeCurrentSourceQualified'])
for f in m['existingFixtureSources']:
    assert sha(r/f['path'])==f['sha256']
    text=(r/f['path']).read_text();assert all(not x in f['path'] for x in ['RootFailedStart','SnapshotKeyCloseWitness','WebStartupException','ResponseSnapshotCodec','FingerprintKeyRing','TemporaryInfrastructureException'])
for row in rows:
    key=row['family'];members=[f for f in m['existingFixtureSources'] if f['wholeProducerProof']==m['oldWholeProofs'][key]['independentWholePost']]
    assert sum(bool(re.search(r'void\s+'+row['existingTestMethod']+r'\s*\(', (r/f['path']).read_text())) for f in members)==1
    assert row['independentBasis'] and row['independentExpected'] is not None
methods={(x['family'],x['existingTestMethod']) for x in rows};assert len(methods)==12
out=b/'evidence/PG37796-p01810-negative-mapping-independent-v1';assert not out.exists();out.mkdir()
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore='a013a6d676454082de3c59bc199e87f37fefe159',gitHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),branch=subprocess.check_output(['git','branch','--show-current'],text=True).strip(),os=platform.platform(),python=platform.python_version(),command=['python3','-B','evidence/01_PT/018_NK-OPS-001/input/4822_p01810_negative_mapping_independent.py'],mapping=ref(mp),literalVectorGroups=15,distinctExistingTestMethods=12,existingFixtures=4,explicitTargetMainSourceBindings=source_pins,plannedBoundaryStatusesPreserved=93,sourceOrMethodsExecuted=False,heldSourceBinaryOrPrivateReads=0,newPTPasses=0,coverageMeasurements=0,formalUpdated=False,newAcceptance=0,effortCompletionRate=None,originalPreparationRow='WBS-P018-10.03/1',completedOriginalPricePp=.35,originalCompletedTotalPp='9.888',remainingDetailBasePp='1089.498',laterAcceptanceRowStillPending='WBS-P018-10.03/2')
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,negativeVectorGroups=15,distinctOldMethods=12,sourceTargetsExact=3,newPT=0,whole93Accepted=0))
