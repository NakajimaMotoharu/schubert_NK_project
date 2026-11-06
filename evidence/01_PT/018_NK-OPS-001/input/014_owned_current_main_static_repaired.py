"""Fresh source-only six-Main PMD/Checkstyle; saved normal/SB bytes, no Product execution."""
from pathlib import Path
import sys,json,hashlib,os,datetime,zipfile,shutil,subprocess,collections
import xml.etree.ElementTree as E
import pg9666_pagination_static as runner

ROOT=Path.cwd();RUNS=ROOT.parent/'pgpt-runs/PG379';TC=ROOT.parent/'toolchain'
NORMAL=RUNS/'pg19740-f03-index-style-six-main-compile-v1';SB=RUNS/'pg19742-f03-index-style-six-static-reactor-v1'
SLOT=RUNS/'pg19744-current-six-main-static-repaired-v1';PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/PG19744-current-six-main-static-repaired-v1'
RUNTIME=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG13218-spotbugs-fresh-aux-plan-recovery-v1/manifest.json'
RUNTIME_SHA='a60a6ff0579588e9a10b5a2de6b2d2f4587f983408645a87e8cd4c7ad6917564'
NORMAL_SHA='45fa13f0a99583a03cb765e2c0ce05d94bd9d9adeadd89187ff3334c58f31d8b'
SOURCE='28af318d0198fe7432ca6fcd234d3fabbfd10173'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

CONFIG=None;CONFIG_SHA=None;SB_SHA=None

def configure(path):
 global CONFIG,CONFIG_SHA,SB_SHA,NORMAL,NORMAL_SHA,SB,SLOT,PUBLIC,SOURCE
 p=Path(path);assert p.parent==Path('evidence/01_PT/018_NK-OPS-001/input') and p.name=='050_current_d8_main_static.json'
 CONFIG=ROOT/p;CONFIG_SHA=sha(CONFIG);c=json.loads(CONFIG.read_text());assert set(c)=={'source','normalSlot','normalSha256','sbSlot','sbSha256','slot','publicName'}
 assert c['source']=='d8ff9efb16a7da1b073bdf9770487e3e6415b636'
 assert c['normalSlot']=='pg20112-log-tx-six-main-compile-v1' and c['sbSlot']=='pg20114-log-tx-six-static-reactor-v1'
 assert c['slot']=='pg20150-current-d8-six-main-static-v1' and c['publicName']=='PG20150-current-d8-six-main-static-v1'
 SOURCE=c['source'];NORMAL=RUNS/c['normalSlot'];NORMAL_SHA=c['normalSha256'];SB=RUNS/c['sbSlot'];SB_SHA=c['sbSha256'];SLOT=RUNS/c['slot'];PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence'/c['publicName']

def read_inputs():
 if CONFIG is not None:assert sha(CONFIG)==CONFIG_SHA and sha(SB/'manifest.safe.json')==SB_SHA
 assert sha(NORMAL/'manifest.safe.json')==NORMAL_SHA and sha(RUNTIME)==RUNTIME_SHA
 normal=json.loads((NORMAL/'manifest.safe.json').read_text());old=json.loads(RUNTIME.read_text());sb=json.loads((SB/'manifest.safe.json').read_text())
 assert normal['source']==sb['source']==SOURCE and normal['actualExit']==sb['actualExit']==0 and normal['testsExecuted']==0
 all_inputs=normal['begin']['inputHashes'];inputs={p:h for p,h in all_inputs.items() if p.startswith('src/') and '/src/main/java/' in p and p.endswith('.java')}
 assert len(inputs)==966 and all('/src/test/' not in p and not p.startswith('tools/') for p in inputs)
 assert all(sha(ROOT/p)==h and sha(NORMAL/'snapshot'/p)==h for p,h in all_inputs.items())
 jarhashes={v['path']:v['sha256'] for v in normal['jars'].values()};assert len(jarhashes)==6
 aux={p:h for p,h in old['auxiliaryClasspathHashes'].items() if p not in old['currentJarHashes']}
 assert all('/toolchain/' in p and '/pgpt-runs/' not in p for p in aux);aux.update(jarhashes)
 assert all(sha(p)==h for p,h in aux.items())
 static=TC/'static-gates-20261015';pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
 rules=ROOT/'tools/quality/static';tools=[*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',TC/'jdk-25.0.4/bin/java']
 tools_hash={str(p):sha(p) for p in tools};return normal,sb,inputs,aux,pmd,tools_hash

def reports():
 normal,sb,inputs,aux,pmd,tools_hash=read_inputs();findings=[];processing=[];counts={};filesets={}
 for tool,tag in [('pmd','violation'),('checkstyle','error')]:
  path=SLOT/(tool+'.xml');root=E.parse(path).getroot();files=set()
  for node in root:
   kind=node.tag.rsplit('}',1)[-1]
   if kind in ['error','configerror']:processing.append({'tool':tool,'attributes':dict(node.attrib),'message':' '.join(node.itertext())[:500]});continue
   if kind!='file':continue
   full=Path(node.get('name'));relative=str(full.relative_to(NORMAL/'snapshot'));assert relative in inputs;files.add(relative)
   for item in node:
    itemtag=item.tag.rsplit('}',1)[-1]
    if itemtag in ['suppressedviolation']:raise AssertionError('suppressed violation in raw source report')
    if itemtag!=tag:raise AssertionError('unknown source report item')
    row={'tool':tool,'path':relative,'sourceSha256':inputs[relative],'attributes':dict(item.attrib),'rule':item.get('rule',item.get('source')),'message':' '.join(item.itertext()).strip() if tool=='pmd' else item.get('message'),'applicability':'UNCLASSIFIED','actualViolation':None,'ptExecutionExempt':False}
    if tool=='checkstyle' and row['rule'] in ['com.puppycrawl.tools.checkstyle.Checker','com.puppycrawl.tools.checkstyle.TreeWalker']:processing.append(row)
    else:findings.append(row)
  counts[tool]=sum(r['tool']==tool for r in findings);filesets[tool]=sorted(files)
 assert set(filesets['checkstyle'])==set(inputs)
 physical={}
 for role,item in normal['jars'].items():
  with zipfile.ZipFile(item['path']) as jar:
   expected={n[:-6].replace('/','.') for n in jar.namelist() if n.endswith('.class')};assert expected
  ref=sb['reports'][role];assert sha(ref['path'])==ref['sha256'];x=E.parse(ref['path']).getroot();actual=[n.get('class') for n in x.iter('ClassStats')];summary=x.find('FindBugsSummary');exact=bool(summary is not None and int(summary.get('total_classes'))==len(expected) and len(actual)==len(set(actual)) and set(actual)==expected)
  physical[role]={'normalJar':item,'report':ref['path'],'reportSha256':ref['sha256'],'expectedClasses':len(expected),'reportedClassStats':len(actual),'exactPhysicalClassSet':exact,'absent':sorted(expected-set(actual)),'extra':sorted(set(actual)-expected),'bugs':len(list(x.iter('BugInstance'))),'errors':len(list(x.iter('Error'))),'missingClasses':len(list(x.iter('MissingClass')))}
 return {'findings':findings,'processingErrors':processing,'rawCounts':counts,'reportedSourceFiles':filesets,'existingSixSpotbugsClassSets':physical}

def run():
 normal,sb,inputs,aux,pmd,tools_hash=read_inputs();assert not SLOT.exists() and not PUBLIC.exists();SLOT.mkdir();runner.SLOT=SLOT
 listing=SLOT/'source-list.txt';listing.write_text(''.join(str(NORMAL/'snapshot'/p)+'\n' for p in sorted(inputs)));(SLOT/'source-inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
 cp=os.pathsep.join(sorted(aux));static=TC/'static-gates-20261015';rules=ROOT/'tools/quality/static';java=str(TC/'jdk-25.0.4/bin/java')
 begin={'normalSource':SOURCE,'orchestrationHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'normalManifestSha256':NORMAL_SHA,'driverSha256':sha(__file__),'sourceInputHashes':inputs,'allNormalInputHashes':normal['begin']['inputHashes'],'sourceListSha256':sha(listing),'auxiliaryClasspathHashes':aux,'tools':tools_hash,'runtimeReferenceSha256':RUNTIME_SHA,'testSourceExcludedBeforeRead':True,'characterizationJavaExcluded':True,'applicationEntryInvoked':False,'productTestsExecuted':0,'noRootInvocation':True};(SLOT/'begin.safe.json').write_text(json.dumps(begin,indent=2)+'\n')
 stages={'pmd':runner.step('pmd',[java,'-Xmx2g','-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT,timeout=300)}
 stages['checkstyle']=runner.step('checkstyle',[java,'-Xmx1g','-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT,timeout=180)
 value=reports();assert all(not v['timedOut'] for v in stages.values());assert all(sha(p)==h for p,h in tools_hash.items());read_inputs()
 (SLOT/'findings.json').write_text(json.dumps(value['findings'],ensure_ascii=False,indent=2)+'\n');warnings={name:[line[:1000] for line in (SLOT/(name+'.stderr')).read_text().splitlines() if 'WARN' in line or 'ERROR' in line] for name in stages}
 complete=not value['processingErrors'] and stages['pmd']['actualExit'] in [0,4] and stages['checkstyle']['actualExit']>=0
 raw_gate=0 if complete and not value['findings'] else 1
 manifest={'actualExit':0 if complete else 1,'analysisComplete':complete,'rawGateExit':raw_gate,'actualApplicableViolationCount':None,'normalSource':SOURCE,'orchestrationHead':begin['orchestrationHead'],'atJST':datetime.datetime.now().astimezone().isoformat(),'beginSha256':sha(SLOT/'begin.safe.json'),'stages':stages,'sourceInputHashes':inputs,'mainSourceCount':len(inputs),'testSourceCount':0,'characterizationJavaIncluded':False,'auxCurrentNormalJarsChecked':True,'rawCounts':value['rawCounts'],'processingErrors':value['processingErrors'],'reportedSourceFiles':value['reportedSourceFiles'],'toolWarnings':warnings,'existingSixSpotbugsClassSets':value['existingSixSpotbugsClassSets'],'allMainSpotbugsClassSetsExact':all(x['exactPhysicalClassSet'] and x['bugs']==x['errors']==x['missingClasses']==0 for x in value['existingSixSpotbugsClassSets'].values()),'files':{n:sha(SLOT/n) for n in ['source-list.txt','source-inputs.json','pmd.xml','checkstyle.xml','findings.json','pmd.stdout','pmd.stderr','checkstyle.stdout','checkstyle.stderr']},'suppressionsAdded':False,'oldDiagnosticOrSuccessTransferred':False,'wholeF03Accepted':False,'whole451Accepted':False,'productTestsExecuted':0,'newAccepted':0,'coverageMeasured':False};(SLOT/'manifest.safe.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':manifest['actualExit'],'analysisComplete':complete,'rawGateExit':raw_gate,'rawCounts':value['rawCounts'],'processingErrors':len(value['processingErrors']),'sixSpotbugsClassSetsExact':manifest['allMainSpotbugsClassSetsExact'],'manifestSha256':sha(SLOT/'manifest.safe.json')}));raise SystemExit(manifest['actualExit'])

def post():
 m=json.loads((SLOT/'manifest.safe.json').read_text());b=json.loads((SLOT/'begin.safe.json').read_text());assert m['actualExit']==0 and sha(SLOT/'begin.safe.json')==m['beginSha256'];assert sha(__file__)==b['driverSha256'];assert not PUBLIC.exists();recomputed=reports();assert recomputed['rawCounts']==m['rawCounts'] and recomputed['processingErrors']==m['processingErrors'] and recomputed['existingSixSpotbugsClassSets']==m['existingSixSpotbugsClassSets'];assert json.loads((SLOT/'findings.json').read_text())==recomputed['findings']
 for n,s in m['stages'].items():
  assert s['startUTC']<=s['endUTC'] and not s['timedOut'];assert sha(SLOT/(n+'.stdout'))==s['stdoutSha256'] and sha(SLOT/(n+'.stderr'))==s['stderrSha256']
 assert all(sha(SLOT/n)==h for n,h in m['files'].items());assert all(sha(p)==h for p,h in {**b['tools'],**b['auxiliaryClasspathHashes']}.items());read_inputs();PUBLIC.mkdir(parents=True)
 for n in [*m['files'],'begin.safe.json','manifest.safe.json']:
  shutil.copyfile(SLOT/n,PUBLIC/n)
 for stage in m['stages']:
  for ending in ['begin.safe.json','process.safe.json','exit.safe.json']:shutil.copyfile(SLOT/(stage+'-'+ending),PUBLIC/(stage+'-'+ending))
 value=dict(m,originalManifestSha256=sha(SLOT/'manifest.safe.json'),independentPostReconstruction=True,productClassesExecuted=0,files={p.name:sha(p) for p in PUBLIC.iterdir() if p.is_file()});(PUBLIC/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'actualExit':0,'main':len(m['sourceInputHashes']),'rawGateExit':m['rawGateExit'],'rawCounts':m['rawCounts'],'manifestSha256':sha(PUBLIC/'manifest.json')}))

if __name__=='__main__':
 assert len(sys.argv) in [2,3] and sys.argv[1] in ['run','post']
 if len(sys.argv)==3:configure(sys.argv[2])
 if sys.argv[1]=='run':run()
 else:post()
