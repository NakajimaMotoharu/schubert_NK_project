from pathlib import Path
import json,hashlib,subprocess,os,zipfile,xml.etree.ElementTree as ET,re,datetime
import pg9666_pagination_static as shared
R=Path('/home/mini/codex/project1/work/pgpt-foundation');W=R.parent/'pgpt-runs/PG379';S=W/'pg18590-config-loaders-current-whole10-v1';TC=R.parent/'toolchain';shared.SLOT=S
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
planfile=next((R/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104').glob('656_*.json'));plan=json.loads(planfile.read_text());source=plan['productionMainSource'];normalfile=R/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG14216-typed-marker-guard-six-compile-v1/manifest.json';assert H(normalfile)=='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3';normal=json.loads(normalfile.read_text());assert normal['source']==source and normal['actualExit']==normal['testsExecuted']==0
mainhash={p:h for p,h in normal['begin']['inputHashes'].items() if '/src/main/' in p};assert mainhash and all(H(R/p)==h for p,h in mainhash.items())
jars=[Path(normal['jars'][m]['path']) for m in ['protocol','storage','bootstrap','api','web']];assert all(H(p)==normal['jars'][m]['sha256'] for p,m in zip(jars,['protocol','storage','bootstrap','api','web']))
console=TC/'junit-platform-console-standalone-1.13.4.jar';cli=TC/'org.jacoco.cli-0.8.15-nodeps.jar';agent=TC/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';yaml=TC/'m2/repository/org/snakeyaml/snakeyaml-engine/3.1.1/snakeyaml-engine-3.1.1.jar'
assert H(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892';assert H(cli)=='d2b74b20b415163c1f53261e7c5ef4445b788327094208ff821e0c2baf9bc8f1'
classes=S/'test-classes';classes.mkdir();component=S/'component';component.mkdir();inputs={str(p):H(p) for p in [*jars,console,cli,agent,yaml]};testhash={row['test']:row['testSha256'] for row in plan['rows']};assert all(H(R/p)==h for p,h in testhash.items())
names=[];physical={}
for row in plan['rows']:
 name=row['main'].split('/main/java/')[1].removesuffix('.java');names.append(name)
 with zipfile.ZipFile(normal['jars'][row['module']]['path']) as z:
  closure=[p for p in z.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')];assert closure==[name+'.class']
  p=component/(name+'.class');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(closure[0]));physical[name]=H(p)
cp=os.pathsep.join(map(str,[classes,*jars,yaml,console]));jdk=TC/'jdk-25.0.4/bin';session='PG18590-CONFIG-LOADERS-CURRENT-WHOLE10';stages=[]
begin=dict(source=source,testSource=plan['source'],branch='dev-foundation',head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),planSha256=H(planfile),driverSha256=H(__file__),normalManifestSha256=H(normalfile),normalMainInputHashes=mainhash,testInputHashes=testhash,dependencies=inputs,physical=physical,session=session,effects=plan['effects'],oldRuntimeTransferred=False,oldExecCombined=False,expectedTests=10,environment=shared.ENV,startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());put(S/'begin.safe.json',begin)
def step(label,cmd):
 v=shared.step(label,list(map(str,cmd)),S,timeout=180);stages.append(dict(label=label,**v));put(S/'stages.safe.json',stages);assert v['actualExit']==0 and not v['timedOut'],label;return v
try:
 step('compile',[jdk/'javac','--release','25','-encoding','UTF-8','-cp',cp,'-d',classes,*[R/p for p in testhash]])
 xml=S/'xml';cmd=[jdk/'java',f'-Xlog:class+init=info:file={S/"class-init.log"}',f'-javaagent:{agent}=destfile={S/"jacoco.exec"},append=false,sessionid={session},includes=dev.codex.schubert.nk.api.bootstrap.ApiConfigurationLoader:dev.codex.schubert.nk.web.bootstrap.WebConfigurationLoader','-cp',cp,'org.junit.platform.console.ConsoleLauncher','execute','--disable-banner','--details=summary','--include-engine=junit-jupiter','--fail-if-no-tests','--reports-dir',xml,'--config=junit.jupiter.extensions.autodetection.enabled=false','--config=junit.jupiter.execution.parallel.enabled=false']
 for row in plan['rows']:cmd+=['--select-class','dev.codex.schubert.nk.'+row['module']+'.bootstrap.'+('Api' if row['module']=='api' else 'Web')+'ConfigurationLoaderTest']
 step('unit',cmd)
 step('coverage',[jdk/'java','-jar',cli,'report',S/'jacoco.exec','--classfiles',component,'--xml',S/'coverage.xml','--csv',S/'coverage.csv'])
 step('execinfo',[jdk/'java','-jar',cli,'execinfo',S/'jacoco.exec'])
 step('classinfo',[jdk/'java','-jar',cli,'classinfo','--verbose',component])
 static=TC/'static-gates-20261015';rules=R/'tools/quality/static';pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))];listing=S/'sources.txt';listing.write_text('\n'.join(str(R/p) for p in testhash)+'\n');inputs.update({str(p):H(p) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']})
 # Findings are not converted to success; command returns recorded, analysis below.
 for label,cmd in [('pmd',[jdk/'java','-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',listing,'--rulesets',rules/'pmd.xml','--use-version','java-25','--minimum-priority','5','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',S/'pmd.xml']),('checkstyle',[jdk/'java','-jar',static/'checkstyle-14.3.0-all.jar','-c',rules/'checkstyle.xml','-f','xml','-o',S/'checkstyle.xml','@'+str(listing)])]:
  v=shared.step(label,list(map(str,cmd)),S,timeout=180);stages.append(dict(label=label,**v));put(S/'stages.safe.json',stages);assert not v['timedOut'] and v['actualExit'] in (0,4)
 assert all(H(Path(p))==h for p,h in inputs.items()) and all(H(R/p)==h for p,h in mainhash.items()) and all(H(R/p)==h for p,h in testhash.items())
 put(S/'manifest.safe.json',dict(actualExit=0,source=source,testSource=plan['source'],begin=begin,stages=stages,toolAndDependencyHashes=inputs,files={p.name:H(p) for p in S.iterdir() if p.is_file() and p.name not in ['manifest.safe.json']},testsNotYetIndependentlyQualified=True,formalUpdated=False,whole451Accepted=False));print('COMPLETED_TOOL_STAGES',H(S/'manifest.safe.json'))
except BaseException as e:
 put(S/'failure.safe.json',dict(source=source,exceptionType=type(e).__name__,stages=stages,noReplay=True));raise
