"""Independent original terminal / whole XML / immutable Git / single-exec CRC-init / full counters."""
from pathlib import Path
import ast,datetime,hashlib,json,re,struct,subprocess,tarfile,xml.etree.ElementTree as ET
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';w=r.parent/'pgpt-runs/PG379/pg30748-haruka-common91-v4';e=b/'evidence/PG30756-common91-v4-independent-whole-source-post-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
cfg=load(w/'payload-config.json');source=cfg['sourceCommit'];unit=load(b/'evidence/PG30752-haruka-common91-unit-raw-terminal-v4/manifest.json');assert source==unit['sourceCommit']=='cf868540e7e461dc1809e4f0b7a677ccddeed168'
assert unit['actualExit'] in (0,1) and unit['ownedProcessGroupAbsent'] is True and not unit['timedOut']
assert not unit['coverageExclusions'] and not unit['qualitySkips'] and not unit['oldExecCombined']
archive=w/'collect.private.tar';assert load(w/'collect-local-terminal.json')['actualExit']==0
p=w/'independent-post-input';assert not (e/'manifest.json').exists();p.mkdir(mode=0o700,exist_ok=True);e.mkdir(exist_ok=True)
with tarfile.open(archive) as t:
 entries=t.getmembers();assert len({x.name for x in entries})==len(entries)
 for x in entries:assert x.isfile() and not Path(x.name).is_absolute() and '..' not in Path(x.name).parts and x.size<64*1024**2
 t.extractall(p,filter='data')
collection=load(p/'collection-manifest.json');assert collection['sourceCommit']==source and not collection['missing'] and not collection['unexpectedClassNames']
for name,digest in collection['files'].items():assert sha(p/name)==digest
assert load(p/'unit-result.json')==unit and load(p/'unit-verify-exit.json')=={k:v for k,v in unit.items() if k in ['actualExit','timedOut','atUTC','process','logSha256','ownedProcessGroupAbsent']}
stage=load(p/'stage.json');owner=load(p/'owner.json');assert stage['sourceCommit']==source==owner['sourceCommit'] and owner['bootId']==unit['process']['bootId']
assert stage['archiveSha256']==sha(w/'source-payload.tar') and stage['configSha256']==sha(p/'payload/config.json') and load(p/'payload/config.json')==cfg
begin=load(p/'unit-verify-begin.json');process=load(p/'unit-verify-process.json');assert process['owner']==unit['process'] and process['pgid']==unit['process']['pid'] and begin['cwd']==str(Path('/home/mini/schubert-nk-pgpt/runs/pg30748-common91-v4/payload/source'))
command=begin['command'];assert command[-1]=='verify' and '-Dtest='+','.join(unit['selectedWholeClasses']) in command
assert not any(x in ' '.join(command) for x in ['select-method','skipTests','jacoco.skip','append=true','excludes=','enable-native-access'])
assert datetime.datetime.fromisoformat(begin['atUTC'])<datetime.datetime.fromisoformat(unit['atUTC'])
closure=load(b/'evidence/PG30718-common91-whole-source-closure-and-independent-inverses-v1/manifest.json')
expected=set()
for name in closure['allSelectedTestPaths']:
 text=(r/name).read_text();package=re.search(r'^package\s+([\w.]+);',text,re.M).group(1);names=re.findall(r'@Test\s+(?:@[\w.]+\([\s\S]*?\)\s+)*void\s+(\w+)\s*\(',text)
 if Path(name).stem=='GateContractValidatorNegativeTest':
  assert '@ValueSource(strings = {FAILED, "FAILED", "FLAKY", "SKIP", "SKIPPED", "DISABLED", "NOT_RUN"})' in text
  assert 'private static final String FAILED = "FAIL";' in text
  names+=['rejectsEveryNonPassExecutionStatus(String)['+str(n)+']' for n in range(1,8)]
 if Path(name).stem=='GateContractTest':
  for method in ['secretScannerHandlesBinaryEvidenceWithoutUtf8Decoding','fullByteScanIncludesLargeFilesBoundariesPrefixesEmptyAndIo']:
   assert re.search(r'void\s+'+method+r'\(\s*@TempDir Path \w+\)',text)
   names[names.index(method)]=method+'(Path)'
 assert len(names)==unit['selectedWholeClasses'][Path(name).stem]
 expected.update((package+'.'+Path(name).stem,n) for n in names)
assert len(expected)==91
module=p/'payload/source/program/characterization/target';actual=[];xmls=[];env={}
for name,count in unit['selectedWholeClasses'].items():
 f=module/'surefire-reports'/('TEST-dev.codex.schubert.characterization.'+name+'.xml');tree=ET.parse(f);root=tree.getroot();cases=root.findall('testcase')
 assert int(root.get('tests'))==len(cases)==count and all(int(root.get(k))==0 for k in ['failures','errors','skipped'])
 assert not any(root.findall('.//'+tag) for tag in ['failure','error','skipped'])
 actual.extend((n.get('classname'),n.get('name')) for n in cases)
 env.update({x.get('name'):x.get('value') for x in root.findall('./properties/property') if x.get('name') in ['java.version','os.name','os.arch','file.encoding']})
 for n in [root,*cases]:
  for child in list(n):
   if child.tag in ['properties','system-out','system-err']:n.remove(child)
 ET.indent(tree);out=e/f.name;tree.write(out,encoding='utf-8',xml_declaration=True);xmls.append(dict(name=f.name,rawSha256=sha(f),sanitizedSha256=sha(out),cases=count))
assert len(actual)==len(set(actual))==91 and set(actual)==expected
assert env['java.version']=='25.0.4'
for name,digest in cfg['payloadHashes'].items():
 if name.startswith('source/'):
  path=name[len('source/'):];assert sha(r/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',source+':'+path])).hexdigest()
with tarfile.open(w/'source-payload.tar') as t:
 assert all(int(x.mtime)==cfg['payloadMtimeEpoch']>0 for x in t.getmembers())
prepare=load(p/'prepare-result.json');ad=load(p/'admission.json');assert prepare==load(b/'evidence/PG30750-haruka-common91-full-static-raw-v4/manifest.json')
assert ad==load(i/'2577_common91_v4_static_admission.json') and ad['sourceCommit']==source and ad['prepareSha256']==sha(p/'prepare-result.json')
assert prepare['standardResourceCopyVerified'] and len(prepare['resourceOutputs'])==7 and ad['applicable']==ad['unclassified']==0
sb=ET.parse(module/'spotbugsXml.xml').getroot();assert not any(sb.findall('.//'+n) for n in ['BugInstance','MissingClass','Error'])
assert len(sb.findall('.//ClassStats'))==10 and not ET.parse(p/'checkstyle.xml').findall('.//error')
classes=module/'classes';physical={str(f.relative_to(classes)):sha(f) for f in classes.rglob('*.class')};assert len(physical)==10
helper=i/'1415_manifest_current_independent_post.py';nodes=[n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name in ['crc64','code_count']];assert len(nodes)==2
ns=dict(struct=struct);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(helper),'exec'),ns)
ids={n[:-6]:ns['crc64']((classes/n).read_bytes()) for n in physical};methods={n[:-6]:ns['code_count']((classes/n).read_bytes()) for n in physical}
java=r.parent/'toolchain/jdk-25.0.4/bin/java';cli=r.parent/'toolchain/org.jacoco.cli-0.8.15-nodeps.jar';tools={}
for label,args in [('classinfo',['classinfo',str(classes)]),('execinfo',['execinfo',str(module/'jacoco.exec')])]:
 out=w/(label+'-independent.private.stdout');err=w/(label+'-independent.private.stderr');assert not out.exists() and not err.exists()
 with out.open('x') as stdout,err.open('x') as stderr:result=subprocess.run([str(java),'-jar',str(cli),*args],stdout=stdout,stderr=stderr,timeout=45)
 assert result.returncode==0 and err.stat().st_size==0;tools[label]=out.read_text()
info={name:dict(crc=crc,instructions=int(inst)) for inst,branch,line,method,complexity,crc,name in re.findall(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+class 0x([0-9a-f]{16}) (\S+)$',tools['classinfo'],re.M)}
assert set(info)==set(ids) and all(info[n]['crc']==crc and info[n]['instructions']>0 for n,crc in ids.items())
assert tools['execinfo'].count('Session "')==1 and 'Session "PG30748-COMMON91"' in tools['execinfo']
probes={n:(crc,int(hit),int(total)) for crc,hit,total,n in re.findall(r'^([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(\S+)$',tools['execinfo'],re.M)}
assert all(n in probes and probes[n][0]==crc and probes[n][1]>0 for n,crc in ids.items())
init=[]
for log in p.glob('class-init-*.log'):
 initialized=set(re.findall(r"Initializing '([^']+)'",log.read_text()))
 if set(ids)<=initialized:init.append(dict(logSha256=sha(log),allMain10InitializedTogether=True))
assert len(init)==1
tree=ET.parse(module/'site/jacoco/jacoco.xml');root=tree.getroot();covclasses={n.get('name'):n for n in root.findall('.//class')};assert set(covclasses)==set(ids)
counters=lambda n:{x.get('type'):dict(covered=int(x.get('covered')),missed=int(x.get('missed'))) for x in n.findall('counter')}
coverage=counters(root)
for key,row in coverage.items():
 for field in ['covered','missed']:assert sum(counters(n).get(key,{}).get(field,0) for n in covclasses.values())==row[field]
misses={n:{k:v['missed'] for k,v in counters(node).items() if v['missed']} for n,node in covclasses.items() if any(v['missed'] for v in counters(node).values())}
four100=all(coverage[k]['missed']==0 and coverage[k]['covered']>0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for n in list(root.findall('sessioninfo')):root.remove(n)
ET.indent(tree);tree.write(e/'coverage.sanitized.xml',encoding='utf-8',xml_declaration=True)
result=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=source,productionCoreMain=cfg['productionCoreMain'],run=cfg['run'],originalMavenExit=unit['actualExit'],ownedGroupAbsent=True,tests=91,suites=10,failures=0,errors=0,skipped=0,newTestDefinitions=0,toolScopeNotAppRoster=True,physicalClasses=10,positiveMainCrc=10,singleExec=True,execSha256=sha(module/'jacoco.exec'),classIds=ids,physicalClassHashes=physical,actualJvmCodeMethodCounts=methods,actualJvmCodeMethods=sum(methods.values()),jacocoDefaultMethods=coverage['METHOD']['covered']+coverage['METHOD']['missed'],coverage=coverage,uncoveredFullSourceClasses=misses,wholeScopeFour100=four100,manualCoverageExclusions=[],oldExecCombined=False,allMain10SameJvmInit=init,independentFullXML=xmls,environment=env,standardMavenResources7=prepare['resourceOutputs'],pinnedOriginalBaseline27=len(cfg['originalBaselineHashes'])==27,staticApplicable=0,staticUnclassified=0,staticProcessingErrors=0,checkstyle=0,spotbugs=0,formalAccepted=False,whole451Accepted=False,newAcceptance=0,effortRate=None,actualDbRootVmNativeKeyActions=0)
(e/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['actualExit','tests','suites','positiveMainCrc','coverage','wholeScopeFour100','actualJvmCodeMethods','jacocoDefaultMethods','formalAccepted']}))
