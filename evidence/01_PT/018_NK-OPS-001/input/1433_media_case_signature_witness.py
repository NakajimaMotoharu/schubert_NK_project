"""Independent source+compiled Test descriptor witness; no class initialization or product test replay."""
from pathlib import Path
import hashlib,json,re,subprocess
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';W=R.parent/'pgpt-runs/PG379/pg26990-media186-profile-v2';TC=R.parent/'toolchain';O=B/'evidence/PG27010-case-signature-witness-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));assert not O.exists();m=load(B/'evidence/PG26990-media186-profile-v2/manifest.json');source='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/MediaBodyStreamerTest.java';klass='dev.codex.schubert.nk.web.media.MediaBodyStreamerTest';method='exactIntervalsUseBoundedWritesAndLeaveResourcesOpen';s=(R/source).read_text();assert sha(R/source)==m['inputHashes'][source];assert 'void '+method+'(@TempDir Path root)' in s and 'import java.nio.file.Path;' in s
classfile=W/'test-classes'/Path(klass.replace('.','/')+'.class');assert sha(classfile)==m['testClassHashes'][str(classfile.relative_to(W/'test-classes'))];O.mkdir();c.SLOT=O;stage=c.step('javap-test-signature',[str(TC/'jdk-25.0.4/bin/javap'),'-p','-s',str(classfile)],R);assert stage['actualExit']==0 and not stage['timedOut'];text=(O/'javap-test-signature.stdout').read_text();assert 'void '+method+'(java.nio.file.Path)' in text and 'descriptor: (Ljava/nio/file/Path;)V' in text
checks=[]
for p in m['ownTestSources']:
 text=(R/p).read_text();methods=re.findall(r'@Test\b(?:[^\n]*\n)*?\s*void (\w+)\s*\(',text)
 for name in methods:
  parameters=re.search(r'void '+re.escape(name)+r'\(([^)]*)\)',text).group(1).strip();checks.append(dict(path=p,name=name,parameters=parameters))
assert len(checks)==23 and len([x for x in checks if x['parameters']])==1
alias=dict(classname=klass,rawExpected=method+'()',sourceExpected=method+'(Path)',sourcePath=source,sourceSha256=sha(R/source),compiledTestSha256=sha(classfile),descriptor='(Ljava/nio/file/Path;)V')
def project(classname,name):
 if classname==alias['classname'] and name==alias['rawExpected']:return alias['sourceExpected']
 return name
assert project(klass,method+'()')==method+'(Path)';assert project(klass+'Foreign',method+'()')==method+'()';assert project(klass,method+'(String)')==method+'(String)';assert project(klass,method+'(Path,Path)')==method+'(Path,Path)'
v=dict(actualExit=0,source='16dbed2efca0e014ff849e833a9ddbd89f126c36',stages={'javap-test-signature':stage},alias=alias,allOwnSourceSignatureChecks=checks,zeroArgMethods=22,pathArgMethods=1,positiveChecks=1,negativeChecks=3,productTestsExecuted=0,productTestClassInitialized=False,productionOrTestChanged=False,originalRunAndExpectedCasesPreserved=True,unknownCasesAllowed=False,bug='BUG-2687',horizontal='YKT-2365',verifier=ref(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sourceSignatures23=True,positive1=True,negative3=True,productTestsExecuted=0,manifestSha256=sha(O/'manifest.json'))))
