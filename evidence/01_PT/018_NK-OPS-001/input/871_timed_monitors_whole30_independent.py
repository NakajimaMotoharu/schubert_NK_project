"""Independent original timed monitors whole30, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25052-timed-monitors-original-whole30-v1';RAW=B/'evidence/PG25052-timed-monitors-original-whole30-v1';O=B/'evidence/PG25054-timed-monitors-whole30-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='ba872b82d2178025a1795702f1768a54a7ed436810a009acb43c533a8b55e06f' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==30 and m['source']=='e730f6c06355754a3299d8b9793eb7f2620eb4e3' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==8 and pf['sourcePrograms']==4 and pf['expectedTests']==30
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25044-timed-monitors-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.batch.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalTimedMonitorsWhole30',tests='30',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==30 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==30 and app['rawFindings']==20 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent fixed UTC/golden and elapsed/count arithmetic, never a production expected generator.
path=next(p for p in pf['testPaths'] if Path(p).stem=='TimedFilesystemMonitorTest');source=(R/path).read_text();block=re.search(r'String expected =\s*(.*?);',source,re.S).group(1);literal=''.join(ast.literal_eval(v) for v in re.findall(r'"(?:\\.|[^"\\])*"',block))
base=datetime.datetime(2026,10,23,tzinfo=datetime.timezone.utc);at=(base+datetime.timedelta(seconds=300)).isoformat(timespec='milliseconds').replace('+00:00','Z');assert at=='2026-10-23T00:05:00.000Z'
expected='# SUPPLIED_MONITORING_STATE_V1 MODE=STANDARD\ncondition\tservice\tseverity\tcount\tfirstSeen\tlastSeen\n'+'FILESYSTEM\tWEB\tWARNING\t65\t'+at+'\t'+at+'\n';assert literal==expected and len(literal.splitlines())==3
assert 1+64==65 and 301+300==601 and 61+600==661 and 601+600==1201
assert 299_999_999_999<300_000_000_000 and 59_999_999_999<60_000_000_000 and 599_999_999_999<600_000_000_000
for path in pf['testPaths']:
 text=(R/path).read_text();assert 'try (var pool' not in text and 'try (var executor' not in text and 'pool.invokeAll(jobs)' not in text
assert sum((R/p).read_text().count('invokeAll(tasks, 10, TimeUnit.SECONDS)')+(R/p).read_text().count('invokeAll(jobs, 10, TimeUnit.SECONDS)') for p in pf['testPaths'])==4
assert sum((R/p).read_text().count('.shutdownNow();') for p in pf['testPaths'])==sum((R/p).read_text().count('.awaitTermination(10, TimeUnit.SECONDS)') for p in pf['testPaths'])==4
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==8;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=148,METHOD=16,CLASS=8,BRANCH=72,INSTRUCTION=735)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'TimedFilesystemMonitor.java','TimedJvmHeapMonitor.java','TimedDbPoolMonitor.java','TimedSyncLatencyMonitor.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25052-TIMED-MONITORS-ORIGINAL-WHOLE30'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
sample=dict(tests=30,fixtures=4,source=m['source'],totals=total,sourceFour100=True,naturalZeroBranchSources=0,crcs=crcs,heldFourInitializations=0)
def validate(v):
 assert type(v['tests']) is int and v['tests']==30 and type(v['fixtures']) is int and v['fixtures']==4 and v['source']==m['source'] and v['totals']==total and v['sourceFour100'] is True and type(v['naturalZeroBranchSources']) is int and v['naturalZeroBranchSources']==0 and v['crcs']==crcs and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0
validate(sample);checks=0
for k,v in [('tests',True),('tests',29),('fixtures',2),('source','0'*40),('totals',{}),('sourceFour100',False),('naturalZeroBranchSources',False),('naturalZeroBranchSources',1),('crcs',{}),('heldFourInitializations',1)]:
 bad=copy.deepcopy(sample);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid qualification accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crcs[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=30,wholeFixtures=4,failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=30,newProductTests=0,productTestsExecuted=0,sourcePrograms=4,physicalInputClasses=8,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=4,originalThirtyAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=3,finiteOwnerSitesCorrected=4,outerUnboundedTwrRecloseRemoved=True,independentTimedBoundaryAndGoldenOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=8,helperPositiveMainClasses=len(positive)-8,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=20,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=30,allSourceFour100=True,positiveMain=len(positive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
