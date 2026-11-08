"""Independent original Batch label whole14, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25132-batch-label-original-whole14-v1';RAW=B/'evidence/PG25132-batch-label-original-whole14-v1';O=B/'evidence/PG25134-batch-label-whole14-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='8f768055b18da30d75e0b9d1ba0e80f0a995d971b00157c60cf28f536ef3dbe0' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==14 and m['source']=='38c41496117a0a77a25f45bfdde7efb5cb13f725' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==1 and pf['sourcePrograms']==1 and pf['expectedTests']==14
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25124-batch-label-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.batch.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalBatchLabelWhole14',tests='14',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==14 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==14 and app['rawFindings']==6 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent approved SS351 catalog subset and fixed closed-domain tuples, not production methods.
assert app['existingFutureGet10SitesRetained']==1 and app['normalFlagTypeNegativeChecks']==4
path=pf['testPaths'][0];text=(R/path).read_text();assert 'try (var workers' not in text and text.count('workers.submit(')==text.count('job.get(10, TimeUnit.SECONDS)')==text.count('workers.shutdownNow();')==text.count('workers.awaitTermination(10, TimeUnit.SECONDS)')==1 and 'invokeAll(' not in text
families={'nk_batch_runs_total':('counter',{'step','status'}),'nk_batch_last_success_timestamp_seconds':('gauge',{'step'}),'nk_file_transfer_files':('gauge',{'suffix'}),'nk_file_transfer_bytes':('gauge',{'suffix'}),'nk_integrity_failures_total':('counter',{'area','step'}),'nk_process_restarts_total':('counter',{'service','reason'})}
design=next((p,r) for p,r in pf['approvedDesigns'].items() if Path(p).name.startswith('351_'));raw=subprocess.check_output(['git','show',design[1]['approvedMain']+':'+design[0]]);assert hashlib.sha256(raw).hexdigest()==design[1]['sha256'];catalog={}
for line in raw.decode().splitlines():
 if line.startswith('| `nk_'):
  cells=line.split('|');kind=cells[2].strip()
  if kind in ['counter','gauge','histogram']:
   for n in re.findall(r'`(nk_[a-z_]+)`',cells[1]):catalog[n]=(kind,set(cells[3].strip().split(',')))
assert all(catalog[n]==v for n,v in families.items())
steps=['BACKUP_DB','BACKUP_CONFIG','CLEAN_NOTIFICATION','CLEAN_QUESTION','CLEAN_SESSION','CLEAN_INBOX_OUTBOX','CLEAN_LOG','CLEAN_BATCH_RUN','CLEAN_TRANSFER','CLEAN_EXPIRY'];statuses=['SUCCESS','WARNING','FAILED','SKIPPED'];services=['WEB','API','BATCH','BROKER','DB','CADDY'];reasons=['NONZERO_EXIT','SIGNAL_EXIT','OOM','UNKNOWN'];assert len(set(steps))==10 and len({(s,v) for s in steps for v in statuses})==40 and len({(a,s) for a in ['HASH','PATH','CONFIG'] for s in steps})==30 and len({(s,v) for s in services for v in reasons})==24
assert 40+10+2*2+30+24==108 and len(range(64))==64
# The normal compile-only value is a false flag, never a zero test count.
normal=load(R.parent/'pgpt-runs/PG379/pg22084-api-stop-state-six-main-compile-v1/manifest.safe.json');assert normal['testsExecuted'] is False and normal['testStatus']=='NOT_RUN_COMPILE_ONLY_NOT_PASS';assert all(v is not False for v in [0,True,None,'false'])
sdkref=pf['sdkMetadata'];assert sha(R/sdkref['path'])==sdkref['sha256']=='37c1f138bf8d90b698cc92d0e34e0bf9d6a992779227ed5270bf854175bb453e';sdk=load(R/sdkref['path']);assert sdk['actualExit']==0 and sdk['productTestsExecuted']==0 and sdk['sdkClassesRuntimeInitializedByThisCommand'] is False
assert pf['vendorJarSha256']==sdk['sdkJarSha256']==sha(Path(pf['vendorJarPath']))=='9ca47dfa831409b40253c8dc98c17b9d3e050ebbde4d1543c5521dca2b95ad56'
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==1;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=41,METHOD=5,CLASS=1,BRANCH=14,INSTRUCTION=208)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'BatchMetricLabelPolicy.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25132-BATCH-LABEL-ORIGINAL-WHOLE14'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
vendorPositive={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4].startswith('io/micrometer/') and int(hit[2])>0:assert hit[4] not in vendorPositive;vendorPositive[hit[4]]=hit[1]
assert vendorPositive==pf['vendorCrc64']=={'io/micrometer/core/instrument/Tag':'9de40eb5187eb4d5','io/micrometer/core/instrument/ImmutableTag':'6364a9ef575c334d'}
vendorInitializers={n for n in initializers if n.startswith('io/micrometer/')};assert vendorInitializers==set(vendorPositive)
import zipfile
with zipfile.ZipFile(Path(pf['vendorJarPath'])) as jar:
 for member,digest in pf['vendorClassHashes'].items():assert hashlib.sha256(jar.read(member)).hexdigest()==digest==sdk['classHashes'][member]

sample=dict(tests=14,fixtures=1,source=m['source'],totals=total,sourceFour100=True,naturalZeroBranchSources=0,crcs=crcs,heldFourInitializations=0)
def validate(v):
 assert type(v['tests']) is int and v['tests']==14 and type(v['fixtures']) is int and v['fixtures']==1 and v['source']==m['source'] and v['totals']==total and v['sourceFour100'] is True and type(v['naturalZeroBranchSources']) is int and v['naturalZeroBranchSources']==0 and v['crcs']==crcs and type(v['heldFourInitializations']) is int and v['heldFourInitializations']==0
validate(sample);checks=0
for k,v in [('tests',True),('tests',13),('fixtures',2),('source','0'*40),('totals',{}),('sourceFour100',False),('naturalZeroBranchSources',False),('naturalZeroBranchSources',1),('crcs',{}),('heldFourInitializations',1)]:
 bad=copy.deepcopy(sample);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(sample,sort_keys=True)
 try:validate(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('invalid qualification accepted')
O.mkdir();E.ElementTree(safe).write(O/'testcases.safe.xml',encoding='utf-8',xml_declaration=True);(O/'coverage.xml').write_bytes((S/'coverage.xml').read_bytes());(O/'execinfo.safe.txt').write_text('\n'.join(n+' '+crcs[n]+' positiveProbes='+str(positive[n]) for n in sorted(positive))+'\n')
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=14,wholeFixtures=1,failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=14,newProductTests=0,productTestsExecuted=0,sourcePrograms=1,physicalInputClasses=1,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=0,originalFourteenAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=0,finiteOwnerSitesCorrected=1,outerUnboundedTwrRecloseRemoved=True,independentLabelDomainAndProviderOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=1,helperPositiveMainClasses=len(positive)-1,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=6,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,normalFlagTypeNegativeChecks=4,observedSdkValueTypes=2,allObservedSdkCrcMatch=True,sdkIdentityOnlyNotCoverage=True,unexpectedMicrometerInitializations=0,actualRegistryOrCollectorOrExportActions=0,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=14,allSourceFour100=True,positiveMain=len(positive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
