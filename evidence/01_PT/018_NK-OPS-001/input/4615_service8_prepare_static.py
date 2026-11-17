"""Current four-module class-byte context, whole memory-only Service8 Test and unselected shared helper compile/static; no PT."""
from pathlib import Path
import datetime,hashlib,json,re,shutil,sys,xml.etree.ElementTree as ET
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
rootp=b/'evidence/PG36956-backup-path-four-main-compile-v1/manifest.json';root=ld(rootp);assert root['actualExit']==0 and root['sourceCore']=='01c3b1a34ee01f4a43fcfd1eaa4cc945010675c9'
path='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/MorningServiceReadinessTest.java';helper=path.replace('MorningServiceReadinessTest.java','RootStartupContextTest.java');text=(r/path).read_text();shared=(r/helper).read_text()
assert len(re.findall(r'@Test\s+void\s+(\w+)\s*\(',text))==8
assert not any(n in text+shared for n in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest'])
assert not any(n in text for n in ['ProcessBuilder','java.lang.foreign','new Socket','HttpClient','NativeIo','RootStartupContext.create(', '@BeforeAll','@TempDir'])
assert shared.count('RootStartupContext context() {')==1 and 'return new RootStartupContext(this);' in shared and 'static {' not in shared
assert 'class LaunchFixture extends Fixture' in shared and 'static class Fixture implements RootStartupContext.Io' in shared
assert text.count('new RootStartupContextTest.LaunchFixture()')==1
sources=[path,helper]
main='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MorningServiceReadiness.java';assert sha(r/main)==root['inputHashes'][main]
assert all(sha(r/p)==h for p,h in root['inputHashes'].items());work=r.parent/'pgpt-runs/PG379/pg37148-service8-prepare-v1';out=b/'evidence/PG37148-service8-prepare-static-v1';assert not work.exists() and not out.exists();work.mkdir();out.mkdir();component=work/'component';component.mkdir();physical={}
held={'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'}
for module in ['protocol','storage','bootstrap','batch']:
 for n,h in root['physicalClassHashes'][module].items():
  assert Path(n).stem.split('$')[0] not in held and n not in physical
  old=Path(root['cwd'])/('src/schubert-nk-'+module)/'target/classes'/n;assert sha(old)==h
  p=component/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old,p);physical[n]=h
assert len(physical)==1101
classes=work/'test-classes';classes.mkdir();deps=[tc/'junit-platform-console-standalone-1.13.4.jar',tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar',tc/'m2/repository/com/github/spotbugs/spotbugs-annotations/4.10.4/spotbugs-annotations-4.10.4.jar'];classpath=':'.join(map(str,[component,*deps]));jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015';libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))];rules=r/'tools/quality/static';listing=out/'sources.txt';listing.write_text(''.join(str(r/n)+'\n' for n in sources));pins={str(p):sha(p) for p in [*deps,*libs,sg/'checkstyle-14.3.0-all.jar',tc/'google-java-format-1.36.1-all-deps.jar',rules/'pmd.xml',rules/'checkstyle.xml']};stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
commands={'format':[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(r/n) for n in sources]],'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],'test-compile':[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(classes),*[str(r/n) for n in sources]],'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+classpath,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]};stages={}
for n,c in commands.items():
 stages[n]=stage.step(n,c,work,timeout=120);assert not stages[n]['timedOut'] and stages[n]['actualExit'] in ([0,4] if n=='pmd' else [0])
raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
 tag=node.tag.rsplit('}',1)[-1]
 if tag in ['error','configerror']:errors.append(dict(node.attrib))
 if tag=='file':
  for item in node:
   if item.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**item.attrib,message=(item.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error')
assert all(sha(r/p)==h for p,h in root['inputHashes'].items()) and all(sha(component/n)==h for n,h in physical.items())
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=root['sourceCore'],rootCompile=ref(rootp),mainInputHashes=root['inputHashes'],testSourceHashes={n:sha(r/n) for n in sources},physicalClassHashes=physical,testPhysicalHashes={str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},work=str(work),classpath=classpath,toolDependencyHashes=pins,stages=stages,rawFindings=raw,processingErrors=errors,wholeTestSourceCounts={path:8},expectedTests=8,unselectedSharedTestSource=helper,unselectedRootTestCasesExecuted=0,productTestsExecuted=0,productMainRecompiled=False,mainSpotBugsCurrentProof=ref(b/'evidence/PG36958-backup-path-fresh-sibling-spotbugs-v1/manifest.json') if (b/'evidence/PG36958-backup-path-fresh-sibling-spotbugs-v1/manifest.json').exists() else None,heldClassfilesReadOrGenerated=False,actualBackendNativeRootOperations=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,mainContext=1101,wholeTests=8,raw=len(raw),productTestsExecuted=0)))
