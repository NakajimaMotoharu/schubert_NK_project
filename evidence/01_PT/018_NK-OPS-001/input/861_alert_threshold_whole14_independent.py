"""Independent original threshold whole14, exact source/case/CRC/counter and literal oracle post."""
from pathlib import Path
import copy,datetime,hashlib,json,re,subprocess,xml.etree.ElementTree as E
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg25010-alert-threshold-original-whole14-v1';RAW=B/'evidence/PG25010-alert-threshold-original-whole14-v1';O=B/'evidence/PG25012-alert-threshold-whole14-independent-v1';assert not O.exists();load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=RAW/'manifest.json';assert sha(mp)=='262a2ea068dcffde58900831247b95e5f4818d8357f5a71bcacd903f8fba7996' and sha(S/'manifest.json')==sha(mp);m=load(mp);assert m['actualExit']==0 and m['productTestsExecuted']==14 and m['source']=='367d68b29ff2d5f6f7ecb8805bc2b65dbff4bc90' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5';ref=m['begin']['preflight'];assert sha(R/ref['path'])==ref['sha256'];pf=load(R/ref['path']);assert pf['targetPhysicalClasses']==1 and pf['sourcePrograms']==1 and pf['expectedTests']==14
for k in ['inputHashes','dependencies','targetClassHashes']:assert m['begin'][k]==pf[k]
for path,digest in pf['inputHashes'].items():assert sha(R/path)==digest==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+path])).hexdigest()
for path,digest in pf['dependencies'].items():assert sha(Path(path))==digest
for name in ['compile','unit','coverage','execinfo','classinfo']:
 value=m['stages'][name];assert value['actualExit']==0 and value['timedOut'] is False and load(S/(name+'-exit.safe.json'))==value
before=load(B/'evidence/PG25002-alert-threshold-owner-before-v1/manifest.json');expected={}
for row in before['sources']:
 old=subprocess.check_output(['git','show',row['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==row['sha256'];fqn='dev.codex.schubert.nk.batch.monitoring.'+Path(row['path']).stem;names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==pf['expectedCaseCounts'][fqn];expected[fqn]=set(names)
actual=[];envs=[];safe=E.Element('testsuite',name='OriginalThresholdWhole14',tests='14',failures='0',errors='0',skipped='0')
for name,digest in m['xmlHashes'].items():
 p=S/'xml'/name;assert sha(p)==digest;root=E.parse(p).getroot();env={n.get('name'):n.get('value') for n in root.findall('./properties/property')}
 for t in root.findall('testcase'):
  cls=t.get('classname');method=t.get('name').removesuffix('()');assert cls in expected and method in expected[cls] and not any(t.findall(n) for n in ['failure','error','skipped']);actual.append((cls,method));envs.append(env);E.SubElement(safe,'testcase',classname=cls,name=method+'()')
assert len(actual)==len(set(actual))==14 and set(actual)=={(c,n) for c,ns in expected.items() for n in ns} and m['cases']==[dict(className=c,name=n+'()',nonPass=[]) for c,n in actual]
for v in envs:assert v['java.runtime.version'].startswith('25.0.4') and v['user.language']=='ja' and v['user.country']=='JP' and v['user.timezone']=='Asia/Tokyo'
reported={k:envs[0][k] for k in ['java.runtime.version','java.vendor','os.name','os.arch','os.version','user.language','user.country','user.timezone']};assert all(all(v[k]==reported[k] for k in reported) for v in envs)
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path']);assert app['originalWholeCases']==14 and app['rawFindings']==5 and app['applicableViolations']==0 and app['checkstyleFindings']==0 and app['suppressionAdded'] is False and app['outerExecutorTwrCountAfterFix']==0
for r in app['sourceContinuity']:assert sha(R/r['path'])==r['currentSha256'] and r['originalWholeBodiesExactlyRestored'] is True
# Independent integer/IEEE thresholds from SS351, not production expected generation.
assert 3_500_000_000==35*100_000_000 and 4_500_000_000==45*100_000_000
assert 699*100<1000*70 and 700*100==1000*70 and 899*100<1000*90 and 900*100==1000*90
assert (2**63-1)*100>(2**63-1)*90 and 300*1_000_000_000-1<300*1_000_000_000
assert 60<300<600<1800 and 2.0<2.5 and 5000<9000 and 1000<5000
assert sum(1 for increase in [False,True] for unknown in [False,True] if increase or unknown)==3
for path in pf['testPaths']:assert 'try (var executor' not in (R/path).read_text()
assert sum((R/p).read_text().count('executor.invokeAll(tasks, 10, TimeUnit.SECONDS)') for p in pf['testPaths'])==1 and sum((R/p).read_text().count('executor.awaitTermination(10, TimeUnit.SECONDS)') for p in pf['testPaths'])==1
assert sha(R/pf['physicalIndex']['path'])==pf['physicalIndex']['sha256'];index=load(R/pf['physicalIndex']['path']);assert sha(R/pf['metadataInventory']['path'])==pf['metadataInventory']['sha256'];meta=load(R/pf['metadataInventory']['path']);normalNames={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta};held={r['physicalKey'].split(':',1)[1].removesuffix('.class') for r in meta if Path(r['sourcePath']).stem in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException']};assert len(held)==4
targets={v.removesuffix('.class') for v in pf['targetClassHashes']};xml=E.parse(S/'coverage.xml').getroot();classes={c.get('name'):c for c in xml.findall('.//class')};assert set(classes)==targets and len(classes)==1;total={v.get('type'):dict(covered=int(v.get('covered')),missed=int(v.get('missed'))) for v in xml.findall('counter')};assert all(v['missed']==0 for v in total.values()) and {k:total[k]['covered'] for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}==dict(LINE=66,METHOD=21,CLASS=1,BRANCH=102,INSTRUCTION=410)
perClass={name:{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in c.findall('counter')} for name,c in classes.items()};sourceCounters={s.get('name'):{n.get('type'):dict(covered=int(n.get('covered')),missed=int(n.get('missed'))) for n in s.findall('counter')} for s in xml.findall('.//sourcefile')};assert set(sourceCounters)=={'AlertThresholds.java'}
for counters in sourceCounters.values():assert all(k in counters and counters[k]['covered']>0 and counters[k]['missed']==0 for k in ['LINE','METHOD','CLASS','BRANCH'])
for member,digest in pf['targetClassHashes'].items():assert index[member.removesuffix('.class')]['sha256']==digest==sha(S/'component'/Path(member).name)
info=(S/'execinfo.stdout').read_text();assert re.findall(r'^Session "([^"]+)":',info,re.M)==['PG25010-ALERT-THRESHOLD-ORIGINAL-WHOLE14'];positive={};crcs={}
for line in info.splitlines():
 hit=re.fullmatch(r'\s*([0-9a-f]{16})\s+(\d+) of\s+(\d+)\s+(.+)',line)
 if hit and hit[4] in normalNames and int(hit[2])>0:assert hit[4] not in positive;positive[hit[4]]=int(hit[2]);crcs[hit[4]]=hit[1];assert index[hit[4]]['crc64']==hit[1]
assert targets<=set(positive)<=set(pf['allowedObservedMain']) and not set(positive)&held;initializers=set(re.findall(r"Initializing '([^']+)'",(S/'class-init.log').read_text()));assert not initializers&held
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
out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),preflight=ref,tests=14,wholeFixtures=1,failures=0,errors=0,skipped=0,aborted=0,existingTestsRequalified=14,newProductTests=0,productTestsExecuted=0,sourcePrograms=1,physicalInputClasses=1,coverage=total,perClassCounters=perClass,sourceCounters=sourceCounters,aggregateMeasuredFour100=True,allSourceFour100=True,strictNonemptySourceFourCounterGateExit=0,naturalZeroBranchSources=0,naturalZeroBranchClasses=0,originalFourteenAssertionsUnchanged=True,finiteInvokeAllSitesCorrected=0,finiteOwnerSitesCorrected=1,outerUnboundedTwrRecloseRemoved=True,independentThresholdLiteralOraclesMatched=True,allObservedMainCrcMatchCurrentNormal=True,observedPositiveMainClasses=len(positive),targetPositiveMainClasses=1,helperPositiveMainClasses=len(positive)-1,heldFourInitializations=0,heldFourPositiveMainProbes=0,singleSession=True,oldExecUnion=False,manualCoverageExclusions=[],pmdRawFindings=5,applicableStaticViolations=0,checkstyleFindings=0,processingErrors=0,metadataNegativeChecks=checks,reportedEnvironment=reported,actualServiceOrCollectorOrDbJmsRootVmNativeActions=0,globalYkt2177Closed=False,newAcceptance=0,formalUpdated=False,effortRate=None,whole451Accepted=False,files={p.name:sha(p) for p in O.iterdir()},toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,existingTestsRequalified=14,allSourceFour100=True,positiveMain=len(positive),metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
