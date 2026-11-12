"""Recover completed original compile once; metadata helper correction, no product reexecution."""
from pathlib import Path
import ast,hashlib,json,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';script=B/'input/1450_user_query159_qualifier.py'
s=script.read_text();old="assert len(canonicalTests)==2";assert s.count(old)==1
# Original producer is retained under27055 before mutation. Source body and command unaffected.
script.write_text(s.replace(old,"assert len(canonicalTests)==3"))
sys.argv=['profile','metadata-finalize'];ns={};exec(compile(s.split("if phase=='prepare':")[0],str(script),'exec'),ns)
W=ns['W'];O=ns['O'];sha=ns['sha'];load=ns['load'];ref=ns['ref'];ct=ns['ct']
assert not (O/'manifest.json').exists()
stage=load(O/'test-compile-exit.safe.json');assert stage['actualExit']==0 and not stage['timedOut']
physical={str(p.relative_to(W/'component')):sha(p) for p in (W/'component').rglob('*.class')};assert len(physical)==192
canonicalTests={str(p.relative_to(ct)):sha(p) for p in ct.rglob('*.class')}
oldproof=B/'evidence/PG26640-canonical-test-compile-v2/manifest.json';proof=load(oldproof)
assert sha(oldproof)=='7addbd44296bd9055dbbcc9a1c82fd4e9f94949962cb2f7d4a7d1b130f0b1720'
expectedNames={'dev/codex/schubert/nk/api/idempotency/'+x+'.class' for x in ['OperationFingerprintTest','SecretBufferTest','SecretBufferTest$Inspectable']}
assert set(canonicalTests)==expectedNames
assert canonicalTests==proof['testClassHashes']
newTestHashes={str(p.relative_to(W/'test-classes')):sha(p) for p in (W/'test-classes').rglob('*.class')};assert len(newTestHashes)==6
pt=ns['pt'];assert len(pt['classHashes'])==47
def valid(value):return value==canonicalTests
assert valid(dict(canonicalTests))
bad=dict(canonicalTests);bad.pop(next(iter(bad)));assert not valid(bad)
bad=dict(canonicalTests);bad['extra.class']='0'*64;assert not valid(bad)
bad=dict(canonicalTests);bad[next(iter(bad))]='0'*64;assert not valid(bad)
v=dict(actualExit=0,inputHashes=ns['inputs'],dependencies=ns['deps'],apiMainSources=ns['paths'],apiTestSources=ns['tests']+[ns['authTest']],apiExactReadClassEntries=ns['names'],apiWholeJarHashedOrOtherEntryPayloadRead=False,physicalClassHashes=physical,protoMain=ref(ns['pp']),protoTest=ref(ns['tp']),normalMain=ref(ns['np']),canonicalProof=ref(ns['cp']),authorizationProof=ref(ns['ap']),canonicalTestClassHashes=canonicalTests,testClassHashes=newTestHashes,selectedClasses=sorted({x['classname'] for x in ns['expected']}),expectedCases=ns['expected'],expectedTests=159,stages={'test-compile':stage},MainRebuilt=False,productTestsExecuted=0,actualFourClassBinaryAccess=False,repositoryExceptionalBranchesNotAccepted=True,helperMetadataCorrection=dict(bug='BUG-2690',horizontal='YKT-2367',originalCompileNotReexecuted=True,canonicalPhysical3=True,protocolPhysical47=True,newPhysical6=True,negativeControls3=True,oldCompilerProof=ref(oldproof)),finalizer=ref(Path(__file__).resolve()))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,expectedTests=159,physical=192,canonicalTests=3,newTestsPhysical=6,compileReexecuted=False,manifest=ref(O/'manifest.json'))))
