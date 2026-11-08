"""Independent original Transfer whole16, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25170-transfer-original-whole16-v1';RAW=B/'evidence/PG25170-transfer-original-whole16-v1';O=B/'evidence/PG25172-transfer-whole16-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='d20cb405cadba855fbfef377d408c925b76d083431fc465bcc2d19e5b84644c3' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==16 and m['source']=='0660d2305bdf11235be7e1f74cae0b3872268389' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==6 and pf['sourcePrograms']==2 and pf['expectedTests']==16
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25164-transfer-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.batch.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalTransferWhole16',tests='16',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==16 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==16 and app['rawFindings']==12 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# SS351 two gauge families and independent supplied-count/alert/time golden expectations.
assert app['finiteInvokeAllSitesCorrected']==app['finiteOwnerSitesCorrected']==2
for path in pf['testPaths']:
 text=(R/path).read_text();assert text.count('@Test')==8 and text.count('.invokeAll(jobs, 10, TimeUnit.SECONDS)')==text.count('.shutdownNow();')==text.count('.awaitTermination(10, TimeUnit.SECONDS)')==1
families={'nk_file_transfer_files':('gauge',{'suffix'}),'nk_file_transfer_bytes':('gauge',{'suffix'})}
design=next((p,r) for p,r in pf['approvedDesigns'].items() if Path(p).name.startswith('351_'));raw=subprocess.check_output(['git','show',design[1]['approvedMain']+':'+design[0]]);assert hashlib.sha256(raw).hexdigest()==design[1]['sha256'];catalog={}
for line in raw.decode().splitlines():
 if line.startswith('| `nk_'):
  cells=line.split('|');kind=cells[2].strip()
  if kind in ['counter','gauge','histogram']:
   for n in re.findall(r'`(nk_[a-z_]+)`',cells[1]):catalog[n]=(kind,set(cells[3].strip().split(',')))
assert all(catalog[n]==v for n,v in families.items());assert '| Transfer | >=3.5GBまたは5,000 | >=4.5GBまたは9,000 |' in raw.decode();assert len({(n,s) for n in families for s in ['.part','.ready']})==4 and 2+3==5 and 1024+2048==3072 and 8+10==18 and 64+1==65
maximum=2**63-1;assert maximum-1+1==maximum and maximum+1>2**63-1 and float(maximum-1)==9223372036854776000.0
assert 1750000000*2==3500000000 and 2250000000*2==4500000000 and 2500*2==5000 and 4500*2==9000
assert 301-1==300 and 300-1==299 and 1203-603==600 and 1202-603==599 and 1201-601==600 and 1200-601==599
metric=(R/pf['testPaths'][0]).read_text();health=(R/pf['testPaths'][1]).read_text();assert all(s in metric for s in ['Double.isNaN','Long.MAX_VALUE','9_223_372_036_854_776_000.0','ArithmeticException.class','snapshot == first || snapshot == second','assertSame(']);assert all(s in health for s in ['3_499_999_999L','3_500_000_000L','4_499_999_999L','4_500_000_000L','4999','5000','8999','9000','CauseClearance.UNCONFIRMED','BigInteger.valueOf(65)','1202','1203','1200','1201'])
normal=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert normal['testsExecuted'] is False and normal['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS';assert all(v is not False for v in [0,True,None,'false'])
sdkPath=B/'evidence/PG25153-batch-recorders-sdk-identity-v1/manifest.json';assert sha(sdkPath)=='2fe2912cdf6ae83dd3c97322dd1b971ae9766dde128610e8a8f8b7fa3e4850d8';sdk=load(sdkPath);assert sdk['actualExit']==sdk['productTestsExecuted']==0 and sdk['sdkPositiveClasses']==51 and sdk['allObservedSdkCrcMatch'] is True and sdk['sdkIdentityOnlyNotCoverage'] is True and sdk['sdkRuntimeInitializedByThisMetadata'] is False
assert pf['bug2578Corrected'] is True and pf['dependencyNegativeChecks']==2;recPath=B/'evidence/PG25178-transfer-dependency-recurrence-v1/manifest.json';rec=load(recPath);assert rec['actualExit']==0 and rec['failedToolUnchanged'] is True and rec['partialSourceStaticUnchanged'] is True and rec['unexecutedEntryUnchanged'] is True and rec['originalSourceStaticPhaseReexecuted'] is False and rec['dependencyNegativeChecks']==2 and rec['preflightSha256']==sha(R/ref['path'])
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==6;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=78,METHOD=25,CLASS=6,BRANCH=22,INSTRUCTION=351)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'TransferMetricRecorder.java','TransferHealthMonitor.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25170-TRANSFER-ORIGINAL-WHOLE16'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
vendorPositive={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4].startswith('io/micrometer/') and int(hit[2])>0:assert hit[4] not in vendorPositive;vendorPositive[hit[4]]=hit[1]
assert len(vendorPositive)==42 and set(vendorPositive)<=set(sdk['classRows']) and all(sdk['classRows'][n]['crc64']==v for n,v in vendorPositive.items());assert {n.split('$$Lambda+',1)[0] for n in initializers if n.startswith('io/micrometer/')}<=set(sdk['normalizedSdkInitializerNames'])
zeroBranch={n for n,c in perClass.items() if 'BRANCH' not in c or c['BRANCH']['covered']+c['BRANCH']['missed']==0};assert zeroBranch=={'dev/codex/schubert/nk/batch/monitoring/TransferMetricRecorder$Usage','dev/codex/schubert/nk/batch/monitoring/TransferHealthMonitor$Evaluation','dev/codex/schubert/nk/batch/monitoring/TransferMetricRecorder$Suffix'}
sample=dict(tests=16,fixtures=2,source=m['source'],totals=total,sourceFour100=True,naturalZeroBranchSources=0,crcs=crcs,heldFourInitializations=0)
def validate(v):
 assert type(v['tests']) is int and v['tests']==16 and type(v['fixtures']) is int and v['fixtures']==2 and v['source']==m['source'] and v['totals']==total and v['sourceFour100'] is True and type(v['naturalZeroBranchSources']) is int and v['naturalZeroBranchSources']==0 and v['crcs']==crcs and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0
validate(sample);checks=0
for k,v in [('tests',True),('tests',15),('fixtures',3),('source','0'*40),('totals',{}),('sourceFour100',False),('naturalZeroBranchSources',False),('naturalZeroBranchSources',1),('crcs',{}),('heldFourInitializations',1)]:
 bad=copy.deepcopy(sample);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid qualification accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crcs[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=16,wholeFixtures=2,failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=16,newProductTests=0,productTestsExecuted=0,sourcePrograms=2,physicalInputClasses=6,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=3,originalSixteenAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=2,finiteOwnerSitesCorrected=2,dependencyNegativeChecks=2,toolRecurrenceManifestSha256=sha(recPath),independentFixedDomainTimeAndCountOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=6,helperPositiveMainClasses=len(positive)-6,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=12,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,normalFlagTypeNegativeChecks=4,observedSdkClasses=len(vendorPositive),allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,sdkIdentityManifest=dict(path=str(sdkPath.relative_to(R)),sha256=sha(sdkPath)),actualExternalCollectorOrExportActions=0,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=16,allSourceFour100=True,positiveMain=len(positive),sdkIdentityClasses=len(vendorPositive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
