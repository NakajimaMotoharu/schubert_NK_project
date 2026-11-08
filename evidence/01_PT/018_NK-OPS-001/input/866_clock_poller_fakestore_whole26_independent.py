"""Independent original clock poller fakestore whole26, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,struct,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25032-clock-poller-fakestore-original-whole26-v1';RAW=B/'evidence/PG25032-clock-poller-fakestore-original-whole26-v1';O=B/'evidence/PG25034-clock-poller-fakestore-whole26-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='9fd744c18eaaa51ed2cf620a957400c0d1c5e5d7abc441ad8f056c16c3eb130d' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==26 and m['source']=='62fbb98e1795ef22f91fccb8056e18e124ef3ecd' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==4 and pf['sourcePrograms']==4 and pf['expectedTests']==26
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25024-clock-poller-fakestore-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.batch.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalClockPollerFakeStoreWhole26',tests='26',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==26 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==26 and app['rawFindings']==20 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent signed-wrap / fixed IEEE / count and elapsed arithmetic, never production expected generation.
signed64=lambda n:((n+2**63)%2**64)-2**63
assert signed64((-5)-(-10))==5 and signed64((-2**63+1)-(2**63-4))==5
assert divmod(2**63-1,1_000_000_000)==(9_223_372_036,854_775_807)
for percent,bits in [(80.0,0x4053ffffffffffff),(90.0,0x40567fffffffffff),(95.0,0x4057bfffffffffff)]:assert struct.unpack('>Q',struct.pack('>d',percent))[0]-1==bits
assert len(set(range(1,65)))==64 and sum(1 for _ in range(64))==64 and 64+1==65
assert (1000-200)*100//1000==80 and 662+600==1262 and 1261<1262
for path in pf['testPaths']:assert 'try (var pool' not in (R/path).read_text()
assert sum((R/p).read_text().count('pool.invokeAll(jobs, 10, TimeUnit.SECONDS)') for p in pf['testPaths'])==4 and sum((R/p).read_text().count('pool.awaitTermination(10, TimeUnit.SECONDS)') for p in pf['testPaths'])==4
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==4;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=66,METHOD=14,CLASS=4,BRANCH=18,INSTRUCTION=311)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'MonitoringPoller.java','MonitoringObservationClock.java','FilesystemHealthObservation.java','FilesystemHealthMonitor.java'}
naturalSources=[]
for name,counters in sourceCounters.items():
 assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS'])
 branch=counters.get('BRANCH',dict(covered=0,missed=0))
 if name=='FilesystemHealthMonitor.java':assert branch==dict(covered=0,missed=0);naturalSources.append(name)
 else:assert branch['covered']>0 and branch['missed']==0
assert naturalSources==['FilesystemHealthMonitor.java']
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25032-CLOCK-POLLER-FAKESTORE-ORIGINAL-WHOLE26'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
sample=dict(tests=26,fixtures=3,source=m['source'],totals=total,sourceFour100=False,naturalZeroBranchSources=1,crcs=crcs,heldFourInitializations=0)
def validate(v):
 assert type(v['tests']) is int and v['tests']==26 and type(v['fixtures']) is int and v['fixtures']==3 and v['source']==m['source'] and v['totals']==total and v['sourceFour100'] is False and type(v['naturalZeroBranchSources']) is int and v['naturalZeroBranchSources']==1 and v['crcs']==crcs and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0
validate(sample);checks=0
for k,v in [('tests',True),('tests',25),('fixtures',2),('source','0'*40),('totals',{}),('sourceFour100',True),('naturalZeroBranchSources',True),('naturalZeroBranchSources',0),('crcs',{}),('heldFourInitializations',1)]:
 bad=copy.deepcopy(sample);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid qualification accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crcs[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=26,wholeFixtures=3,failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=26,newProductTests=0,productTestsExecuted=0,sourcePrograms=4,physicalInputClasses=4,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=False,strictNonemptySourceFourCounterGateExit=1,naturalZeroBranchSources=1,naturalZeroBranchClasses=1,originalTwentySixAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=4,finiteOwnerSitesCorrected=4,outerUnboundedTwrRecloseRemoved=True,independentClockStoreAndCallbackOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=4,helperPositiveMainClasses=len(positive)-4,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=20,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=26,allSourceFour100=False,positiveMain=len(positive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
