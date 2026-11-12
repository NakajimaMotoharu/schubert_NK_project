"""Owned isolated JDK whole10 reproduction, before any Main change; no API jar or held class."""
from pathlib import Path
import hashlib,json,re,sys,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';W=R.parent/'pgpt-runs/PG379/pg26624-canonical-scalar-red-v1';O=B/'evidence/PG26624-canonical-scalar-red-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert not W.exists() and not O.exists();before=load(B/'evidence/PG26620-canonical-scalar-before-v1/manifest.json');assert all(sha(R/p)==h for p,h in before['paths'].items());prefix='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/';main=list(before['paths'])+[prefix+'package-info.java'];tests=[prefix.replace('/main/','/test/')+n+'.java' for n in ['OperationFingerprintTest','SecretBufferTest']];classes=['dev.codex.schubert.nk.api.idempotency.'+n for n in ['OperationFingerprintTest','SecretBufferTest']]
for p in main+tests:assert not any(n in (R/p).read_text() for n in ['FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException','ProcessBuilder','DriverManager','java.nio.file','java.net.'])
W.mkdir();O.mkdir();(W/'classes').mkdir();c.SLOT=O;jdk=TC/'jdk-25.0.4/bin';deps=[TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',TC/'junit-platform-console-standalone-1.13.4.jar'];inputs={p:sha(R/p) for p in main+tests};wr(O/'begin.json',dict(source=before['source'],testInputHashes=inputs,dependencies={str(p):sha(p) for p in deps},expectedWholeTests=10,actualProviderKeysDbBrokerAndHeldClassAccess=False));stages={}
stages['compile']=c.step('compile',[str(jdk/'javac'),'--release','25','-g','-Xlint:all','-Werror','-cp',':'.join(map(str,deps)),'-d',str(W/'classes'),*[str(R/p) for p in main+tests]],R);assert stages['compile']['actualExit']==0
stages['unit']=c.step('unit',[str(jdk/'java'),'-Djunit.jupiter.execution.parallel.enabled=false','-jar',str(deps[1]),'execute','--disable-banner','--class-path',str(W/'classes')+':'+str(deps[0]),*[v for cl in classes for v in ['--select-class',cl]],'--reports-dir',str(O/'xml'),'--fail-if-no-tests','--details','summary'],R,timeout=120)
cases=[];messages=[]
for p in (O/'xml').glob('TEST-*.xml'):
 for t in ET.parse(p).findall('testcase'):
  cases.append(dict(classname=t.get('classname'),name=t.get('name'),failure=t.find('failure') is not None,error=t.find('error') is not None,skipped=t.find('skipped') is not None))
  for f in t.findall('failure'):messages.append(f.get('message',''))
assert len(cases)==10 and sum(t['failure'] for t in cases)==1 and sum(t['error'] or t['skipped'] for t in cases)==0 and stages['unit']['actualExit']==1
assert len(messages)==1 and 'Multiple Failures (24 failures)' in messages[0]
assert all(sha(R/p)==h for p,h in inputs.items())
v=dict(actualExit=0,productActualExit=1,tests=10,success=9,failures=1,errors=0,skipped=0,independentMalformedBoundariesExecutedAndFailed=24,actualMainSource=before['source'],inputHashes=inputs,stages=stages,cases=cases,newMainChanged=False,interpretation='REPRODUCED_IMPLEMENTED_CANONICAL_UTF16_SUBSTITUTION_BUG_NOT_TDD_UNIMPLEMENTED',formalUpdated=False,verifierSha256=sha(Path(__file__)));wr(O/'manifest.json',v);print(json.dumps({k:v[k] for k in ['actualExit','productActualExit','tests','success','failures','independentMalformedBoundariesExecutedAndFailed']}))
