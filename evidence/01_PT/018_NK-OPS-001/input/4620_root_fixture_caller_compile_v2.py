"""Recover full17 Test compile using original missing cross-module helper, no runtime probe."""
from pathlib import Path
import hashlib,json,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
priorp=b/'evidence/PG37160-root-fixture-caller-compile-v1/manifest.json';prior=ld(priorp);assert prior['actualExit']==1 and prior['productTestsExecuted']==0
assert all(sha(r/x['path'])==x['shaAfter'] and x['actualExit']==0 and x['allTokensAndLiteralsIdentical'] for x in prior['formatChanges'])
plan=ld(w/'pg37162-test-caller-compile-source-plan.json');assert len(plan['sources'])==17
for path in plan['sources']:
 assert Path(path).stem not in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest']
 assert not {x for x,at in lexical((r/path).read_text())}&{'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'}
p=ld(b/'evidence/PG37134-caddy20-prepare-static-v1/manifest.json');component=Path(p['work'])/'component';assert all(sha(component/n)==h for n,h in p['physicalClassHashes'].items()) and all(sha(Path(n))==h for n,h in prior['toolDependencies'].items())
out=b/'evidence/PG37164-root-fixture-caller-compile-v2';slot=w/'pg37164-root-fixture-caller-compile-v2';assert not out.exists() and not slot.exists();out.mkdir();slot.mkdir();classes=slot/'test-classes';classes.mkdir()
cmd=[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-g','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',':'.join([str(component),*prior['toolDependencies']]),'-d',str(classes),*[str(r/n) for n in plan['sources']]];stage.SLOT=out;stage.ENV=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8');result=stage.step('test-caller-compile',cmd,slot,timeout=120)
v=dict(actualExit=result['actualExit'],terminalAtUTC=result['endUTC'],timedOut=result['timedOut'],inputHashes={n:sha(r/n) for n in plan['sources']},originalFailure=ref(priorp),changedCallerSources=8,alignedFieldReferences=11,sourceClosureCount=17,wholeMainContext=1101,mainClassHashes=p['physicalClassHashes'],testClassHashes={str(n.relative_to(classes)):sha(n) for n in classes.rglob('*.class')},toolDependencies=prior['toolDependencies'],stage=result,productTestsExecuted=0,CallerMonitorProbeExecuted=False,rootOrNativeTestsSelected=0,heldClassfilesReadCompiledLoaded=False,bug='BUG3159',horizontal='YKT2628',formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=result['actualExit'],sources=17,changedCallers=8,productTests=0)));assert result['actualExit']==0 and not result['timedOut']
