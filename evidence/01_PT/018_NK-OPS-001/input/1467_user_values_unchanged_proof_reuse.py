"""Reuse unchanged historical whole4 target proof without replay or old-to-new runtime relabel."""
from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG27088-user-values-unchanged-proof-reuse-v1';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists()
oldp=B/'evidence/PG23334-user-mutation-values-independent-v1/manifest.json';old=load(oldp);assert old['actualExit']==0 and old['tests']==4 and old['wholeTargetCodeCoverage100'] and old['heldFourInitializations']==0
for p,h in old['inputHashes'].items():assert sha(R/p)==h
indexp=B/'evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json';assert sha(indexp)=='db6581ac589b42bdaa6e51ac101dac365d02a8fabab7d689eb5f12de29319723';index=load(indexp)
normal=load(B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json');current=load(B/'evidence/PG27060-user-query159-independent-v1/manifest.json');assert current['actualExit']==0
bindings=[]
for name,crc in old['normalObservedCrc'].items():
 assert name in index and not any(x in name for x in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
 row=index[name];path=row['path'];assert sha(R/path)==normal['begin']['inputHashes'][path]
 if '/protocol/' in name:
  assert current['classIds'][name]==crc and current['physicalClassHashes'][name+'.class']==row['sha256']
 else:assert row['crc64']==crc and normal['normalPhysicalClassHashes']['api:'+name+'.class']==row['sha256']
 bindings.append(dict(name=name,path=path,sourceSha256=sha(R/path),physicalSha256=row['sha256'],crc64=crc))
assert len(bindings)==12
for name,h in old['physical'].items():assert index[name]['sha256']==h
assert set(old['physical'])==set(old['sourceFilePhysicalClosure']) and len(old['physical'])==3
assert all(x['missed']==0 for x in old['coverage'].values()) and old['coverage']['BRANCH']['covered']==6
def valid(xs):return xs==bindings
assert valid([dict(x) for x in bindings])
assert not valid(bindings[:-1]);bad=[dict(x) for x in bindings];bad[0]['crc64']='0'*16;assert not valid(bad)
assert not valid(bindings+[dict(name='foreign/Unknown')])
O.mkdir();v=dict(actualExit=0,currentGit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='627ba52c319d5db9e2dd1d76d303fba045b6e592',historicalRuntimeSource=old['source'],historicalWhole4Proof=ref(oldp),historicalTarget3Coverage=old['coverage'],allOriginalInputHashesUnchanged=True,all12ObservedMainSourceAndPhysicalCrcUnchanged=bindings,all3TargetSourcePhysicalClosureUnchanged=True,currentProtocolByteProof=ref(B/'evidence/PG27060-user-query159-independent-v1/manifest.json'),metadataIndex=ref(indexp),negativeControls=3,productTestsExecuted=0,newDefinitions=0,oldExecCombined=False,freshRuntimeSourceQualification=False,wholeOldBroadJarProfileNotPromoted=True,currentWhole451Accepted=False,originalP01002Or03Accepted=False,actualHeldBinaryOrBackendAccess=0,wholeApiJarHashedOrRead=False,newAcceptance=0,formalUpdated=False,effortRate=None,fee='EXISTING_SCOPE_DECISION_OVERHEAD_NO_ADDITIONAL_PRICE',verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,historicalUnchangedTarget3=True,all12Bindings=True,productTestsExecuted=0,manifest=ref(O/'manifest.json'))))
