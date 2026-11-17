"""Compile four whole ordinary Test sources; static-check just the changed Main/new Test."""
from pathlib import Path
import hashlib,json,re,shutil,sys,xml.etree.ElementTree as ET
r=Path.cwd();sys.path.insert(0,str(r/'tools/quality'))
import pg9666_pagination_static as stage
from public_catch_manual_lexer import lexical
b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
rootp=b/'evidence/PG37390-summary-four-main-compile-v2/manifest.json';root=ld(rootp);fp=b/'evidence/PG37389-summary-close-format-v1/manifest.json';fmt=ld(fp);assert root['actualExit']==fmt['actualExit']==0
original=ld(b/'evidence/PG37370-summary-source-before-v1/manifest.json');selected=dict(original['originalThreeTestHashes']);assert len(selected)==3
new='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/InspectionSummaryValueContractTest.java';selected[new]=sha(r/new);assert all(sha(r/n)==h for n,h in selected.items())
graph='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/InspectionSummaryGraphContractTest.java';selected[graph]=sha(r/graph)
counts={n:len(re.findall(r'@Test\s+void',(r/n).read_text())) for n in selected};assert sum(counts.values())==23 and counts[new]==3 and counts[graph]==1
fenced={'TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException','RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest'}
assert all(not ({t for t,_ in lexical((r/n).read_text())}&fenced) for n in selected)
assert '.getDeclaredConstructor()' not in (r/new).read_text()
helper='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/JdbcResourceCases.java';assert '@Test' not in (r/helper).read_text();helperHashes={helper:sha(r/helper)}
out=b/'evidence/PG37394-summary-test-static-v2';work=r.parent/'pgpt-runs/PG379/pg37394-summary-test-static-v2';assert not out.exists() and not work.exists();out.mkdir();work.mkdir();component=work/'component';classes=work/'test-classes';component.mkdir();classes.mkdir();physical={}
for module,rows in root['physicalClassHashes'].items():
 for n,h in rows.items():
  assert n not in physical and Path(n).stem.split('$')[0] not in fenced
  p=Path(root['cwd'])/('src/schubert-nk-'+module)/'target/classes'/n;assert sha(p)==h;q=component/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);physical[n]=h
assert len(physical)==1101 and all(sha(r/n)==h for n,h in root['inputHashes'].items())
deps=ld(b/'evidence/PG37164-root-fixture-caller-compile-v2/manifest.json')['toolDependencies'];assert all(sha(Path(n))==h for n,h in deps.items());classpath=':'.join([str(component),*deps]);jdk=tc/'jdk-25.0.4/bin';sg=tc/'static-gates-20261015';rules=r/'tools/quality/static'
stage.SLOT=out;stage.ENV=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(tc/'jdk-25.0.4'),LANG='C.UTF-8')
cmd=[str(jdk/'javac'),'--release','25','-g','-proc:none','-implicit:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(classes),*[str(r/n) for n in selected],str(r/helper)];compiled=stage.step('test-compile',cmd,work,timeout=120)
record=dict(actualExit=compiled['actualExit'],terminalAtUTC=compiled['endUTC'],sourceCore=root['sourceCore'],rootCompile=ref(rootp),stage=compiled,inputHashes=selected,testSourceHashes=selected,sourceClosureCount=5,wholeTestSourceCounts=counts,expectedTests=23,originalWholeCases=19,newWholeCases=4,helperSourceHashes=helperHashes,actualCompileSourceClosureCount=6,physicalClassHashes=physical,testPhysicalHashes={str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},toolDependencies=deps,work=str(work),classpath=classpath,productTestsExecuted=0)
(out/'compile.json').write_text(json.dumps(record,indent=2)+'\n');assert compiled['actualExit']==0 and not compiled['timedOut']
sources=[x['path'] for x in fmt['files']];assert len(sources)==2 and all(sha(r/x['path'])==x['afterSha256'] for x in fmt['files']);listing=out/'sources.txt';listing.write_text(''.join(str(r/n)+'\n' for n in sources));libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))]
commands={'checkstyle':[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),'@'+str(listing)],'pmd':[str(jdk/'java'),'-cp',':'.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',str(tc/'jdk-25.0.4/lib/jrt-fs.jar')+':'+str(classes)+':'+classpath,'--no-cache','--format','xml','--report-file',str(out/'pmd.xml')]}
stages={n:stage.step(n,command,work,timeout=120) for n,command in commands.items()};raw=[];errors=[]
for node in ET.parse(out/'pmd.xml').getroot().iter():
 tag=node.tag.rsplit('}',1)[-1]
 if tag in ['error','configerror']:errors.append(dict(node.attrib))
 if tag=='file':
  for x in node:
   if x.tag.rsplit('}',1)[-1]=='violation':raw.append(dict(path=str(Path(node.get('name')).relative_to(r)),**x.attrib,message=(x.text or '').strip()))
assert not errors and not ET.parse(out/'checkstyle.xml').getroot().findall('.//error') and stages['checkstyle']['actualExit']==0 and stages['pmd']['actualExit'] in [0,4] and not any(x['timedOut'] for x in stages.values())
pins={str(p):sha(p) for p in [*map(Path,deps),*libs,sg/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',tc/'google-java-format-1.36.1-all-deps.jar']}
v=dict(record,actualExit=0,terminalAtUTC=stages['pmd']['endUTC'],mainInputHashes=root['inputHashes'],sourcePatch=ref(fp),toolDependencyHashes=pins,stages=stages,rawFindings=raw,processingErrors=errors,reflectionReview=dict(privateReflection=False,osOrApplicationPermissionChanges=False),heldClassfileActions=0,actualBackendNativeRootOperations=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,testSourceClosure=5,expected23=True,raw=len(raw),productTests=0)))
