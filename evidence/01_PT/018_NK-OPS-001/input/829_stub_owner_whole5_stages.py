"""Prepare only; the Product whole5 uses canonical no-argument pg24886 entry."""
from pathlib import Path
import datetime,hashlib,json,os,sys,xml.etree.ElementTree as E
import pg9666_pagination_static as stage
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';RUNS=R.parent/'pgpt-runs/PG379';PRE=RUNS/'pg24866-stub-owner-prepare-v1';OUT=B/'evidence/PG24866-stub-owner-prepare-v1'
TEST=R/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/StubAnswerProviderTest.java';LAUNCHER=B/'input/828_stub_owner/StubOwnerWholeLauncher.java';REPORTER=R/'tools/quality/architecture/SharedSelectedJunitReporterV1.java';NORMAL=RUNS/'pg22084-api-stop-state-six-main-compile-v1';SOURCE='7aed8eace7c844c2f79f2e39db766faf914890d5'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes());write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert len(sys.argv)==2 and sys.argv[1]=='prepare'
assert all(n not in os.environ for n in ['JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','_JAVA_OPTIONS','CLASSPATH'])
assert sha(NORMAL/'manifest.safe.json')=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(NORMAL/'manifest.safe.json');assert nm['source']==SOURCE and nm['actualExit']==0
assert sha(REPORTER)=='c9d94f87d9cd8d3287601d6fe4e108c8cfcacfa3b5ba62b5f6c51cbd924d1515'
main=['StubAnswerProvider','AnswerResult','AnswerProvider'];mainPaths=[R/'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/application/question'/(n+'.java') for n in main]
assert all(sha(p)==nm['begin']['inputHashes'][str(p.relative_to(R))] for p in mainPaths)
if sys.argv[1]=='prepare':
 assert not PRE.exists() and not OUT.exists();PRE.mkdir();stage.SLOT=PRE;steps={}
 steps['format']=stage.step('format',[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--replace',str(TEST),str(LAUNCHER)],R,timeout=60);assert steps['format']['actualExit']==0
 filelist=PRE/'source-list.txt';filelist.write_text(str(TEST)+'\n');static=TC/'static-gates-20261015';rules=R/'tools/quality/static';pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
 sdk=[TC/'m2/repository'/p for p in ['org/junit/jupiter/junit-jupiter-api/5.13.4/junit-jupiter-api-5.13.4.jar','org/junit/platform/junit-platform-commons/1.13.4/junit-platform-commons-1.13.4.jar','org/opentest4j/opentest4j/1.3.0/opentest4j-1.3.0.jar','org/apiguardian/apiguardian-api/1.1.2/apiguardian-api-1.1.2.jar','org/jspecify/jspecify/1.0.0/jspecify-1.0.0.jar']]
 assert all(p.is_file() for p in sdk);api=Path(nm['jars']['api']['path']);assert sha(api)==nm['jars']['api']['sha256'];aux=os.pathsep.join(map(str,[api,*sdk]));jdk=TC/'jdk-25.0.4/bin'
 steps['pmd']=stage.step('pmd',[str(jdk/'java'),'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(filelist),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',aux,'--no-cache','--format','xml','--report-file',str(PRE/'pmd.xml')],PRE,timeout=120)
 steps['checkstyle']=stage.step('checkstyle',[str(jdk/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(PRE/'checkstyle.xml'),'@'+str(filelist)],PRE,timeout=90)
 reports={}
 for name,tag in [('pmd','violation'),('checkstyle','error')]:
  x=E.parse(PRE/(name+'.xml')).getroot();nodes=[n for n in x.iter() if n.tag.rpartition('}')[2]==tag];errors=[n for n in x.iter() if n.tag.rpartition('}')[2] in ['error','configerror']] if name=='pmd' else []
  assert not errors
  reports[name]=dict(rawFindings=len(nodes),processingErrors=len(errors),findings=[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())) for n in nodes])
 assert steps['pmd']['actualExit'] in [0,4] and steps['checkstyle']['actualExit']==0 and reports['checkstyle']['rawFindings']==0
 text=TEST.read_text();assert text.count('@Test')==text.count('@DisplayName')==5 and text.count('executor.invokeAll(tasks, 5, TimeUnit.SECONDS)')==1 and text.count('executor.shutdownNow();')==1 and text.count('executor.awaitTermination(10, TimeUnit.SECONDS)')==1
 assert not any(s in text for s in ['ProcessBuilder','DriverManager','getConnection(','@BeforeAll','System.getenv(']) and text.count('Files.')==2
 OUT.mkdir()
 for name in ['pmd.xml','checkstyle.xml','format.stdout','format.stderr','pmd.stdout','pmd.stderr','checkstyle.stdout','checkstyle.stderr']:(OUT/name).write_bytes((PRE/name).read_bytes())
 v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),productionCoreMain=SOURCE,testPath=str(TEST.relative_to(R)),testSha256=sha(TEST),launcherPath=str(LAUNCHER.relative_to(R)),launcherSha256=sha(LAUNCHER),reporterSha256=sha(REPORTER),mainSourceHashes={str(p.relative_to(R)):sha(p) for p in mainPaths},stages=steps,reports=reports,toolHashes={str(p):sha(p) for p in [TC/'google-java-format-1.36.1-all-deps.jar',static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',*pmd,*sdk]},sourceToolSha256=sha(Path(__file__)),productTestsExecuted=0,staticApplicabilityPending=True,files={p.name:sha(p) for p in OUT.iterdir()})
 write(OUT/'manifest.json',v);print(json.dumps(dict(actualExit=0,reports=reports,manifestSha256=sha(OUT/'manifest.json'))));sys.exit(0)
