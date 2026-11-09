"""Independent original Web media byte whole8: immutable source, literal catalog/oracle, CRC and measured counters."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25528-web-media-bytes-original-whole8-v1';RAW=B/'evidence/PG25528-web-media-bytes-original-whole8-v1';O=B/'evidence/PG25532-web-media-bytes-whole8-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='c8b17962e77c7fc9aaf0d5c0e908634eff32963a418b9993a791545e833aa9f8' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==8 and m['source']=='5dbdc47b9d9f2dcc44e9df3acb686bd36a6dbf73' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==2 and pf['sourcePrograms']==1 and pf['expectedTests']==8
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25522-web-media-bytes-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.web.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalWebMediaBytesWhole8',tests='8',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==8 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==8 and app['rawFindings']==6 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent fixed SS351 counter/SS333 media table and supplied-byte fixture arithmetic.
assert app['finiteInvokeAllSitesCorrected']==app['finiteOwnerSitesCorrected']==1
text=(R/pf['testPaths'][0]).read_text();assert len(pf['testPaths'])==1 and text.count('@Test')==8 and text.count('.shutdownNow();')==text.count('.awaitTermination(10, TimeUnit.SECONDS)')==text.count('.invokeAll(tasks, 10, TimeUnit.SECONDS)')==text.count('.get(5, TimeUnit.SECONDS)')==1
for prefix in ['351_','333_']:
 design=next((p,ref) for p,ref in pf['approvedDesigns'].items() if Path(p).name.startswith(prefix));raw=subprocess.check_output(['git','show',design[1]['approvedMain']+':'+design[0]]);assert hashlib.sha256(raw).hexdigest()==design[1]['sha256']
 if prefix=='351_':
  rows=[line.split('|') for line in raw.decode().splitlines() if line.startswith('| `nk_media_bytes_total`')];assert len(rows)==1 and rows[0][2].strip()=='counter' and set(rows[0][3].strip().split(','))=={'media_type','mode','status'}
 else:
  for name,code in [('Audio','IF-009'),('Video','IF-012'),('Music','IF-016')]:assert any(name in line and code in line for line in raw.decode().splitlines() if line.startswith('|'))
expectedBytes={}
for index in range(64):
 key=(['AUDIO','VIDEO','MUSIC'][index%3],['INLINE','DOWNLOAD','RANGE'][(index//3)%3],[200,206,416,503][(index//9)%4]);expectedBytes[key]=expectedBytes.get(key,0)+index+1
assert len(expectedBytes)==36 and sum(expectedBytes.values())==2080 and expectedBytes[('AUDIO','INLINE',200)]==38 and sorted(expectedBytes.values())==sorted([2*k+36 if k<=28 else k for k in range(1,37)]) and 36*3+1==109
assert float(2**63-1)==9.223372036854776E18 and all(v in text for v in ['assertEquals(109, registry.increments.get())','assertEquals(64, registry.increments.get())','expected.merge(type.name()','bytes, Long::sum)','result.get(5, TimeUnit.SECONDS)','assertEquals(after ? 3 : 0','assertEquals(2, registry.registrations.get())','assertEquals(1, registry.getMeters().size())','new AtomicInteger(7)','assertSame(','assertArrayEquals','Long.MIN_VALUE','Long.MAX_VALUE'])
sdkPath=B/'evidence/PG25530-web-media-bytes-sdk-identity-v1/manifest.json';assert sha(sdkPath)=='005fc0185af226120e230b8889a1feb0f8d6edc4437314bf76d773d56ae4a521';sdk=load(sdkPath);assert sdk['actualExit']==sdk['productTestsExecuted']==0 and sdk['sdkPositiveClasses']==50 and sdk['allObservedSdkCrcMatch'] is True and sdk['sdkIdentityOnlyNotCoverage'] is True and sdk['sdkRuntimeInitializedByThisMetadata'] is False and sdk['producerManifestSha256']==sha(mp)
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==2;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=42,METHOD=7,CLASS=2,BRANCH=18,INSTRUCTION=240)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'MediaBytesMetricRecorder.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
naturalClassZero=sum(sum(c.get('BRANCH',dict(covered=0,missed=0)).values())==0 for c in perClass.values());naturalSourceZero=sum(sum(c.get('BRANCH',dict(covered=0,missed=0)).values())==0 for c in sourceCounters.values());assert naturalSourceZero==0

for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25528-WEB-MEDIA-BYTES-ORIGINAL-WHOLE8'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
vendorPositive={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4].startswith('io/micrometer/') and int(hit[2])>0:assert hit[4] not in vendorPositive;vendorPositive[hit[4]]=hit[1]
assert vendorPositive=={n:r['crc64'] for n,r in sdk['classRows'].items()};assert {n.split('$$Lambda+',1)[0] for n in initializers if n.startswith('io/micrometer/')}==set(sdk['normalizedSdkInitializerNames'])
sample=dict(tests=8,fixtures=1,source=m['source'],totals=total,sourceFour100=True,naturalZeroBranchSources=0,crcs=crcs,heldFourInitializations=0)
def validate(v):
 assert type(v['tests']) is int and v['tests']==8 and type(v['fixtures']) is int and v['fixtures']==1 and v['source']==m['source'] and v['totals']==total and v['sourceFour100'] is True and type(v['naturalZeroBranchSources']) is int and v['naturalZeroBranchSources']==0 and v['crcs']==crcs and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0
validate(sample);checks=0
for k,v in [('tests',True),('tests',23),('fixtures',2),('source','0'*40),('totals',{}),('sourceFour100',False),('naturalZeroBranchSources',False),('naturalZeroBranchSources',1),('crcs',{}),('heldFourInitializations',1)]:
 bad=copy.deepcopy(sample);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid qualification accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crcs[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=8,wholeFixtures=len(expected),failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=len(actual),newProductTests=0,productTestsExecuted=0,sourcePrograms=1,physicalInputClasses=2,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=naturalClassZero,originalEightAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=1,finiteOwnerSitesCorrected=1,existingFutureGet5SitesRetained=1,existingPrecomputedByteOracleAndRegistryOwnershipPreserved=True,independentFixedDomainTimeAndCountOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=2,helperPositiveMainClasses=len(positive)-2,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=6,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,normalFlagTypeNegativeChecks=0,observedSdkClasses=len(vendorPositive),allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkIdentityManifest=dict(path=str(sdkPath.relative_to(R)),sha256=sha(sdkPath)),actualExternalCollectorOrExportActions=0,actualHttpOrMediaDeliveryActions=0,configuredSelectedFormatQualified=True,mavenSixModuleFormatQualified=False,globalFormatHold=True,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=len(actual),allSourceFour100=True,positiveMain=len(positive),sdkIdentityClasses=len(vendorPositive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
