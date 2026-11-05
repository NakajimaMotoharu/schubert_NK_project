"""Exact memory-only MediaRange port qualification; phase-specific fresh outputs, no native fixtures."""
from pathlib import Path
import sys,os,json,hashlib,subprocess,datetime,zipfile,xml.etree.ElementTree as E
import pg9666_pagination_static as r
root=Path.cwd();runs=root.parent/'pgpt-runs/PG379';tc=root.parent/'toolchain';jdk=tc/'jdk-25.0.4/bin';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();phase=sys.argv[1];main='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/media/MediaRangeService.java';test='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/media/MediaRangePortTest.java';core='b09393b0e746b55fd480176d57996d65bd76a95d';comp=runs/'pg18642-jms-uuid-six-main-compile-v1';base=json.loads((comp/'manifest.safe.json').read_text());assert base['actualExit']==0 and base['source']==core
for n,h in base['begin']['inputHashes'].items():
 assert sha(root/n)==h
for j in base['jars'].values():assert sha(j['path'])==j['sha256']
console=tc/'junit-platform-console-standalone-1.13.4.jar';assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892';deps=[Path(base['jars'][n]['path']) for n in ['protocol','web']];classpath=os.pathsep.join(map(str,[*deps,console]))
if phase=='prepare':
 slot=runs/'pg18794-media-range-port-compile-v1';assert not slot.exists();slot.mkdir();r.SLOT=slot;stages={}
 stages['format']=r.step('format',[str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--replace',str(root/test)],root)
 assert stages['format']['actualExit']==0
 inputs={n:sha(root/n) for n in [main,test]};classes=slot/'test-classes';classes.mkdir();stages['test-compile']=r.step('test-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',classpath,'-d',str(classes),str(root/test)],root)
 value={'actualExit':stages['test-compile']['actualExit'],'source':core,'gitHead':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'testUncommitted':True,'inputHashes':inputs,'normalCompileManifest':{'path':str(comp/'manifest.safe.json'),'sha256':sha(comp/'manifest.safe.json')},'normalMainInputCount':len(base['begin']['inputHashes']),'jars':{str(p):sha(p) for p in deps},'consoleSha256':sha(console),'classpath':classpath,'stages':stages,'classHashes':{str(p.relative_to(classes)):sha(p) for p in classes.rglob('*.class')},'testExecution':False,'actualBackendOperations':0};(slot/'manifest.safe.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'actualExit':value['actualExit'],'manifestSha256':sha(slot/'manifest.safe.json'),'mainRecompiled':False,'testsExecuted':0}));raise SystemExit(value['actualExit'])
if phase=='static':
 slot=runs/'pg18796-media-range-port-static-v1';assert not slot.exists();slot.mkdir();r.SLOT=slot;prepared=runs/'pg18794-media-range-port-compile-v1';pm=json.loads((prepared/'manifest.safe.json').read_text());assert pm['actualExit']==0
 for n,h in pm['inputHashes'].items():assert sha(root/n)==h
 files=[root/main,root/test];(slot/'source-list.txt').write_text(''.join(str(p)+'\n' for p in files));static=tc/'static-gates-20261015';rules=root/'tools/quality/static';pmd=[static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
 stages={};stages['pmd']=r.step('pmd',[str(jdk/'java'),'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(slot/'source-list.txt'),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',classpath,'--no-cache','--format','xml','--report-file',str(slot/'pmd.xml')],slot)
 stages['checkstyle']=r.step('checkstyle',[str(jdk/'java'),'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(slot/'checkstyle.xml'),'@'+str(slot/'source-list.txt')],slot);reports={}
 for key,path,tag in [('pmd',slot/'pmd.xml','violation'),('checkstyle',slot/'checkstyle.xml','error')]:
  x=E.parse(path).getroot();nodes=[n for n in x.iter() if n.tag.rsplit('}',1)[-1]==tag];errors=[n for n in x.iter() if n.tag.rsplit('}',1)[-1] in (('error','configerror') if key=='pmd' else ())];reports[key]={'path':str(path),'sha256':sha(path),'findings':len(nodes),'processingErrors':len(errors),'items':[dict(n.attrib,message=' '.join(''.join(n.itertext()).split())[:300]) for n in nodes]}
 old=runs/'pg18648-jms-uuid-six-static-reactor-v1/manifest.safe.json';sb=json.loads(old.read_text());assert sb['actualExit']==0 and sb['source']==core
 for n,x in sb['reports'].items():
  assert sha(x['path'])==x['sha256'];tree=E.parse(x['path']).getroot();assert not tree.findall('.//BugInstance') and not tree.findall('.//MissingClass') and not tree.findall('.//Error')
 value={'coreSource':core,'compileManifestSha256':sha(prepared/'manifest.safe.json'),'inputHashes':pm['inputHashes'],'stages':stages,'reports':reports,'sameSourceSixMainSpotBugs':{'manifest':str(old),'sha256':sha(old),'reports':sb['reports'],'currentAllMainInputsEqualPG18642':True},'rules':{str(f):sha(f) for f in [rules/'pmd.xml',rules/'checkstyle.xml']},'suppressionAdded':False,'testsExecuted':0,'formalUpdated':False};(slot/'manifest.safe.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'manifestSha256':sha(slot/'manifest.safe.json'),'findings':{k:[v['findings'],v['processingErrors']] for k,v in reports.items()},'stages':{k:v['actualExit'] for k,v in stages.items()}}));raise SystemExit(0)
if phase=='post':
 import re,shutil
 p=runs/'pg18802-media-range-port-eight-unit-v1';out=root/'evidence/01_PT/009_NK-MED-001/evidence/PG18802-media-range-port-eight-v1';assert not out.exists();m=json.loads((p/'manifest.safe.json').read_text());b=m['begin'];assert b['source']=='4300e7eb1b0991e816e5d1be370a4c0a15eadd95' and b['coreSource']==core;assert m['actualExit']==0 and m['tests']==8 and all(m[k]==0 for k in ['failures','errors','skipped'])
 prepared=runs/'pg18794-media-range-port-compile-v1';pm=json.loads((prepared/'manifest.safe.json').read_text());assert sha(prepared/'manifest.safe.json')==b['compileManifestSha256'] and sha(comp/'manifest.safe.json')==b['mainCompileManifestSha256']
 for f,h in b['inputHashes'].items():assert sha(root/f)==h and hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+f])).hexdigest()==h
 for f,h in b['classHashes'].items():assert sha(prepared/'test-classes'/f)==h
 for f,h in {**b['dependencies'],**b['tools']}.items():assert sha(f)==h
 for n,x in m['stages'].items():
  assert x['actualExit']==0 and not x['timedOut'] and x['startUTC']<=x['endUTC'];assert sha(p/(n+'.stdout'))==x['stdoutSha256'] and sha(p/(n+'.stderr'))==x['stderrSha256']
 methods=re.findall(r'@Test\s+void\s+(\w+)\s*\(', (root/test).read_text());assert len(methods)==8;actual=[];xmlPins={}
 for f in sorted((p/'xml').glob('TEST-*.xml')):
  xmlPins[str(f)]=sha(f)
  for c in E.parse(f).getroot().findall('testcase'):
   assert not any(c.findall(tag) for tag in ['failure','error','skipped']);assert c.get('classname')=='dev.codex.schubert.nk.web.media.MediaRangePortTest';n=c.get('name');assert n.endswith('()') and n.count('(')==1;actual.append(n[:-2])
 assert len(actual)==8 and len(set(actual))==8 and set(actual)==set(methods)
 cmd=m['stages']['unit']['command'];assert cmd.count('--select-class')==1 and cmd[cmd.index('--select-class')+1]==b['selectedClasses'][0] and '--select-method' not in cmd;assert any('append=false' in v and 'sessionid='+b['session'] in v for v in cmd)
 for text in ['8 tests found','8 tests started','8 tests successful','0 tests failed','0 tests aborted','0 tests skipped','0 containers aborted']:assert text in (p/'unit.stdout').read_text()
 cp=cmd[cmd.index('--class-path')+1].split(os.pathsep);assert cp==[str(prepared/'test-classes'),*map(str,deps)];assert not any('storage' in v or 'playwright' in v or 'postgresql' in v for v in cp)
 physical=m['physical'];assert len(physical)==4
 with zipfile.ZipFile(deps[1]) as z:
  for n,h in physical.items():assert sha(p/'component'/(n+'.class'))==h and hashlib.sha256(z.read(n+'.class')).hexdigest()==h
 ids={n:crc for crc,n in re.findall(r'class 0x([0-9a-f]{16}) (\S+)',(p/'classinfo.stdout').read_text())};assert set(ids)==set(physical);execText=(p/'execinfo.stdout').read_text();assert execText.count('Session \"')==1 and 'Session \"'+b['session']+'\"' in execText
 execIds={n:(crc,int(hit),int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',execText,re.M)}
 coverage={};abstract=[]
 for c in E.parse(p/'coverage.xml').getroot().findall('.//package/class'):
  n=c.get('name');assert n in physical;cs={x.get('type'):{'covered':int(x.get('covered')),'missed':int(x.get('missed'))} for x in c.findall('counter')};coverage[n]=cs
  if cs:assert all(x['missed']==0 for x in cs.values()) and n in execIds and execIds[n][0]==ids[n]
  else:assert '$' in n and not c.findall('method');abstract.append(n)
 assert len(coverage)==4 and len(abstract)==3
 out.mkdir(parents=True)
 for name in ['manifest.safe.json','begin.safe.json','unit.stdout','unit.stderr','coverage.xml','coverage.csv','classinfo.stdout','execinfo.stdout','jacoco.exec']:shutil.copyfile(p/name,out/name)
 for n in m['stages']:
  for suffix in ['begin.safe.json','process.safe.json','exit.safe.json']:shutil.copyfile(p/(n+'-'+suffix),out/(n+'-'+suffix))
 suite=E.Element('testsuite',tests='8',failures='0',errors='0',skipped='0')
 for n in sorted(actual):E.SubElement(suite,'testcase',classname=b['selectedClasses'][0],name=n+'()')
 E.ElementTree(suite).write(out/'testcases.safe.xml',encoding='utf-8',xml_declaration=True)
 value={'actualExit':0,'atJST':datetime.datetime.now().astimezone().isoformat(),'source':b['source'],'productionCoreMain':core,'originalManifest':{'path':str(p/'manifest.safe.json'),'sha256':sha(p/'manifest.safe.json')},'originalXmlPins':xmlPins,'tests':8,'testClasses':1,'failures':0,'errors':0,'skipped':0,'aborted':0,'selectedTestMethods':sorted(actual),'normalMainCompileSourceInputsChecked':True,'allNormalJarHashesChecked':True,'inputHashes':b['inputHashes'],'physicalHashes':physical,'physicalClassIds':ids,'execMatches':{n:execIds[n] for n in physical if n in execIds},'session':b['session'],'coverage':coverage,'wholeSourceFourCounter100':['MediaRangeService.java'],'abstractInterfacesNoExecutableMethods':abstract,'interfacesExcludedFromReport':False,'oldExecUnion':False,'manualCoverageExclusions':[],'noNativeAccessFlag':not any('--enable-native-access' in v for v in cmd),'onlyMemoryCallbackFixtures':True,'oldSixNativeTestReplayed':False,'actualMediaAuthOrFilesOrHttpVerified':False,'newAccepted':0,'formalUpdated':False,'secondPilot':False,'files':{f.name:sha(f) for f in out.iterdir() if f.is_file()}}
 (out/'manifest.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({'actualExit':0,'tests':8,'sourceQualified':1,'physicalReported':4,'executablePhysical':1,'abstractInterfaces':3,'manifestSha256':sha(out/'manifest.json')}));raise SystemExit(0)
assert phase=='run'
slot=runs/'pg18802-media-range-port-eight-unit-v1';assert not slot.exists();slot.mkdir();r.SLOT=slot;prepared=runs/'pg18794-media-range-port-compile-v1';pm=json.loads((prepared/'manifest.safe.json').read_text());assert pm['actualExit']==0;head=sys.argv[2];assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
for f,h in pm['inputHashes'].items():assert sha(root/f)==h and hashlib.sha256(subprocess.check_output(['git','show',head+':'+f])).hexdigest()==h
for f,h in pm['classHashes'].items():assert sha(prepared/'test-classes'/f)==h
agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';assert sha(cli)=='d2b74b20b415163c1f53261e7c5ef4445b788327094208ff821e0c2baf9bc8f1';session='PG18802-MEDIA-RANGE-PORT-8';(slot/'tmp').mkdir();cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(slot/'tmp'),'-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(slot/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(slot/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',os.pathsep.join([str(prepared/'test-classes'),*map(str,deps)]),'--select-class','dev.codex.schubert.nk.web.media.MediaRangePortTest','--reports-dir',str(slot/'xml'),'--fail-if-no-tests','--details','summary'];begin={'coreSource':core,'source':head,'session':session,'compileManifestSha256':sha(prepared/'manifest.safe.json'),'mainCompileManifestSha256':sha(comp/'manifest.safe.json'),'inputHashes':pm['inputHashes'],'classHashes':pm['classHashes'],'dependencies':{str(p):sha(p) for p in deps},'tools':{str(p):sha(p) for p in [console,agent,cli]},'selectedClasses':['dev.codex.schubert.nk.web.media.MediaRangePortTest'],'expectedTests':8,'onlyMemoryCallbackFixtures':True,'actualNativeFsDbVmNetworkActions':0,'startUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};(slot/'begin.safe.json').write_text(json.dumps(begin,indent=2)+'\n');stages={'unit':r.step('unit',cmd,root,timeout=120)};component=slot/'component';component.mkdir();physical={}
with zipfile.ZipFile(deps[1]) as z:
 prefix='dev/codex/schubert/nk/web/media/MediaRangeService'
 for n in z.namelist():
  if n==prefix+'.class' or n.startswith(prefix+'$') and n.endswith('.class'):
   p=component/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n));physical[n[:-6]]=sha(p)
assert len(physical)==4
for label,args in [('coverage',['report',str(slot/'jacoco.exec'),'--classfiles',str(component),'--sourcefiles',str(root/'src/schubert-nk-web/src/main/java'),'--xml',str(slot/'coverage.xml'),'--csv',str(slot/'coverage.csv')]),('classinfo',['classinfo',str(component)]),('execinfo',['execinfo',str(slot/'jacoco.exec')])]:stages[label]=r.step(label,[str(jdk/'java'),'-jar',str(cli),*args],root)
cases=[]
for p in (slot/'xml').glob('TEST-*.xml'):
 for c in E.parse(p).getroot().findall('testcase'):cases.append({'class':c.get('classname'),'name':c.get('name'),'failure':bool(c.findall('failure')),'error':bool(c.findall('error')),'skipped':bool(c.findall('skipped'))})
assert all(sha(root/p)==h for p,h in pm['inputHashes'].items());value={'actualExit':stages['unit']['actualExit'],'begin':begin,'stages':stages,'cases':cases,'tests':len(cases),'failures':sum(x['failure'] for x in cases),'errors':sum(x['error'] for x in cases),'skipped':sum(x['skipped'] for x in cases),'physical':physical,'noOldExecUnion':True,'formalUpdated':False,'newAccepted':0};(slot/'manifest.safe.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k] for k in ['actualExit','tests','failures','errors','skipped']}|{'manifestSha256':sha(slot/'manifest.safe.json')}));raise SystemExit(value['actualExit'])
