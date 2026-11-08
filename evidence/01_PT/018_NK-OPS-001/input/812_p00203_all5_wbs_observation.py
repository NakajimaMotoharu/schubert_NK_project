"""Append a reference-only observation, preserving WBS acceptance and strict digest binding."""
from pathlib import Path
import datetime, hashlib, importlib.util, json, re
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG24814-p00203-all5-wbs-observation-binding-v1';assert not O.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=B/'evidence/PG24808-headercodec5-method14-trace-independent-v1/manifest.json';assert sha(proof)=='dd40ac9440700fbb1753b0f15c8c6753372fae2488b54b6c939b863be1454e87';m=json.loads(proof.read_bytes());assert m['actualExit']==0 and m['sourceArtifacts']==5 and m['officialMeasuredMethods']==14 and m['newAcceptance']==0
D=R/'documents/400_PGPT/470_PMO';paths=[D/'485_WBS網羅性・受入対応.json',D/'486_WBS現行実績.json'];key='currentP00203AllMethodReferenceTrace20261109';before=[p.read_bytes() for p in paths];old=[json.loads(b) for b in before];assert all(key not in x for x in old)
private=R.parent/'pgpt-runs/PG379/pg24814-p00203-all5-wbs-observation-before-v1';assert not private.exists();private.mkdir()
for p,b in zip(paths,before):(private/p.name).write_bytes(b)
obs=dict(status='ALL5_METHOD14_REFERENCE_LINKS_COMPLETE_ONLY_NOT_OWNER_ACCEPTED',source=m['source'],testSource=m['testSource'],owner='WBS-P002-03',ownedSourceArtifacts=5,referenceSourceArtifacts=5,remainingSourceReferences=0,methodReferences=14,existingActualCaseRefs=7,naturalZeroBranchSources=2,branchCoveragePercent=None,strictNonemptySourceFourCounterGateExit=1,proof=dict(path=str(proof.relative_to(R)),sha256=sha(proof)),perCaseProbeAttribution=None,allBranchOraclesIndividuallyVerified=False,newProductTests=0,newCoverageMeasurement=False,sourceRegistryAcceptedDelta=0,newAcceptance=0,formalUpdated=False,effortRate=None)
addition=json.dumps({key:obs},ensure_ascii=False,indent=2)[1:-1].rstrip('\n')+',';new485=('{'+addition+before[0].decode()[1:]).encode();digest=hashlib.sha256(new485).hexdigest();s=before[1].decode();matches=list(re.finditer(r'^  "inventorySha256": "([a-f0-9]{64})"',s,re.M));assert len(matches)==1;match=matches[0];assert match.group(1)==hashlib.sha256(before[0]).hexdigest();new486=('{'+addition+s[:match.start(1)][1:]+digest+s[match.end(1):]).encode()
current=[json.loads(b) for b in [new485,new486]];assert {k:v for k,v in current[0].items() if k!=key}==old[0];check={k:v for k,v in current[1].items() if k!=key};check['inventorySha256']=old[1]['inventorySha256'];assert check==old[1] and current[0][key]==current[1][key]
sp=importlib.util.spec_from_file_location('guard',B/'input/580_wbs_inventory_reference_guard.py');g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);g.validate_bytes(*before);assert g.validate_bytes(new485,new486)['bindingValid'] is True
for p,b in zip(paths,[new485,new486]):p.write_bytes(b)
checks=0
for value in [old[1]['inventorySha256'],'0'*64,False]:
 bad=dict(current[1]);bad['inventorySha256']=value
 try:g.validate_bytes(new485,json.dumps(bad).encode())
 except ValueError:checks+=1
 else:raise AssertionError('invalid binding')
try:g.validate_bytes(new485,b'{"inventorySha256":"'+digest.encode()+b'","inventorySha256":"'+digest.encode()+b'"}')
except ValueError:checks+=1
else:raise AssertionError('duplicate binding')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),command='python3 -B evidence/01_PT/018_NK-OPS-001/input/812_p00203_all5_wbs_observation.py',source=m['source'],observationKey=key,beforeHashes={str(p.relative_to(R)):hashlib.sha256(b).hexdigest() for p,b in zip(paths,before)},afterHashes={str(p.relative_to(R)):sha(p) for p in paths},inventorySha256=digest,originalWbsValuesUnchangedExceptRootInventoryBinding=True,observationsEqual=True,sourceReferenceArtifacts=5,methodReferenceCount=14,existingActualCaseRefs=7,bindingNegativeChecks=checks,guardSha256=sha(B/'input/580_wbs_inventory_reference_guard.py'),productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,artifacts=5,methods=14,bindingNegativeChecks=checks,inventorySha256=digest)))
