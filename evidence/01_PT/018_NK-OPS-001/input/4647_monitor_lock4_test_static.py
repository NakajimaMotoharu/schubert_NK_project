"""Fresh Main context, original whole ordinary source closure and four changed-source static checks."""
from pathlib import Path
import hashlib,json,re,shutil,sys,xml.etree.ElementTree as ET
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
cp=b/'evidence/PG37216-monitor-lock4-four-main-compile-v1/manifest.json';c=ld(cp);fp=b/'evidence/PG37214-monitor-lock4-format-v2/manifest.json';f=ld(fp);assert c['actualExit']==f['actualExit']==0
testdir=r/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/monitoring'
names=['MonitoringPollerTest','MonitoringObservationClockTest','BatchMetricRecorderTest','RestartHealthMonitorTest','DlqHealthMonitorTest','IntegrityHealthMonitorTest','AsyncQueueMonitorTest','TransferHealthMonitorTest','JvmHeapHealthMonitorTest','BackupHealthMonitorTest','WebLogBacklogMonitorTest','ExpiryBacklogMonitorTest','FilesystemHealthObservationTest','MonitoringLockContractTest']
selected={str((testdir/(n+'.java')).relative_to(r)):len(re.findall(r'@Test\s+void',(testdir/(n+'.java')).read_text())) for n in names};assert sum(selected.values())==113
index={p.stem:p for p in testdir.glob('*.java')};closure=set(names)
while True:
 extended=closure|{n for name in closure for n in re.findall(r'\b\w+Test\b',index[name].read_text()) if n in index}
 if extended==closure:break
 closure=extended
assert len(closure)==16
paths=sorted(str(index[n].relative_to(r)) for n in closure)
fenced={'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest'}
assert all(not ({t for t,_ in lexical((r/n).read_text())}&fenced) for n in paths)
out=b/'evidence/PG37220-monitor-lock4-test-static-v1';work=r.parent/'pgpt-runs/PG379/pg37220-monitor-lock4-test-static-v1';assert not out.exists() and not work.exists();out.mkdir();work.mkdir();component=work/'component';component.mkdir();physical={}
for module,classes in c['physicalClassHashes'].items():
 for n,h in classes.items():
  assert n not in physical and Path(n).stem.split('$')[0] not in fenced
  p=Path(c['cwd'])/('src/schubert-nk-'+module)/'target/classes'/n;assert sha(p)==h
  target=component/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target);physical[n]=h
assert len(physical)==1101 and all(sha(r/n)==h for n,h in c['inputHashes'].items())
old=ld(b/'evidence/PG37164-root-fixture-caller-compile-v2/manifest.json');deps=dict(old['toolDependencies'])
sdk=ld(b/'evidence/PG36846-ssc449-boot-batch-static-v1/manifest.json')['actualCompileClasspaths']['batch']['entries']
for n in sdk:
 if '/dev/codex/schubert/' not in n:
  p=Path(n);assert p.is_file() and p.suffix=='.jar';deps[str(p)]=sha(p)
assert all(sha(Path(n))==h for n,h in deps.items());classpath=':'.join([str(component),*deps]);classes=work/'test-classes';classes.mkdir();jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015';rules=r/'tools/quality/static'
stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
command=[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(classes),*[str(r/n) for n in paths]]
compiled=stage.step('test-compile',command,work,timeout=120)
compile_record=dict(actualExit=compiled['actualExit'],stage=compiled,inputHashes={n:sha(r/n) for n in paths},sourceClosureCount=len(paths),selectedWholeCounts=selected,expectedTests=113,sourceCore=c['sourceCore'],rootCompile=ref(cp),physicalClassHashes=physical,testPhysicalHashes={str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},work=str(work),toolDependencies=deps,classpath=classpath,productTestsExecuted=0)
(out/'compile.json').write_text(json.dumps(compile_record,indent=2)+'\n');assert compiled['actualExit']==0 and not compiled['timedOut']
source_paths=[x['path'] for x in f['files']];assert len(source_paths)==4
for x in f['files']:assert sha(r/x['path'])==x['afterFormatSha256']
listing=out/'sources.txt';listing.write_text(''.join(str(r/n)+'\n' for n in source_paths))
libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]
commands={'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(classes)+':'+classpath,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]}
stages={n:stage.step(n,cmd,work,timeout=120) for n,cmd in commands.items()};raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
 tag=node.tag.rsplit('}',1)[-1]
 if tag in ['error','configerror']:errors.append(dict(node.attrib))
 if tag=='file':
  for x in node:
   if x.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**x.attrib,message=(x.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error')
assert stages['checkstyle']['actualExit']==0 and stages['pmd']['actualExit'] in [0,4] and not any(x['timedOut'] for x in stages.values())
pins={str(p):sha(p) for p in [*map(Path,deps),*libs,sg/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',tc/'google-java-format-1.36.1-all-deps.jar']}
v=dict(compile_record,actualExit=0,terminalAtUTC=stages['pmd']['endUTC'],mainInputHashes=c['inputHashes'],testSourceHashes=compile_record['inputHashes'],toolDependencyHashes=pins,wholeTestSourceCounts=selected,sourcePatch=ref(fp),stages=stages,rawFindings=raw,processingErrors=errors,changedSourcesChecked=4,unchangedOriginalWholeSelectedTests=107,newLockTests=6,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,compiledSources=len(paths),expectedTests=113,pmdRaw=len(raw),productTests=0)))
