"""Independent original three API supplied recorders whole24, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25328-api-pool-outbox-original-whole24-v1';RAW=B/'evidence/PG25328-api-pool-outbox-original-whole24-v1';O=B/'evidence/PG25332-api-pool-outbox-whole24-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='ccc3936b7d67d14b0331b2d5e7aafdd0062318304eee11861fcc109034bf4f7b' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==24 and m['source']=='28e48089eea6447378490c43d930c9b659908744' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==8 and pf['sourcePrograms']==3 and pf['expectedTests']==24
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25322-api-pool-outbox-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.api.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalApiPoolOutboxWhole24',tests='24',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==24 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==24 and app['rawFindings']==21 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent approved SS351 labels and scalar/duration/record contracts; no production expected generator.
assert app['finiteInvokeAllSitesCorrected']==app['finiteOwnerSitesCorrected']==3
texts=[(R/path).read_text() for path in pf['testPaths']]
for text in texts:assert text.count('@Test')==8 and text.count('.shutdownNow();')==text.count('.awaitTermination(10, TimeUnit.SECONDS)')==1 and text.count('.invokeAll(tasks, 10, TimeUnit.SECONDS)')==1
families={'nk_db_pool_connections':('gauge',{'service','state'}),'nk_outbox_rows':('gauge',{'store','status'}),'nk_outbox_oldest_seconds':('gauge',{'store','status'})}
design=next((p,r) for p,r in pf['approvedDesigns'].items() if Path(p).name.startswith('351_'));raw=subprocess.check_output(['git','show',design[1]['approvedMain']+':'+design[0]]);assert hashlib.sha256(raw).hexdigest()==design[1]['sha256'];catalog={}
for line in raw.decode().splitlines():
 if line.startswith('| `nk_'):
  cells=line.split('|');kind=cells[2].strip()
  if kind in ['counter','gauge','histogram']:
   for n in re.findall(r'`(nk_[a-z_]+)`',cells[1]):catalog[n]=(kind,set(cells[3].strip().split(',')))
assert all(catalog[n]==v for n,v in families.items())
pool,age,rows=texts;assert all('"'+n+'"' in pool for n in ['active','idle','pending','max','API'])
assert all('"'+n+'"' in age and '"'+n+'"' in rows for n in ['PENDING','SENT','ERROR','API'])
assert all(x in pool for x in ['new Counts(3, 5, 2, 8)','return actual == first || actual == second','assertEquals(999,','assertEquals(7,','Long.MAX_VALUE','0x1.0p63','Double.isNaN'])
assert all(x in age for x in ['1.5','0.000000001','300','return actual == one || actual == two','3045','Ages[pending=PT3S, sent=PT5S, error=PT7S]','Long.MIN_VALUE','999_999_999','0x1.0p63','Double.isNaN'])
assert all(x in rows for x in ['new Counts(3, 5, 2)','return actual == one || actual == two','assertEquals(999,','assertEquals(7,','Long.MAX_VALUE','0x1.0p63','Double.isNaN'])
assert 1500/1000==1.5 and 1/1000000000==0.000000001 and (3*31+5)*31+7==3045 and float((1<<63)-1)==float.fromhex('0x1.0p63')
assert max(i for i in range(1000) if i%2==1)==999 and len([i for i in range(64) if i%2==0])==32 and len([i for i in range(64) if i%2])==32
normal=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert normal['testsExecuted'] is False and normal['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS';assert all(v is not False for v in [0,True,None,'false'])
sdkPath=B/'evidence/PG25330-api-pool-outbox-sdk-identity-v1/manifest.json';assert sha(sdkPath)=='d91fc34792b15b3aa4c6d274466806c93a666ba09ef5bb53c84fed0d903f93b9';sdk=load(sdkPath);assert sdk['actualExit']==sdk['productTestsExecuted']==0 and sdk['sdkPositiveClasses']==43 and sdk['allObservedSdkCrcMatch'] is True and sdk['sdkIdentityOnlyNotCoverage'] is True and sdk['sdkRuntimeInitializedByThisMetadata'] is False and sdk['producerManifestSha256']==sha(mp)
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==8;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=120,METHOD=34,CLASS=8,BRANCH=69,INSTRUCTION=645)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'DbPoolMetricRecorder.java','OutboxAgeMetricRecorder.java','OutboxRowsMetricRecorder.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25328-API-POOL-OUTBOX-ORIGINAL-WHOLE24'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
vendorPositive={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4].startswith('io/micrometer/') and int(hit[2])>0:assert hit[4] not in vendorPositive;vendorPositive[hit[4]]=hit[1]
assert vendorPositive=={n:r['crc64'] for n,r in sdk['classRows'].items()};assert {n.split('$$Lambda+',1)[0] for n in initializers if n.startswith('io/micrometer/')}==set(sdk['normalizedSdkInitializerNames'])
sample=dict(tests=24,fixtures=3,source=m['source'],totals=total,sourceFour100=True,naturalZeroBranchSources=0,crcs=crcs,heldFourInitializations=0)
def validate(v):
 assert type(v['tests']) is int and v['tests']==24 and type(v['fixtures']) is int and v['fixtures']==3 and v['source']==m['source'] and v['totals']==total and v['sourceFour100'] is True and type(v['naturalZeroBranchSources']) is int and v['naturalZeroBranchSources']==0 and v['crcs']==crcs and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0
validate(sample);checks=0
for k,v in [('tests',True),('tests',23),('fixtures',2),('source','0'*40),('totals',{}),('sourceFour100',False),('naturalZeroBranchSources',False),('naturalZeroBranchSources',1),('crcs',{}),('heldFourInitializations',1)]:
 bad=copy.deepcopy(sample);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid qualification accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crcs[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=24,wholeFixtures=3,failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=24,newProductTests=0,productTestsExecuted=0,sourcePrograms=3,physicalInputClasses=8,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=sum(not any(v.get("type")=="BRANCH" and int(v.get("covered"))+int(v.get("missed"))>0 for v in c.findall("counter")) for c in classes.values()),originalTwentyFourAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=3,finiteOwnerSitesCorrected=3,independentFixedDomainTimeAndCountOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=8,helperPositiveMainClasses=len(positive)-8,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=21,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,normalFlagTypeNegativeChecks=4,observedSdkClasses=len(vendorPositive),allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkIdentityManifest=dict(path=str(sdkPath.relative_to(R)),sha256=sha(sdkPath)),actualExternalCollectorOrExportActions=0,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=24,allSourceFour100=True,positiveMain=len(positive),sdkIdentityClasses=len(vendorPositive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
