import json,hashlib,zipfile,collections,datetime
from pathlib import Path
import classfile_code_metadata as code
from g07_host_class_provenance_inputs import write
import os
root=Path.cwd();b=root/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
matrix=json.loads((b/'503_Source証拠再利用判定.json').read_bytes())
normalPath=root.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json'
assert hashlib.sha256(normalPath.read_bytes()).hexdigest()=='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
normal=json.loads(normalPath.read_bytes());assert normal['source']==matrix['source'] and normal['actualExit']==normal['testsExecuted']==0
bySource=collections.defaultdict(list);errors=[];jarPins={}
for role,jarInfo in normal['jars'].items():
 jarPath=Path(jarInfo['path']);assert hashlib.sha256(jarPath.read_bytes()).hexdigest()==jarInfo['sha256'];jarPins[role]=jarInfo
 with zipfile.ZipFile(jarPath) as jar:
  for entry in jar.namelist():
   if not entry.endswith('.class') or not entry.startswith('dev/codex/schubert/'):continue
   raw=jar.read(entry)
   try:parsed=code.decode(raw,entry)
   except ValueError as error:
    errors.append(dict(module=role,entry=entry,error=str(error)));continue
   package=entry.rpartition('/')[0]
   path='src/schubert-nk-'+role+'/src/main/java/'+package+'/'+parsed['sourceFile']
   bySource[path].append(dict(name=entry[:-6],sha256=hashlib.sha256(raw).hexdigest(),flags=parsed['flags'],methods=parsed['methods'],sourceFile=parsed['sourceFile']))
rows=[]
for r in matrix['rows']:
 if r['evidenceStatus']!='NOT_IN_CURRENT_MEASUREMENT_REGISTRY':continue
 path=r['path'];assert 'RootFailedStartRecoveryTest' not in path and 'RootFailedStartPairRecoveryTest' not in path
 physical=bySource.get(path,[]);sourceMatches=normal['begin']['inputHashes'].get(path)==r['sha256']
 hasCode=any(m['hasCode'] for c in physical for m in c['methods'])
 native=any(m['flags']&0x0100 for c in physical for m in c['methods'])
 if not physical or not sourceMatches:decision='SEPARATE_BUILD_OR_SOURCE_BINDING_RECONCILIATION_REQUIRED'
 elif not hasCode and not native:decision='WHOLE_PHYSICAL_SOURCE_NO_CODE_STATIC_COVERAGE_NONAPPLICABILITY_ONLY'
 elif native:decision='CODE_OR_NATIVE_CONTRACT_CURRENT_PROOF_REQUIRED'
 else:decision='EXECUTABLE_BODY_CURRENT_SOURCE_PROOF_OR_REUSE_RECONCILIATION_REQUIRED'
 rows.append(dict(path=path,owner=r['owner'],module=r['module'],sourceSha256=r['sha256'],normalSourceHashMatches=sourceMatches,physical=physical,physicalCount=len(physical),hasCode=hasCode if physical else None,hasNative=native if physical else None,decision=decision,necessaryDynamicExecutions=None,newCoverage=0,newAcceptance=False,businessContractClosed=False))
assert len(rows)==282
counts=dict(collections.Counter(r['decision'] for r in rows))
value=dict(actualExit=0,source=matrix['source'],atJST=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),scope='STATIC_BINARY_METADATA_FOR_ALL282_UNREGISTERED_SOURCE_UNITS_NOT_RUNTIME_QUALIFICATION',normalCompileSha256='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3',jars=jarPins,rows=rows,counts=counts,parserErrors=errors,wholeProductionClassesLoadedOrExecuted=0,productTests=0,oldExecTransferred=False,registryUpdated=False,coverageExclusionsAdded=False,allSourceOracleMeaningReviewed=False,formalUpdated=False,heldToolPathsAccessed=False,heldRootFailedTestSourceFilesAccessed=False,mayFinishTurn=False)
out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18520-unregistered282-binary-static-v2'
assert not out.exists()
out.mkdir()
write(out/'manifest.json',value)
with (out/'manifest.json').open('rb') as persisted:
 os.fsync(persisted.fileno())
summary=dict(actualExit=0,source=value['source'],rows=len(rows),counts=counts,parserErrors=len(errors),physicalCount=sum(r['physicalCount'] for r in rows),manifestSha256=hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),manifestBytes=(out/'manifest.json').stat().st_size,productTests=0,registryUpdated=False)
payload=json.dumps(summary,ensure_ascii=False)
assert len(payload.encode())<=4096
print(payload)
