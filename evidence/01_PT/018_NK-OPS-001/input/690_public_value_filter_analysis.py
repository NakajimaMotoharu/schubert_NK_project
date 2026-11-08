"""One official tool analyzer with empty execution data; product bytes are not on its class path."""
from pathlib import Path
import hashlib,json,datetime,zipfile
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';RUNS=R.parent/'pgpt-runs/PG379';S=RUNS/'pg24296-public-value-six-official-filter-analysis-v1';assert not S.exists();O=B/'evidence/PG24296-public-value-six-official-filter-analysis-v1';assert not O.exists();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_bytes())
bridge=B/'evidence/PG24190-public-value-six-source-byte-bridge-v1';bm=load(bridge/'manifest.json');rows=load(bridge/'source-byte-bridges.json');assert len(rows)==6 and bm['knownMethodMetadata']==30 and bm['historicalMeasuredMethods']==18
normal=RUNS/'pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json';assert sha(normal)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';nm=load(normal)
tc=R.parent/'toolchain';repo=tc/'m2/repository';jars=[repo/'org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',*[repo/('org/ow2/asm/'+n+'/9.10.1/'+n+'-9.10.1.jar') for n in ['asm','asm-tree','asm-commons']]];deps={str(p):sha(p) for p in jars}
S.mkdir();(S/'classes').mkdir();(S/'input').mkdir();members={};files=[]
with zipfile.ZipFile(nm['jars']['api']['path']) as z:
 for row in rows:
  assert row['physicalKey'].startswith('api:') and not any(n in row['physicalKey'] for n in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
  name=row['physicalKey'][4:];raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==row['classSha256']
  p=S/'input'/Path(name).name;assert not p.exists();p.write_bytes(raw);files.append(str(p));members[name]=row['classSha256']
source=B/'input/690_public_value_filter/OfficialMeasuredMethods.java';cp=':'.join(map(str,jars));c.SLOT=S
compile=c.step('tool-compile',[str(tc/'jdk-25.0.4/bin/javac'),'-proc:none','-implicit:none','--release','25','-Xlint:all','-Werror','-cp',cp,'-d',str(S/'classes'),str(source)],R);assert compile['actualExit']==0
analyze=c.step('tool-analyze',[str(tc/'jdk-25.0.4/bin/java'),'-Dfile.encoding=UTF-8','-cp',str(S/'classes')+':'+cp,'OfficialMeasuredMethods',*files],R);assert analyze['actualExit']==0
methods=[]
for line in (S/'tool-analyze.stdout').read_text().splitlines():
 owner,name,descriptor,missed,instructions=line.split('\t');assert int(missed)==1 and int(instructions)>0;methods.append(dict(className=owner,name=name,descriptor=descriptor,emptyDataMethodMissed=int(missed),emptyDataInstructionsMissed=int(instructions)))
assert len(methods)==18 and len({(m['className'],m['name'],m['descriptor']) for m in methods})==18
O.mkdir();(O/'official-retained-methods.json').write_text(json.dumps(methods,ensure_ascii=False,indent=2)+'\n')
for name in ['tool-compile.stdout','tool-compile.stderr','tool-analyze.stdout','tool-analyze.stderr']:(O/name).write_bytes((S/name).read_bytes())
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),sourceProductionMain=nm['source'],historicalBridgeManifest=dict(path=str((bridge/'manifest.json').relative_to(R)),sha256=sha(bridge/'manifest.json')),exactPhysicalMembers=members,toolDependencies=deps,toolSourceSha256=sha(source),stages=dict(compile=compile,analysis=analyze),toolClassHashes={str(p.relative_to(S/'classes')):sha(p) for p in (S/'classes').glob('*.class')},rawMethods=30,officialRetainedMethods=18,emptyExecutionData=True,allAnalyzedMethodsUncovered=True,productClassPathEntries=0,productClassInitializationOrInvocation=False,oldPrivateArtifactsRead=False,productTestsExecuted=0,coverageMeasured=False,manualFilterOrCounterExclusions=[],newAcceptance=0,formalUpdated=False,effortRate=None,files={p.name:sha(p) for p in O.iterdir()})
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawMethods=30,officialRetainedMethods=18,allUncovered=True,manifestSha256=sha(O/'manifest.json'))))
