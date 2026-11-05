"""QA054 owned pure protocol qualification: source-pinned normal JAR, no backend execution."""
from pathlib import Path
import sys,os,json,hashlib,subprocess,datetime,zipfile,re,shutil,xml.etree.ElementTree as ET
import pg9666_pagination_static as runner
root=Path.cwd();runs=root.parent/'pgpt-runs/PG379';tc=root.parent/'toolchain';jdk=tc/'jdk-25.0.4/bin';phase=sys.argv[1];assert phase in {'prepare','static','run','post'}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
core='da176a90e7d59c23aaa50b2a00f42c200590b775';comp=runs/'pg19412-qa054-protocol-six-main-compile-v1';main=json.loads((comp/'manifest.safe.json').read_text());assert main['source']==core and main['actualExit']==0
jar=Path(main['jars']['protocol']['path']);assert sha(jar)==main['jars']['protocol']['sha256']
proto='src/schubert-nk-protocol/';testroot=root/proto/'src/test';console=tc/'junit-platform-console-standalone-1.13.4.jar';annotations=tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';deps=[jar,console,annotations];assert sha(console)=='3fdfc37e29744a9a67dd5365e81467e26fbde0b7aa204e6f8bbe79eeaa7ae892'
selected=['layout.WebLogActionContractTest','codec.PayloadCodecTest','codec.PayloadGoldenVectorTest','layout.LayoutFieldCatalogTest','layout.PayloadTypeCatalogTest','layout.PayloadSemanticValidatorTest','layout.SemanticFieldValueTest','layout.SemanticDirectBoundaryTest','layout.semantic.ProtocolSemanticTypeTest','layout.semantic.EnumWireCompatibilityTest','layout.PayloadPaginationBoundaryTest','codec.AuthenticationErrorProfileTest','codec.ScenarioRecordEncodingTest'];selected=['dev.codex.schubert.nk.protocol.'+x for x in selected]
changed=['layout/LayoutFieldCatalog','codec/PayloadCodec','layout/log/WebLogEventData','layout/PayloadSemanticValidator'];mainpaths=[proto+'src/main/java/dev/codex/schubert/nk/protocol/'+p+'.java' for p in changed]
prepared=runs/'pg19450-qa054-protocol-test-compile-v1';static=runs/'pg19452-qa054-protocol-static-v1';unit=runs/'pg19458-qa054-protocol-selected-unit-v1';session='PG19458-QA054-PROTOCOL';pub=root/'evidence/01_PT/002_NK-PRO-002/evidence/PG19458-qa054-protocol-selected-v1'
for p,h in main['begin']['inputHashes'].items():assert sha(root/p)==h
if phase=='prepare':
 assert not prepared.exists();prepared.mkdir();runner.SLOT=prepared;snapshot=prepared/'snapshot';snapshot.mkdir();files=sorted(testroot.rglob('*'));inputs={}
 for p in files:
  if p.is_file():
   rel=p.relative_to(root);dst=snapshot/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(p.read_bytes());inputs[str(rel)]=sha(p)
 sources=sorted(snapshot.rglob('*.java'));out=prepared/'test-classes';out.mkdir();args=prepared/'sources.txt';args.write_text('\n'.join(str(p) for p in sources)+'\n');cmd=[str(jdk/'javac'),'-encoding','UTF-8','--release','25','-Xlint:all','-Werror','-cp',os.pathsep.join(map(str,deps)),'-d',str(out),'@'+str(args)];stage=runner.step('compile',cmd,root)
 resources=snapshot/proto/'src/test/resources'
 if stage['actualExit']==0 and resources.exists():shutil.copytree(resources,out,dirs_exist_ok=True)
 result={'coreSource':core,'sourceAtCompile':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'actualExit':stage['actualExit'],'command':cmd,'inputHashes':inputs,'dependencies':{str(p):sha(p) for p in deps},'classHashes':{str(p.relative_to(out)):sha(p) for p in out.rglob('*.class')},'stage':stage,'selectedClasses':selected};(prepared/'manifest.safe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'compile':stage['actualExit'],'classes':len(result['classHashes'])}));raise SystemExit(stage['actualExit'])
if phase=='static':
 assert not static.exists();static.mkdir();runner.SLOT=static;pm=json.loads((prepared/'manifest.safe.json').read_text());assert pm['actualExit']==0
 paths=[root/p for p in mainpaths]+[root/proto/'src/test/java'/Path(c.replace('.','/')+'.java') for c in selected if c.endswith(('WebLogActionContractTest','PayloadCodecTest','PayloadGoldenVectorTest','PayloadTypeCatalogTest','IndependentNamedFieldOracle','SemanticDirectBoundaryTest'))];lst=static/'sources.txt';lst.write_text('\n'.join(map(str,paths))+'\n');sg=tc/'static-gates-20261015';libs=[sg/'record-fix-v1/pmd-record-1298.jar',*sorted((sg/'pmd-bin-7.28.0/lib').glob('*.jar'))];rules=root/'tools/quality/static';cmd=[str(jdk/'java'),'-cp',os.pathsep.join(map(str,libs)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(lst),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(map(str,deps)),'--no-cache','--format','xml','--report-file',str(static/'pmd.xml')];stages={'pmd':runner.step('pmd',cmd,root)};stages['checkstyle']=runner.step('checkstyle',[str(jdk/'java'),'-jar',str(sg/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(static/'checkstyle.xml'),'@'+str(lst)],root);findings=[];errors=[]
 for f in ['pmd.xml','checkstyle.xml']:
  tree=ET.parse(static/f);findings += [(Path(n.get('name','')).name,v.get('rule') or v.get('source'),v.get('beginline') or v.get('line'),(v.text or v.get('message') or '').strip()) for n in tree.iter() if n.tag.split('}')[-1]=='file' for v in n if v.tag.split('}')[-1] in {'violation','error'}];errors += [n.attrib for n in tree.iter() if n.tag.split('}')[-1] in {'error','configerror'} and n.get('filename')]
 result={'source':core,'inputHashes':{str(p.relative_to(root)):sha(p) for p in paths},'stages':stages,'findings':findings,'processingErrors':errors,'toolHashes':{str(p):sha(p) for p in [*libs,sg/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml']}};(static/'manifest.safe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'findings':findings,'processingErrors':errors},ensure_ascii=False));raise SystemExit(0)
if phase=='run':
 head=sys.argv[2];assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head;assert not unit.exists();pm=json.loads((prepared/'manifest.safe.json').read_text());assert pm['actualExit']==0
 for p,h in pm['inputHashes'].items():assert sha(root/p)==hashlib.sha256(subprocess.check_output(['git','show',head+':'+p])).hexdigest()==h
 unit.mkdir();runner.SLOT=unit;(unit/'tmp').mkdir();agent=tc/'m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar';cli=tc/'org.jacoco.cli-0.8.15-nodeps.jar';cmd=[str(jdk/'java'),'-Djava.io.tmpdir='+str(unit/'tmp'),'-Dfile.encoding=UTF-8','-Duser.timezone=Asia/Tokyo','-javaagent:'+str(agent)+'=destfile='+str(unit/'jacoco.exec')+',sessionid='+session+',append=false','-Xlog:class+init=info:file='+str(unit/'class-init.log'),'-jar',str(console),'execute','--disable-banner','--class-path',os.pathsep.join([str(prepared/'test-classes'),str(jar),str(annotations)]),'--reports-dir',str(unit/'xml'),'--details','summary','--fail-if-no-tests']
 for name in selected:cmd+=['--select-class',name]
 begin={'source':head,'coreSource':core,'mainManifestSha256':sha(comp/'manifest.safe.json'),'compileManifestSha256':sha(prepared/'manifest.safe.json'),'inputs':{**pm['inputHashes'],**{p:sha(root/p) for p in mainpaths}},'dependencies':pm['dependencies'],'selectedClasses':selected,'session':session,'command':cmd,'toolHash':sha(__file__),'startedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat()};(unit/'begin.safe.json').write_text(json.dumps(begin,indent=2)+'\n');stages={'unit':runner.step('unit',cmd,root,timeout=180)};component=unit/'component';component.mkdir();physical={}
 with zipfile.ZipFile(jar) as z:
  prefixes=['dev/codex/schubert/nk/protocol/'+p for p in changed]
  for n in z.namelist():
   if any(n==p+'.class' or n.startswith(p+'$') and n.endswith('.class') for p in prefixes):
    dst=component/n;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read(n));physical[n[:-6]]=sha(dst)
 stages['coverage']=runner.step('coverage',[str(jdk/'java'),'-jar',str(cli),'report',str(unit/'jacoco.exec'),'--classfiles',str(component),'--xml',str(unit/'jacoco.xml')],root);counts={'tests':0,'failures':0,'errors':0,'skipped':0};methods=[]
 for p in (unit/'xml').glob('TEST-*.xml'):
  tree=ET.parse(p);n=tree.getroot()
  for k in counts:counts[k]+=int(n.get(k,0))
  methods += [(t.get('classname'),t.get('name')) for t in n.findall('testcase')]
 coverage={}
 for n in ET.parse(unit/'jacoco.xml').getroot().findall('package/sourcefile'):coverage[n.get('name')]={c.get('type'):{'covered':int(c.get('covered')),'missed':int(c.get('missed'))} for c in n.findall('counter')}
 result={'begin':begin,'actualExit':stages['unit']['actualExit'],'stages':stages,**counts,'testMethods':methods,'physicalHashes':physical,'coverage':coverage,'sourceInputsUnchanged':all(sha(root/p)==h for p,h in begin['inputs'].items()),'backendActions':0,'scope':'explicit pure protocol classes/ownedtmp/memory/JDK providers; no runtime heldgraph'};(unit/'manifest.safe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['actualExit','tests','failures','errors','skipped','coverage']}));raise SystemExit(stages['unit']['actualExit'])
assert phase=='post';m=json.loads((unit/'manifest.safe.json').read_text());b=m['begin'];assert m['actualExit']==0 and all(m[k]==0 for k in ['failures','errors','skipped']);assert m['sourceInputsUnchanged'];assert sha(__file__)==b['toolHash'];assert sha(comp/'manifest.safe.json')==b['mainManifestSha256'] and sha(prepared/'manifest.safe.json')==b['compileManifestSha256'];assert not pub.exists()
for p,h in b['inputs'].items():assert hashlib.sha256(subprocess.check_output(['git','show',b['source']+':'+p])).hexdigest()==h
pub.mkdir(parents=True);files={}
for name in ['manifest.safe.json','begin.safe.json','unit-exit.safe.json','unit-process.safe.json','unit.stdout','unit.stderr','coverage-exit.safe.json','jacoco.xml','jacoco.exec']:
 shutil.copyfile(unit/name,pub/name);files[name]=sha(pub/name)
for p in (unit/'xml').glob('TEST-*.xml'):
 tree=ET.parse(p);n=tree.getroot();props=n.find('properties');n.remove(props) if props is not None else None
 for child in list(n):
  if child.tag in {'system-out','system-err'}:n.remove(child)
 for child in n.findall('testcase'):
  for extra in list(child):
   if extra.tag in {'system-out','system-err'}:child.remove(extra)
 dst=pub/p.name;tree.write(dst,encoding='utf-8',xml_declaration=True);files[p.name]=sha(dst)
manifest={'source':b['source'],'productionCoreMain':core,'actualExit':0,'tests':m['tests'],'failures':0,'errors':0,'skipped':0,'coverage':m['coverage'],'physicalHashes':m['physicalHashes'],'inputHashes':b['inputs'],'normalJarSha256':sha(jar),'originalManifest':{'path':str(unit/'manifest.safe.json'),'sha256':sha(unit/'manifest.safe.json')},'files':files,'static':'see separate raw applicability report','global451Accepted':False,'backendActions':0};(pub/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'manifestSha256':sha(pub/'manifest.json'),'tests':m['tests'],'source':b['source']}))
