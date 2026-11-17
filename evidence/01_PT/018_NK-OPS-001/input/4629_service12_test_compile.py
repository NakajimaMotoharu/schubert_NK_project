"""Changed Main/whole12 is an actual compile trigger; all17 shared Test sources remain source-bound."""
from pathlib import Path
import hashlib,json,shutil,sys
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';w=r.parent/'pgpt-runs/PG379';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
rootp=b/'evidence/PG37180-service-command-four-main-compile-v1/manifest.json';root=ld(rootp);oldp=b/'evidence/PG37164-root-fixture-caller-compile-v2/manifest.json';old=ld(oldp);patchp=b/'evidence/PG37178-service-command-port-source-v1/manifest.json';patch=ld(patchp);assert root['actualExit']==old['actualExit']==patch['actualExit']==0
selected=patch['testPath'];assert sha(r/selected)==patch['testShaAfter']
assert all(n==selected or sha(r/n)==h for n,h in old['inputHashes'].items());paths=sorted(old['inputHashes']);assert len(paths)==17
for n in paths:
 assert Path(n).stem not in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest']
 assert not {word for word,at in lexical((r/n).read_text())}&{'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'}
out=b/'evidence/PG37184-service12-test-compile-v1';slot=w/'pg37184-service12-test-compile-v1';assert not out.exists() and not slot.exists();out.mkdir();slot.mkdir();component=slot/'component';component.mkdir();physical={}
for module,classes in root['physicalClassHashes'].items():
 for n,h in classes.items():
  assert Path(n).stem.split('$')[0] not in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'] and n not in physical
  p=Path(root['cwd'])/('src/schubert-nk-'+module)/'target/classes'/n;assert sha(p)==h;q=component/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);physical[n]=h
assert len(physical)==1101 and all(sha(r/n)==h for n,h in root['inputHashes'].items())
classes=slot/'test-classes';classes.mkdir();deps=old['toolDependencies'];assert all(sha(Path(n))==h for n,h in deps.items());cmd=[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-g','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',':'.join([str(component),*deps]),'-d',str(classes),*[str(r/n) for n in paths]];stage.SLOT=out;stage.ENV=dict(PATH=str(tc/'jdk-25.0.4/bin')+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8');result=stage.step('test-caller-compile',cmd,slot,timeout=120)
v=dict(actualExit=result['actualExit'],terminalAtUTC=result['endUTC'],timedOut=result['timedOut'],sourceCore=root['sourceCore'],inputHashes={n:sha(r/n) for n in paths},sourceClosureCount=17,selectedWholeExpected=12,mainInputHashes=root['inputHashes'],rootCompile=ref(rootp),sourcePatch=ref(patchp),prior17SourceProof=ref(oldp),physicalClassHashes=physical,testClassHashes={str(n.relative_to(classes)):sha(n) for n in classes.rglob('*.class')},work=str(slot),toolDependencies=deps,stage=result,productTestsExecuted=0,rootOrNativeTestsSelected=0,heldClassfileActions=0,actualRootVmDbOrServiceActions=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=result['actualExit'],sources=17,expected12=True,mainContext=1101,productTests=0)));assert result['actualExit']==0 and not result['timedOut']
