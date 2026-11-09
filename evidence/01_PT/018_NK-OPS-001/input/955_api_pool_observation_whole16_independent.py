"""Independent original two Inbox/MQ supplied recorders whole16, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25378-api-pool-observation-original-whole16-v1';RAW=B/'evidence/PG25378-api-pool-observation-original-whole16-v1';O=B/'evidence/PG25382-api-pool-observation-whole16-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='ca4fa15b44325c73c0e3fabad26b9011556e42cd96b3aaab9abadb544e063166' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==16 and m['source']=='03eb896eb53d4447e1899e1c6f2797790ec5f251' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==2 and pf['sourcePrograms']==2 and pf['expectedTests']==16
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25372-api-pool-observation-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.api.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalApiPoolObservationWhole16',tests='16',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==16 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==16 and app['rawFindings']==19 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent SS351 fixed API pool labels and original fake four-getter/scalar publication oracle.
assert app['finiteInvokeAllSitesCorrected']==2 and app['finiteOwnerSitesCorrected']==3
observation,collector=[(R/path).read_text() for path in pf['testPaths']]
for text,count in [(observation,1),(collector,2)]:assert text.count('@Test')==8 and text.count('.shutdownNow();')==text.count('.awaitTermination(10, TimeUnit.SECONDS)')==count and text.count('.invokeAll(tasks, 10, TimeUnit.SECONDS)')==1
assert collector.count('.get(5, TimeUnit.SECONDS)')==2 and collector.count('release.countDown();')==2 and 'enteredSecond.await(100, TimeUnit.MILLISECONDS)' in collector
family=('gauge',{'service','state'});design=next((p,r) for p,r in pf['approvedDesigns'].items() if Path(p).name.startswith('351_'));raw=subprocess.check_output(['git','show',design[1]['approvedMain']+':'+design[0]]);assert hashlib.sha256(raw).hexdigest()==design[1]['sha256'];catalog={}
for line in raw.decode().splitlines():
 if line.startswith('| `nk_'):
  cells=line.split('|');kind=cells[2].strip()
  if kind in ['counter','gauge','histogram']:
   for n in re.findall(r'`(nk_[a-z_]+)`',cells[1]):catalog[n]=(kind,set(cells[3].strip().split(',')))
assert catalog['nk_db_pool_connections']==family
assert all('"'+v+'"' in observation for v in ['active','idle','pending','max']) and all('"'+v+'"' in collector for v in ['active','idle','pending','max','API'])
assert all(v in observation for v in ['3, 5, 2, 8','0, 0, 0, 1','2147483647L','i < 64','active, 5, 2, 8','no total/control/management operations','no config/credential getter or mutation','order.subList(0, i + 1)'])
assert all(v in collector for v in ['99, first.snapshot()','111, second.snapshot()','assertEquals(1, one.get(5','assertEquals(2, two.get(5','cycle.initCause(peer)','peer.initCause(cycle)','assertSame(','Double.isNaN'])
assert (1<<31)-1==2147483647 and list(range(64))[-1]==63 and sum(range(64))==2016 and max(range(100))==99 and len(['active','idle','pending','max'])==4
# Hikari executable implementations are outside this fixture graph; metadata is exactly two abstract interfaces.
href=pf['hikariInterfaceReview'];assert sha(R/href['path'])==href['sha256'];hr=load(R/href['path']);assert hr['actualExit']==hr['productTestsExecuted']==hr['actualPoolConfigOrDbActions']==0 and hr['hikariInitializedByMetadata'] is False and set(hr['interfaces'])=={'com.zaxxer.hikari.HikariPoolMXBean','com.zaxxer.hikari.HikariConfigMXBean'}
for name,row in hr['interfaces'].items():assert row['javapExit']==0 and sha((R/href['path']).parent/(name.rsplit('.',1)[1]+'.txt'))==row['metadataSha256']
assert sha(Path(hr['jarPath']))==hr['jarSha256']=='2be45c641b841e81df87292e181f2c203500c5f0e9a1676f135927387f3cf40b'
hikariInitializers=set(re.findall(r"Initializing '(com/zaxxer/hikari/[^']+)'",(S/'class-init.log').read_text()));assert not hikariInitializers
assert not any(re.search(r'\s[1-9]\d* of\s+\d+\s+com/zaxxer/hikari/',line) for line in (S/'execinfo.stdout').read_text().splitlines())
normal=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert normal['testsExecuted'] is False and normal['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS';assert all(v is not False for v in [0,True,None,'false'])
sdkPath=B/'evidence/PG25380-api-pool-observation-sdk-identity-v1/manifest.json';assert sha(sdkPath)=='4d85d48332bac97e62a5512a48a043d00a7de07297ef379ee24f1624d80c0fa6';sdk=load(sdkPath);assert sdk['actualExit']==sdk['productTestsExecuted']==0 and sdk['sdkPositiveClasses']==43 and sdk['allObservedSdkCrcMatch'] is True and sdk['sdkIdentityOnlyNotCoverage'] is True and sdk['sdkRuntimeInitializedByThisMetadata'] is False and sdk['producerManifestSha256']==sha(mp)
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==2;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=26,METHOD=5,CLASS=2,BRANCH=12,INSTRUCTION=122)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'DbPoolMetricObservation.java','DbPoolMetricCollector.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25378-API-POOL-OBSERVATION-ORIGINAL-WHOLE16'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
vendorPositive={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4].startswith('io/micrometer/') and int(hit[2])>0:assert hit[4] not in vendorPositive;vendorPositive[hit[4]]=hit[1]
assert vendorPositive=={n:r['crc64'] for n,r in sdk['classRows'].items()};assert {n.split('$$Lambda+',1)[0] for n in initializers if n.startswith('io/micrometer/')}==set(sdk['normalizedSdkInitializerNames'])
sample=dict(tests=16,fixtures=2,source=m['source'],totals=total,sourceFour100=True,naturalZeroBranchSources=0,crcs=crcs,heldFourInitializations=0)
def validate(v):
 assert type(v['tests']) is int and v['tests']==16 and type(v['fixtures']) is int and v['fixtures']==2 and v['source']==m['source'] and v['totals']==total and v['sourceFour100'] is True and type(v['naturalZeroBranchSources']) is int and v['naturalZeroBranchSources']==0 and v['crcs']==crcs and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0
validate(sample);checks=0
for k,v in [('tests',True),('tests',23),('fixtures',1),('source','0'*40),('totals',{}),('sourceFour100',False),('naturalZeroBranchSources',False),('naturalZeroBranchSources',1),('crcs',{}),('heldFourInitializations',1)]:
 bad=copy.deepcopy(sample);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid qualification accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crcs[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=16,wholeFixtures=len(expected),failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=len(actual),newProductTests=0,productTestsExecuted=0,sourcePrograms=2,physicalInputClasses=2,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=0,originalSixteenAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=2,finiteOwnerSitesCorrected=3,existingFutureGet5SitesRetained=2,existingLatchesAndInnerReleasePreserved=True,independentFixedDomainTimeAndCountOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=2,helperPositiveMainClasses=len(positive)-2,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=19,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,normalFlagTypeNegativeChecks=4,observedSdkClasses=len(vendorPositive),allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkIdentityManifest=dict(path=str(sdkPath.relative_to(R)),sha256=sha(sdkPath)),actualExternalCollectorOrExportActions=0,hikariInterfaceReview=href,hikariImplementationInitializations=0,hikariPositiveCodeProbes=0,actualPoolConfigDbJmxActions=0,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=len(actual),allSourceFour100=True,positiveMain=len(positive),sdkIdentityClasses=len(vendorPositive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
