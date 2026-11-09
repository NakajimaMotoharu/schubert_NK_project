"""Independent original two Inbox/MQ supplied recorders whole16, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25408-api-async-jdbc-original-whole16-v1';RAW=B/'evidence/PG25408-api-async-jdbc-original-whole16-v1';O=B/'evidence/PG25412-api-async-jdbc-whole16-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='114a0bcba878303e21053484bf27a036e683a8a24c6ac1a2e647a7a39873403e' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==16 and m['source']=='2c41a3ea9f7de38f92f82275dcd78114abd8edd6' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==2 and pf['sourcePrograms']==2 and pf['expectedTests']==16
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25402-api-async-jdbc-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.api.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalApiAsyncJdbcWhole16',tests='16',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==16 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==16 and app['rawFindings']==21 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent fixed SQL/transaction/resource and five-state publication expectations, no Production expected generator.
assert app['finiteInvokeAllSitesCorrected']==2 and app['finiteOwnerSitesCorrected']==3 and app['fixtureStyleSitesCorrected']==3 and app['oldStyleRawFindings']==24 and app['newStyleRawFindings']==21 and app['styleFindingsRemoved']==3
repository,collector=[(R/path).read_text() for path in pf['testPaths']]
for text,count in [(repository,1),(collector,2)]:assert text.count('@Test')==8 and text.count('.shutdownNow();')==text.count('.awaitTermination(10, TimeUnit.SECONDS)')==count and text.count('.invokeAll(tasks, 10, TimeUnit.SECONDS)')==1
assert collector.count('.get(5, TimeUnit.SECONDS)')==2 and collector.count('release.countDown();')==2 and 'secondEntered.await(100, TimeUnit.MILLISECONDS)' in collector
family=('gauge',{'state'});design=next((p,r) for p,r in pf['approvedDesigns'].items() if Path(p).name.startswith('351_'));raw=subprocess.check_output(['git','show',design[1]['approvedMain']+':'+design[0]]);assert hashlib.sha256(raw).hexdigest()==design[1]['sha256'];catalog={}
for line in raw.decode().splitlines():
 if line.startswith('| `nk_'):
  cells=line.split('|');kind=cells[2].strip()
  if kind in ['counter','gauge','histogram']:
   for n in re.findall(r'`(nk_[a-z_]+)`',cells[1]):catalog[n]=(kind,set(cells[3].strip().split(',')))
assert catalog['nk_async_jobs']==family
sql='SELECT state, COUNT(*) AS job_count FROM schubert.async_jobs GROUP BY state';oracle=R/'evidence/01_PT/018_NK-OPS-001/1627_APIAsyncJobCountSource_単体テスト仕様書.md';assert hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+str(oracle.relative_to(R))])).hexdigest()==sha(oracle) and sql in oracle.read_text() and sql in repository
assert all('"'+v+'"' in repository and '"'+v+'"' in collector for v in ['RECEIVED','PROCESSING','COMPLETED','ERROR','CANCELLED'])
assert all(v in repository for v in ['Connection.TRANSACTION_READ_COMMITTED','borrowed connection must not be mutated or closed','assertEquals(1, timeout)','List.of("RS", "PS")','List.of(rs, ps)','Long.MAX_VALUE','ArithmeticException','READ_ONLY_TRANSACTION_VARIANT = 1','ISOLATION_TRANSACTION_VARIANT = 2','cursor++;','owner + 2L','actual.totalJobs()'])
assert all(v in collector for v in ['assertEquals(15,','Double.isNaN','List.of(close)','cycle.initCause(peer)','peer.initCause(cycle)','assertEquals(222,','i + 2L','assertSame('])
assert sum([1,2,3,4,5])==15 and 7+3==10 and (1<<63)-1+1==1<<63 and len([i+2 for i in range(64)])==64 and min(i+2 for i in range(64))==2 and max(i+2 for i in range(64))==65
oldPrepPath=B/'evidence/PG25404-api-async-jdbc-owner-prepare-v1/manifest.json';oldPrep=load(oldPrepPath);newPrepRef=app['staticManifest'];assert sha(R/newPrepRef['path'])==newPrepRef['sha256'];newPrep=load(R/newPrepRef['path']);oldRules=[v['rule'] for v in oldPrep['reports']['pmd']['findings']];newRules=[v['rule'] for v in newPrep['reports']['pmd']['findings']];assert len(oldRules)==24 and len(newRules)==21 and oldRules.count('AssignmentInOperand')==1 and oldRules.count('AvoidLiteralsInIfCondition')==2 and not set(newRules)&{'AssignmentInOperand','AvoidLiteralsInIfCondition'}
for name in ['pmd.xml','checkstyle.xml']:
 key=str(R/'tools/quality/static'/name);assert oldPrep['toolHashes'][key]==newPrep['toolHashes'][key]
fref=pf['configuredSelectedFormat'];assert sha(R/fref['path'])==fref['sha256'];fmt=load(R/fref['path']);assert fmt['actualExit']==0 and fmt['sourceCount']==14 and fmt['sourceBytesChanged'] is False and fmt['mavenSixModuleGateQualified'] is False and pf['mavenSixModuleFormatQualified'] is False
for path,digest in fmt['sourceHashes'].items():assert sha(R/path)==digest
assert '--skip-reflowing-long-strings' in newPrep['stages']['format']['command']
driverInitializers=set(re.findall(r"Initializing '(org/postgresql/[^']+)'",(S/'class-init.log').read_text()));assert not driverInitializers
normal=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert normal['testsExecuted'] is False and normal['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS';assert all(v is not False for v in [0,True,None,'false'])
sdkPath=B/'evidence/PG25410-api-async-jdbc-sdk-identity-v1/manifest.json';assert sha(sdkPath)=='a8491c65feaf8951c40c8b9802e63c163307cfa6e4e8110cbf9045f61fae81d5';sdk=load(sdkPath);assert sdk['actualExit']==sdk['productTestsExecuted']==0 and sdk['sdkPositiveClasses']==43 and sdk['allObservedSdkCrcMatch'] is True and sdk['sdkIdentityOnlyNotCoverage'] is True and sdk['sdkRuntimeInitializedByThisMetadata'] is False and sdk['producerManifestSha256']==sha(mp)
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==2;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=44,METHOD=6,CLASS=2,BRANCH=24,INSTRUCTION=206)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'AsyncJobCountRepository.java','AsyncJobMetricCollector.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25408-API-ASYNC-JDBC-ORIGINAL-WHOLE16'];positive={};crcs={}
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
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=16,wholeFixtures=len(expected),failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=len(actual),newProductTests=0,productTestsExecuted=0,sourcePrograms=2,physicalInputClasses=2,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=0,originalSixteenAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=2,finiteOwnerSitesCorrected=3,existingFutureGet5SitesRetained=2,existingLatchesAndInnerReleasePreserved=True,independentFixedDomainTimeAndCountOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=2,helperPositiveMainClasses=len(positive)-2,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=21,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,normalFlagTypeNegativeChecks=4,observedSdkClasses=len(vendorPositive),allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkIdentityManifest=dict(path=str(sdkPath.relative_to(R)),sha256=sha(sdkPath)),actualExternalCollectorOrExportActions=0,fixtureStyleSitesCorrected=3,configuredSelectedFormatQualified=True,mavenSixModuleFormatQualified=False,globalFormatHold=True,actualExternalDbDriverOrServiceActions=0,postgresDriverInitializations=0,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=len(actual),allSourceFour100=True,positiveMain=len(positive),sdkIdentityClasses=len(vendorPositive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
