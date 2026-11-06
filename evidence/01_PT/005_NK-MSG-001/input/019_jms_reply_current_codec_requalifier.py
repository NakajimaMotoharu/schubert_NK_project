"""Original seven reply tests, current frozen codec dependency, no backend or new fixture."""
from pathlib import Path
import datetime, hashlib, json, platform, re, shutil, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
import pg9666_pagination_static as c

r=Path.cwd();runs=r.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prep=runs/'pg21818-jms-reply-current-codec-compile-v1';static=runs/'pg21820-jms-reply-current-codec-static-v1';unit=runs/'pg21822-jms-reply-current-codec-seven-unit-v1';post=runs/'pg21824-jms-reply-current-codec-seven-post-v1'
test='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/messaging/JmsReplyDecoderTest.java'
testclass='dev.codex.schubert.nk.web.messaging.JmsReplyDecoderTest'
targets=['dev/codex/schubert/nk/web/messaging/JmsReplyDecoder','dev/codex/schubert/nk/web/messaging/ValidatedReply']
forbidden={'dev/codex/schubert/nk/api/error/TemporaryInfrastructureException','dev/codex/schubert/nk/web/bootstrap/WebStartupException','dev/codex/schubert/nk/api/idempotency/FingerprintKeyRing','dev/codex/schubert/nk/api/idempotency/ResponseSnapshotCodec'}
methods={'acceptanceReplyUsesExactRegisteredAsyncProfile','validReplyProducesAnImmutableRedactedResult','nullTypeBodyLengthAndCopyAnomaliesAreRejected','destinationMustBeThePermanentApprovedAddressWithoutReplyTo','requiredHeadersPropertiesAndValuesDenyMissingBlankAndMalformedInputs','transportAndWireValuesMustExactlyMatchTheReplyHeaderAndRoute','identityPropertiesMustRetainExactLowercaseCanonicalUuidText'}
spec=r/'evidence/01_PT/005_NK-MSG-001/019_JMSReply現codec接続・既七PT再資格仕様.md'
jdk=r.parent/'toolchain/jdk-25.0.4';java=str(jdk/'bin/java');javac=str(jdk/'bin/javac');cli=r.parent/'toolchain/org.jacoco.cli-0.8.15-nodeps.jar';agent=r.parent/'toolchain/m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def unchanged(ctx):
 for n,h in ctx['inputHashes'].items():assert sha(r/n)==h
 for n,h in ctx['runtimeInputs'].items():assert sha(Path(n))==h

if sys.argv[1]=='prepare':
 assert not prep.exists() and not static.exists();prep.mkdir();static.mkdir();(prep/'test-classes').mkdir();(prep/'component').mkdir()
 head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 for p in [Path(__file__),spec,r/test]:assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(p.relative_to(r))])).hexdigest()==sha(p)
 original=r/'evidence/01_PT/005_NK-MSG-001/evidence/provisional/PG18644-jms-uuid-normal-post-v1/manifest.json';assert sha(original)=='5cafcb6a2f2d4a8b61dcc33a614de0338b5e4dc99980da102a10a1f0ea8d3ba6';old=load(original);rawp=original.parent/'manifest.safe.json';assert sha(rawp)==old['files']['manifest.safe.json'];raw=load(rawp);assert sha(r/test)==old['sourcePins'][test]
 normalp=runs/'pg20990-outbox-required-six-main-compile-v1/manifest.safe.json';assert sha(normalp)=='1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618';normal=load(normalp);assert normal['actualExit']==0
 sbp=runs/'pg20992-outbox-required-six-static-reactor-v1/manifest.safe.json';assert sha(sbp)=='2d3130234ce662ebf2b0bb1f57e74c123ec68e7a307feb10844231bd9822a20a' and load(sbp)['actualExit']==0
 sdk={n:h for n,h in raw['begin']['dependencies'].items() if not Path(n).name.startswith('schubert-nk-') and not Path(n).name.startswith('jspecify-')};assert len(sdk)==8
 annotation=r.parent/'toolchain/m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';pins=load(r/'evidence/01_PT/016_NK-WEB-002/evidence/PG21660-business-mvc-format-v1/manifest.json')['toolHashes'];assert sha(annotation)==pins[str(annotation)];sdk[str(annotation)]=sha(annotation)
 jars={k:normal['jars'][k] for k in ['web','protocol']};runtime={**sdk,**{v['path']:v['sha256'] for v in jars.values()},str(cli):sha(cli),str(agent):sha(agent),java:sha(Path(java)),javac:sha(Path(javac))}
 cp=':'.join([v['path'] for v in jars.values()]+list(sdk));assert all(n not in cp for n in ['schubert-nk-api-','schubert-nk-storage-','schubert-nk-bootstrap-','schubert-nk-batch-','postgresql-','artemis-server-'])
 for n,h in runtime.items():assert sha(Path(n))==h
 inputs={test:sha(r/test),str(Path(__file__).relative_to(r)):sha(Path(__file__)),str(spec.relative_to(r)):sha(spec)}
 physical={}
 with zipfile.ZipFile(jars['web']['path']) as z:
  for cls in targets:
   assert cls not in forbidden;data=z.read(cls+'.class');expected=normal['normalPhysicalClassHashes']['web:'+cls+'.class'];assert hashlib.sha256(data).hexdigest()==expected
   dest=prep/'component'/(cls+'.class');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);physical[cls]=expected;source='src/schubert-nk-web/src/main/java/'+cls+'.java';assert sha(r/source)==normal['begin']['inputHashes'][source];inputs[source]=sha(r/source)
 ctx=dict(source=head,productionCoreMain=normal['source'],atJST=datetime.datetime.now().astimezone().isoformat(),inputHashes=inputs,runtimeInputs=runtime,normalManifest=dict(path=str(normalp),sha256=sha(normalp)),mainStatic=dict(path=str(sbp),sha256=sha(sbp)),original14=dict(path=str(original.relative_to(r)),sha256=sha(original)),classpath=cp,jars=jars,physicalHashes=physical,testClass=testclass,expectedMethods=sorted(methods),expectedTests=7,javaVersion='25.0.4',os=platform.platform(),session='PG21822-JMS-REPLY-CURRENT-CODEC7',sdkGlobalSyscallZeroMeasured=False,actualBackendActions=False)
 write(prep/'context.safe.json',ctx);c.SLOT=prep;stage=c.step('compile',[javac,'--release','25','-proc:none','-g','-encoding','UTF-8','-Xlint:all','-Werror','-cp',cp,'-d',str(prep/'test-classes'),str(r/test)],r,timeout=60);assert stage['actualExit']==0 and not stage['timedOut']
 oldstatic=load(runs/'pg18636-jms-uuid-static-v1/manifest.safe.json')
 for n,h in oldstatic['tools'].items():assert sha(Path(n))==h
 (static/'source-list.txt').write_text(str(r/test)+'\n');pmd=list(oldstatic['stages']['pmd']['command'])
 for flag,value in [('--file-list',str(static/'source-list.txt')),('--aux-classpath',cp),('--report-file',str(static/'pmd.xml'))]:pmd[pmd.index(flag)+1]=value
 cs=list(oldstatic['stages']['checkstyle']['command'][:-4]);cs[cs.index('-o')+1]=str(static/'checkstyle.xml');cs.append(str(r/test));c.SLOT=static
 ps=c.step('pmd',pmd,r,timeout=120);css=c.step('checkstyle',cs,r,timeout=60);assert ps['actualExit'] in (0,4) and css['actualExit']==0 and not ps['timedOut'] and not css['timedOut']
 tree=ET.parse(static/'pmd.xml');findings=[]
 for node in tree.getroot().iter():
  if node.tag.rsplit('}',1)[-1]=='violation':
   rule=node.get('rule');assert rule in ['UseConcurrentHashMap','UseProperClassLoader','CompareObjectsWithEquals'];findings.append(dict(rule=rule,line=int(node.get('beginline')),endline=int(node.get('endline')),message=' '.join(''.join(node.itertext()).split()),classification='CONTEXTUAL_NONAPPLICABLE',actualViolation=False,reason={'UseConcurrentHashMap':'Fresh per-case local Map and synchronous public-JMS Proxy; no shared worker or concurrent mutation.','UseProperClassLoader':'Proxy must implement the public JMS interface using its exact defining loader.','CompareObjectsWithEquals':'Own Proxy Object.equals deliberately compares proxy identity.'}[rule]))
  assert node.tag.rsplit('}',1)[-1] not in ['error','processingerror','configerror']
 assert not any(x.tag=='error' for x in ET.parse(static/'checkstyle.xml').getroot().iter())
 sm=dict(actualExit=0,rawPmdExit=ps['actualExit'],checkstyleExit=0,findings=findings,applicableViolations=0,source=ctx['source'],inputHashes={test:sha(r/test)},stages=dict(pmd=ps,checkstyle=css),suppressionAdded=False)
 write(static/'manifest.safe.json',sm);write(prep/'manifest.safe.json',dict(actualExit=0,source=head,contextSha256=sha(prep/'context.safe.json'),stage=stage,staticManifestSha256=sha(static/'manifest.safe.json'),targetClasses=targets));unchanged(ctx);print(json.dumps(dict(actualExit=0,compiledTestClasses=len(list((prep/'test-classes').rglob('*.class'))),rawStaticFindings=len(findings),applicableViolations=0)))
elif sys.argv[1]=='run':
 ctx=load(prep/'context.safe.json');assert load(prep/'manifest.safe.json')['actualExit']==load(static/'manifest.safe.json')['actualExit']==0;unchanged(ctx);assert not unit.exists();unit.mkdir();(unit/'tmp').mkdir();c.SLOT=unit
 console=next(n for n in ctx['runtimeInputs'] if Path(n).name=='junit-platform-console-standalone-1.13.4.jar')
 cmd=[java,'-Dfile.encoding=UTF-8','-Duser.language=ja','-Duser.country=JP','-Duser.timezone=Asia/Tokyo','-Djava.io.tmpdir='+str(unit/'tmp'),'-javaagent:'+str(agent)+'=destfile='+str(unit/'jacoco.exec')+',sessionid='+ctx['session']+',append=false','-Xlog:class+init=info:file='+str(unit/'class-init.stdout'),'-jar',console,'execute','--disable-banner','--class-path',str(prep/'test-classes')+':'+ctx['classpath'],'--reports-dir',str(unit/'xml'),'--fail-if-no-tests','--details','summary','--select-class',testclass]
 write(unit/'begin.safe.json',dict(source=ctx['source'],contextSha256=sha(prep/'context.safe.json'),command=cmd,expectedTests=7,session=ctx['session'],atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat()));stage=c.step('unit',cmd,r,timeout=120);write(unit/'manifest.safe.json',dict(actualExit=stage['actualExit'],source=ctx['source'],stage=stage,contextSha256=sha(prep/'context.safe.json')));print(json.dumps(dict(actualExit=stage['actualExit'],timedOut=stage['timedOut'],newMethods=0,requalifiedExpected=7)));assert stage['actualExit']==0 and not stage['timedOut'];unchanged(ctx)
elif sys.argv[1]=='post':
 ctx=load(prep/'context.safe.json');unchanged(ctx);u=load(unit/'manifest.safe.json');assert u['actualExit']==0 and not u['stage']['timedOut'];assert not post.exists();post.mkdir();c.SLOT=post
 cases=[];xmlpins={}
 for p in sorted((unit/'xml').glob('TEST-*.xml')):
  xmlpins[str(p)]=sha(p);tree=ET.parse(p)
  for t in tree.getroot().iter('testcase'):
   assert not any(t.find(n) is not None for n in ['failure','error','skipped']);assert t.get('classname')==testclass;cases.append(t.get('name','').removesuffix('()'))
 assert len(cases)==7 and set(cases)==methods
 stages={};stages['coverage']=c.step('coverage',[java,'-jar',str(cli),'report',str(unit/'jacoco.exec'),'--classfiles',str(prep/'component'),'--sourcefiles',str(r/'src/schubert-nk-web/src/main/java'),'--xml',str(post/'coverage.xml'),'--csv',str(post/'coverage.csv')],r,timeout=60)
 stages['classinfo']=c.step('classinfo',[java,'-jar',str(cli),'classinfo',str(prep/'component')],r,timeout=60);stages['execinfo']=c.step('execinfo',[java,'-jar',str(cli),'execinfo',str(unit/'jacoco.exec')],r,timeout=60)
 assert all(x['actualExit']==0 and not x['timedOut'] for x in stages.values());classids={n:i for i,n in re.findall(r'class 0x([0-9a-f]{16})\s+(\S+)',(post/'classinfo.stdout').read_text())};assert set(classids)==set(targets)
 data={n:dict(id=i,hits=int(h),probes=int(p)) for i,h,p,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',(post/'execinfo.stdout').read_text(),re.M)}
 for n in targets:assert data[n]['id']==classids[n] and data[n]['hits']>0
 assert not any(data.get(n,{}).get('hits',0)>0 for n in forbidden)
 init=set(re.findall(r"Initializing '([^']+)",(unit/'class-init.stdout').read_text()));assert not (init & forbidden)
 coverage={};root=ET.parse(post/'coverage.xml').getroot();assert {x.get('name') for x in root.findall('.//class')}==set(targets);assert [x.get('id') for x in root.findall('sessioninfo')]==[ctx['session']]
 for node in root.findall('.//class'):
  cs={x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in node.findall('counter')};assert all(cs[k]['missed']==0 for k in ['LINE','METHOD','CLASS'])
  if 'BRANCH' in cs:assert cs['BRANCH']['missed']==0
  coverage[node.get('name')]=cs
 out=r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21824-jms-reply-current-codec-seven-v1';assert not out.exists();out.mkdir();files={}
 for folder in [prep,static,unit,post]:
  prefix={prep:'compile-',static:'static-',unit:'unit-',post:''}[folder]
  for p in folder.iterdir():
   if p.is_file() and p.suffix in ['.json','.stdout','.stderr','.xml','.csv','.exec','.txt']:
    dest=out/('jacoco.exec' if p.suffix=='.exec' else prefix+p.name);shutil.copyfile(p,dest);files[dest.name]=sha(dest)
 safe=ET.Element('testsuite',dict(tests='7',failures='0',errors='0',skipped='0'))
 for name in sorted(cases):ET.SubElement(safe,'testcase',dict(classname=testclass,name=name))
 ET.ElementTree(safe).write(out/'testcases.safe.xml',encoding='UTF-8',xml_declaration=True);files['testcases.safe.xml']=sha(out/'testcases.safe.xml')
 m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=ctx['source'],productionCoreMain=ctx['productionCoreMain'],context=ctx,files=files,tests=7,failures=0,errors=0,skipped=0,aborted=0,newMethods=0,requalifiedExistingInvocations=7,newSourceProofs=0,newAcceptance=0,selectedTestMethods=[[testclass,n] for n in sorted(cases)],coverage=coverage,physicalHashes=ctx['physicalHashes'],classIds=classids,execMatches={n:data[n] for n in targets},session=ctx['session'],originalXmlPins=xmlpins,unitTerminal=u,reportStages=stages,static=load(static/'manifest.safe.json'),naturalZeroBranchClasses=[n for n,v in coverage.items() if 'BRANCH' not in v],oldExecUnion=False,manualCoverageExclusions=False,defaultCompilerFiltersOnly=True,heldInitializationHits=[],heldExecutedProbes=0,actualBackendActions=False,whole451Accepted=False,formalUpdated=False,effortRate=None)
 write(out/'manifest.json',m);unchanged(ctx);print(json.dumps(dict(actualExit=0,tests=7,newMethods=0,targetSources=2,heldInitAndProbeHits=0,manifestSha256=sha(out/'manifest.json'))))
else:raise ValueError('prepare, run or post only')
