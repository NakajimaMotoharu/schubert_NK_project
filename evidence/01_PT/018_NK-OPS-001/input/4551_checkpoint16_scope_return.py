"""Return actual catalog/ordinary point quality, explicit native/compiler gaps, no parent acceptance."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG36996-checkpoint16-independent-post-v1/manifest.json';p=load(pp)
assert p['actualExit']==0 and p['tests']==16 and not p['targetRawFour100']
assert all(x['result']=='PASS' for x in p['caseResults']) and not p['forbiddenNativeInitializations']
prepare=load(b/'evidence/PG36990-checkpoint16-prepare-static-v1/manifest.json')
root=load(b/'evidence/PG36956-backup-path-four-main-compile-v1/manifest.json')
sb=load(b/'evidence/PG36958-backup-path-fresh-sibling-spotbugs-v1/manifest.json')
assert sb['sourceCore']==p['sourceCore']==root['sourceCore']
path='src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint.java'
raw=load(b/'evidence/PG36960-current287-root-pmd-v1/raw-findings.json')
sites=[x for x in raw if x['path']==path];assert len(sites)==1 and sites[0]['rule']=='AvoidSynchronizedStatement'
assert sites[0]['beginline']=='117' and (r/path).read_text().splitlines()[116].strip()=='synchronized (lock) {'
assert 'private final Object lock = new Object();' in (r/path).read_text()
admission=dict(raw=sites[0],sourceSha256=sha(r/path),disposition='NOT_APPLICABLE',
    reason='SS354 SSC193: private unexposed monitor atomically consumes each point attempt, checks the same profile/version/session and performs the one export. No external monitor, wait/notify or container synchronization protocol. Original32-task fixture proves exactly one winner/data/export in this current16 run. PMD recommends ReentrantLock but this existing direct-Java private monitor is intentional; no runtime performance or broader native completion is inferred.')
base='dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint$PublicAgent'
methods=[x for x in p['methods'] if x['className']==base and (x['name'] in ['string','executionDataWithoutReset'] or x['name']=='<init>' and '$Classes;' in x['descriptor'])]
assert len(methods)==3 and all(v['missed']==0 for x in methods for v in x['counters'].values())
targets={n:h for n,h in prepare['physicalClassHashes'].items() if n.startswith('dev/codex/schubert/nk/bootstrap/FixedNativeCoverageCheckpoint')}
assert len(targets)==8
out=b/'evidence/PG36998-checkpoint16-scope-return-v1';assert not out.exists();out.mkdir()
name='dev.codex.schubert.nk.bootstrap.FixedNativeCoverageCheckpoint'
command=[str(r.parent/'toolchain/jdk-25.0.4/bin/javap'),'-p','-c','-classpath',str(Path(prepare['work'])/'component'),name]
result=subprocess.run(command,capture_output=True,timeout=30);assert result.returncode==0 and not result.stderr
(out/'checkpoint-bytecode.txt').open('xb').write(result.stdout)
text=result.stdout.decode();assert 'java/lang/MatchException' in text and 'tableswitch' in text
oldp=b/'evidence/provisional/PG15278-profile-terminal-fourteen-post-v1/manifest.json';old=load(oldp)
assert old['actualExit']==0 and old['tests']==14
assert all(root['physicalClassHashes']['bootstrap'].get(n+'.class')==h for n,h in old['physicalClasses'].items())
assert all(sha(r/path)==x['sha256'] for path,x in old['owners'].items())
summary=dict(actualExit=0,source=p['sourceCore'],sourceCore=p['sourceCore'],actualUnitSource=p['source'],run=p['run'],
    terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),tests=16,success=16,failed=0,errors=0,skipped=0,notRun=0,
    post=ref(pp),mainRootCompile=ref(b/'evidence/PG36956-backup-path-four-main-compile-v1/manifest.json'),
    fullMainSpotbugs=ref(b/'evidence/PG36958-backup-path-fresh-sibling-spotbugs-v1/manifest.json'),
    mainPmdSite=admission,testStaticAdmission=ref(b/'evidence/PG36992-checkpoint16-static-admission-v1/manifest.json'),
    original12OracleSemanticsInverse=ref(b/'evidence/PG36974-checkpoint-original12-style-before-v1/equivalence.json'),
    qualifiedChangedFatalCatalogs=methods,changedCatalogRawAllMiss0=True,
    targetSourcePhysical=8,trueNoCodePhysical=5,all280HelperCountersRetained=True,
    targetRaw=p['targetRawCounters'],targetRawFour100=False,manualExclusions=[],oldExecCombined=False,
    remainingNative=dict(methods=['PublicAgent default noarg normal-constructor','PublicAgent.lambda$new$1','Checkpoint.lambda$open$0'],branch='open active profile branch',status='HOLD_NOT_RUN_NOT_PASS'),
    remainingCompilerBranch=dict(method='capture',reason='javac exhaustive enum tableswitch has MatchException default',actualRawMissed=1,status='OPEN_REQUIRES_PG_OR_APPLICABLE_EVIDENCE_NOT_EXCLUDED'),
    ordinaryClosingAndPointValueOfNowCovered=True,
    bytecodeMeasurement=dict(command=command,actualExit=0,outputSha256=sha(out/'checkpoint-bytecode.txt'),productInitialization=0),
    original14ExactFivePhysicalAndThreeTestSource=True,original14Proof=ref(oldp),original14Reexecuted=0,
    original14RuntimeHelperChangedNeedsExplicitBinding=True,original14NotAddedToCurrent16=True,
    bug2803='THREE_CATALOGS_LOCALLY_RETESTED',bug2804='ACTUAL_NATIVE_FILE_HOLD_UNRESOLVED',
    bugs3141to3143='CORRECTED_AND_RETESTED',bug3144='NORMAL_CLOSING_PARTIAL_FIXED_COMPILER_NATIVE_REMAIN_OPEN',
    allNineChildCriteriaAccepted=False,endingDependencies=['WBS-F02','WBS-F03'],
    newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortCompletionRate=None)
(out/'manifest.json').open('x').write(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=16,catalogsRawAllHit=3,ordinaryClosingCovered=True,remainingMethods=3,remainingBranches=2,old14Replay=0,newAcceptance=0)))
