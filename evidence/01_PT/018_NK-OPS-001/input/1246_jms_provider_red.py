"""Two new independent TDD probes only, against the preserved original Main2 boundary."""
from pathlib import Path
import hashlib,json,sys,zipfile,xml.etree.ElementTree as ET
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();load=lambda p:json.loads(Path(p).read_bytes());write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
out=B/'evidence/PG26476-jms-provider-original-red-v1';work=RUNS/'pg26476-jms-provider-original-red-v1';assert not out.exists() and not work.exists();out.mkdir();work.mkdir();(work/'classes').mkdir();c.SLOT=out
before=load(B/'evidence/PG26470-jms-provider-classification-before-v1/manifest.json');tests=before['wholeSafeCandidateTests'];guards=list(before['beforeSnapshots'])[:2];dtos=[guards[0].replace('JmsReplyDecoder','ValidatedReply'),guards[1].replace('JmsMessageGuard','GuardedJmsMessage')];main=guards+dtos
for p in guards:assert sha(R/p)==before['beforeSnapshots'][p]['sha256']
proto=load(B/'evidence/PG26278-protocol-unicode-main-compile-v1/manifest.json');jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256']
vendor=[TC/'m2/repository'/p for p in ['jakarta/jms/jakarta.jms-api/3.1.0/jakarta.jms-api-3.1.0.jar','org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar','org/apache/artemis/artemis-jakarta-client/2.56.0/artemis-jakarta-client-2.56.0.jar','org/apache/artemis/artemis-core-client/2.56.0/artemis-core-client-2.56.0.jar','org/apache/artemis/artemis-commons/2.56.0/artemis-commons-2.56.0.jar','io/netty/netty-common/4.1.137.Final/netty-common-4.1.137.Final.jar','io/netty/netty-buffer/4.1.137.Final/netty-buffer-4.1.137.Final.jar','org/slf4j/slf4j-api/2.0.18/slf4j-api-2.0.18.jar','org/jctools/jctools-core/4.0.7/jctools-core-4.0.7.jar']]
console=TC/'junit-platform-console-standalone-1.13.4.jar';held=['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']
for p in vendor+[jar,console]:
 with zipfile.ZipFile(p) as z:assert not any(any(h in n for h in held) for n in z.namelist())
cp=':'.join(map(str,[jar,console,*vendor]));inputs={p:sha(R/p) for p in main+tests};deps={str(p):sha(p) for p in [jar,console,*vendor]};jdk=TC/'jdk-25.0.4/bin'
write(out/'begin.json',dict(productionMain='8b2c6b8d4e76ecfb82eed729d6e3d548b87c0004',inputHashes=inputs,dependencies=deps,plannedCases=2,plannedMatrixCellsPerCase=64,noOriginal14Replay=True,actualBrokerOrHeldOperations=False))
compile=c.step('compile',[str(jdk/'javac'),'-g','-proc:none','-implicit:none','--release','25','-encoding','UTF-8','-Xlint:all','-Werror','-cp',cp,'-d',str(work/'classes'),*main,*tests],R);assert compile['actualExit']==0
classes=['dev.codex.schubert.nk.web.messaging.JmsReplyDecoderTest','dev.codex.schubert.nk.api.messaging.guard.JmsMessageGuardTest'];method='providerFailuresRetainExactIdentityAndEarlierValidationStopsLaterReads'
cmd=[str(jdk/'java'),'-Djunit.jupiter.extensions.autodetection.enabled=false','-Djunit.jupiter.execution.parallel.enabled=false','-Xlog:class+init=info:file='+str(work/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',str(work/'classes')+':'+':'.join(map(str,[jar,*vendor])),*[x for cl in classes for x in ['--select-method',cl+'#'+method]],'--reports-dir',str(work/'xml'),'--details','summary','--fail-if-no-tests']
terminal=c.step('unit',cmd,R,timeout=60);cases=[]
for p in (work/'xml').glob('TEST-*.xml'):
 target=out/p.name;target.write_bytes(p.read_bytes())
 for t in ET.parse(p).findall('testcase'):
  f=t.find('failure');cases.append(dict(classname=t.get('classname'),name=t.get('name'),failed=f is not None,error=t.find('error') is not None,skipped=t.find('skipped') is not None,failureMessage=None if f is None else f.get('message')))
assert terminal['actualExit']==1 and len(cases)==2 and all(t['failed'] and not t['error'] and not t['skipped'] for t in cases)
log=(work/'class-init.log').read_text();assert not any(h in log for h in held);assert 'EmbeddedActiveMQ' not in log and 'ActiveMQConnectionFactory' not in log
v=dict(actualExit=0,unitActualExit=1,expectation='TWO_GENUINE_EXPECTED_RED_FAILURES_PROVIDER_IAE_WRAPPED',compile=compile,terminal=terminal,source='8b2c6b8d4e76ecfb82eed729d6e3d548b87c0004',inputHashes=inputs,dependencies=deps,cases=cases,tests=2,failures=2,successes=0,eachCaseStoppedAtFirstMetadataIAE=True,remainingMatrixCellsNotClaimed=True,noOriginal14Replay=True,heldClassInitialization=0,actualBrokerOrHeldOperations=False,formalUpdated=False);write(out/'manifest.json',v);print(json.dumps(dict(actualExit=0,unitExit=1,tests=2,failures=2,heldClassInitialization=0)))
