"""Independent terminal/XML/input/oracle/receipt qualification, no test replay or Main coverage claim."""
from pathlib import Path
import collections,copy,datetime as dt,hashlib,json,re,subprocess,os,zipfile,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg26154-inspector-exclusive-cp-whole14-v1';O=B/'evidence/PG26156-inspector-exclusive-cp-independent-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=B/'evidence/PG26154-inspector-exclusive-cp-whole14-v1/manifest.json';assert sha(p)=='52436c1681fb0710fe2305c8426def82ed186ed11766a58e0593d388bfd3d5fb';m=load(p);assert sha(S/'manifest.safe.json')==sha(p)
assert type(m['actualExit']) is int and m['actualExit']==0 and m['source']=='0c6ee58560e2401b97a50b8f359ba88d4efc290c' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
assert set(m['stages'])=={'compile','unit'} and all(type(v['actualExit']) is int and v['actualExit']==0 and v['timedOut'] is False for v in m['stages'].values())
pf=load(B/'evidence/PG26088-inspector-current-preflight-v1/manifest.json');assert m['begin']['testSourceHashes']==pf['testSourceHashes']
for n,h in {**pf['testSourceHashes'],**pf['readOnlyPublicInputs'],**pf['childGuardSourceHashes']}.items():assert sha(R/n)==h and hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+n])).hexdigest()==h
cases=[];counts=[]
for n,h in m['xmlHashes'].items():
 pxml=p.parent/n;assert sha(pxml)==h==sha(S/'xml'/n);root=ET.parse(pxml).getroot();assert all(root.get(k)=='0' for k in ['failures','errors','skipped']);counts.append(int(root.get('tests')))
 for c in root.findall('testcase'):
  assert not any(x.tag in ['failure','error','skipped'] for x in c);cases.append((c.get('classname'),c.get('name').split('(')[0]))
expected={(('dev.codex.schubert.nk.api.maintenance.'+Path(n).stem),method) for n,methods in pf['expectedMethods'].items() for method in methods};assert sum(counts)==len(cases)==len(set(cases))==14 and set(cases)==expected
summary=(p.parent/'unit.stdout').read_text()
for label,expectedCount in [('containers skipped',0),('containers aborted',0),('containers failed',0),('tests found',14),('tests skipped',0),('tests started',14),('tests aborted',0),('tests successful',14),('tests failed',0)]:
 matches=re.findall(r'\[\s*(\d+) '+label+r'\s*\]',summary);assert matches==[str(expectedCount)],label
assert not (p.parent/'unit.stderr').read_text()
fixture=S/'public-fixture-root';actualReceipts={}
for n,h in m['publicToolReceiptHashes'].items():
 f=fixture/n;assert sha(f)==h;v=load(f);assert set(v)=={'method','command','exitCode','stdout','stderr'};assert v['method']==Path(n).parent.name;actualReceipts.setdefault(v['method'],[]).append(v)
expectedReceiptCounts={'renderedShellCheck':3,'statusMapping':9,'malformedReceipts':29,'argumentsAndPlaceholders':3,'realMainBridge':1,'baseUnitAndSyntax':1,'previousProfiles':4};assert {k:len(v) for k,v in actualReceipts.items()}==expectedReceiptCounts and sum(expectedReceiptCounts.values())==50
assert all(x['exitCode']==0 and x['stdout']==x['stderr']=='' for k in ['baseUnitAndSyntax','previousProfiles'] for x in actualReceipts[k])
assert actualReceipts['realMainBridge'][0]['exitCode']==70 and actualReceipts['realMainBridge'][0]['stdout']==actualReceipts['realMainBridge'][0]['stderr']==''
assert sha(S/'jacoco.exec')==m['execSha256']
# Compare entire original @Test bodies, permitting only the explicitly recorded owner-oracle fix.
old=(B/'evidence/PG26078-inspector-profile-oracle-before-v1/before1.java').read_text();current=(R/'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorDeploymentTest.java').read_text().replace('SHELLCHECK_BINARY','SHELLCHECK')
def bodies(text):
 matches=list(re.finditer(r'  @Test\n  void (\w+)\(',text));end=text.index('  private static void assertReceipt(')
 return {m.group(1):text[m.start():matches[i+1].start() if i+1<len(matches) else end] for i,m in enumerate(matches)}
a,b=bodies(old),bodies(current);assert set(a)==set(b) and len(a)==8
b['previousProfiles']=b['previousProfiles'].replace('                  "maintenance-owner",\n','').replace('assertEquals(4 + selection.size(), ids.size());','assertEquals(3 + selection.size(), ids.size());');folded='List.of(\n                SHELLCHECK.toString(),\n                "--shell=sh",\n                "--severity=style",\n                wrapper.toString())';assert b['renderedShellCheck'].count(folded)==1
b['renderedShellCheck']=b['renderedShellCheck'].replace(folded,'List.of(SHELLCHECK.toString(), "--shell=sh", "--severity=style", wrapper.toString())');assert a==b
assert m['parentHeldFourInitializations']==0 and m['actualServiceVmDbActions']==0 and m['javaMainCoverageClaimed'] is False
# Independent runtime domain is derived from sealed preflight + public current normal, not the raw claim.
normalp=B/'evidence/PG22106-api-stop-static-independent-input-v1/normal.json';assert sha(normalp)=='b2f07209804d71ee2ffbc4d9aca5311d4e6cf15721c74bcde411f86538cf4f27';normal=load(normalp);TC=R.parent/'toolchain'
excluded=[n for n in pf['dependencies'] if '/pgpt-runs/' in n];assert len(excluded)==6
allowedDeps={n:h for n,h in pf['dependencies'].items() if n not in excluded};assert all(n.startswith(str(TC)+os.sep) and '-SNAPSHOT' not in n and '/dev/codex/schubert/' not in n for n in allowedDeps)
assert m['begin']['dependencies']==allowedDeps
console=str(TC/'junit-platform-console-standalone-1.13.4.jar');annotation=str(TC/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar');vendor=[n for n in allowedDeps if n.endswith('.jar') and n not in [console,annotation]];mainJars=[v['path'] for v in normal['jars'].values()];assert len(mainJars)==len(set(mainJars))==6
expectedRuntime=[str(S/'classes'),*mainJars,*vendor,annotation];expectedBoot=[console,*expectedRuntime]
def closed(command):
 assert command.count('-cp')==command.count('--class-path')==1
 assert command[command.index('-cp')+1].split(os.pathsep)==expectedBoot
 assert command[command.index('--class-path')+1].split(os.pathsep)==expectedRuntime
 assert not set(excluded)&set(expectedRuntime)
closed(m['stages']['unit']['command']);guards=[]
for label,arg,change in [('old-main-runtime','--class-path',lambda v:v+[excluded[0]]),('missing-current','--class-path',lambda v:v[:1]+v[2:]),('duplicate-current','--class-path',lambda v:v+[mainJars[0]]),('old-main-boot','-cp',lambda v:v+[excluded[0]])]:
 bad=m['stages']['unit']['command'][:];i=bad.index(arg)+1;bad[i]=os.pathsep.join(change(bad[i].split(os.pathsep)))
 try:closed(bad)
 except AssertionError:guards.append(label)
 else:raise AssertionError('contaminated/missing/duplicate runtime accepted')
closure=m['begin']['runtimeClosure'];assert closure['currentMainJars']==normal['jars'] and closure['vendorJars']=={n:allowedDeps[n] for n in vendor} and closure['excludedOldMainJarPaths']==excluded and closure['allProjectMainFromCurrentSixOnly'] is True and closure['oldProjectJarByteReads']==0
vendorNameChecks={}
for n,h in allowedDeps.items():
 assert sha(Path(n))==h
 if not n.endswith('.jar'):continue
 with zipfile.ZipFile(n) as z:
  names=z.namelist();assert not any(v.endswith('.class') and ('/dev/codex/schubert/' in '/'+v) for v in names);vendorNameChecks[n]=dict(projectClassNames=0,entries=len(names))
assert vendorNameChecks==closure['vendorJarNameChecks']
for row in normal['jars'].values():assert sha(Path(row['path']))==row['sha256']
oldRaw=B/'evidence/PG26096-inspector-whole8-owner6-v1/manifest.json';assert sha(oldRaw)=='989fd36da0f361a49adb17f3a77decdd45d5565081fe2a7c88ab14a293702671';oldIds={(c['className'],c['name'].split('(')[0]) for c in load(oldRaw)['cases']};assert oldIds==set(cases)==expected
compiled={str(p.relative_to(S/'classes')):sha(p) for p in (S/'classes').rglob('*.class')};assert len(compiled)==5
assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str(p.relative_to(R)),sha256=sha(p)),tests=14,originalWholeTests=8,additionalIndependentOwnerTests=6,failures=0,errors=0,skipped=0,aborted=0,containersFailed=0,containersAborted=0,allFourProfiles=[4,5,5,6],originalWholeBodiesPreservedExceptApprovedOwnerOracle=True,toolReceiptCounts=expectedReceiptCounts,static=dict(path=pf['staticManifest']['path'],sha256=pf['staticManifest']['sha256'],pmdRaw=13,applicable=0,checkstyle=0),inputPins=pf['testSourceHashes'],oldCompileFailurePreserved='PG26092 compile1/tests0',originalSuccessfulTestsReplayedForConfirmation=False,changedSourceRequalification=True,parentHeldFourInitializations=0,actualServiceVmDbActions=0,javaMainCoverage=None,javaMainCoverageClaimed=False,childNativeCoverageMeasured=False,newAcceptance=0,formalUpdated=False,effortRate=None,productTestsReexecutedByPost=0,bugs=['BUG-2631','BUG-2632','BUG-2633','BUG-2634'],toolSha256=sha(Path(__file__)))
v.update(runtimeDomainExclusiveCurrentSix=True,excludedOldMainJarPaths=excluded,oldJarByteReads=0,independentRuntimeClosureGuards=guards,vendorJarNameChecks=vendorNameChecks,compiledTestClassHashes=compiled,rawTemplateNewTestIds=m['newTestIds'],additionalTestIdsIntroducedThisRun=0,existingOwnerFixtureCasesRequalified=6,oldFourteenCaseSetExactlyEqual=True,oldResultQualified=False,qualification='CURRENT_SOURCE_EXCLUSIVE_CLASSPATH_LIMITED_FOURTEEN_QUALIFIED_NO_MAIN_COVERAGE_OR_WHOLE_C02',bugs=['BUG-2631','BUG-2632','BUG-2633','BUG-2634','BUG-2635','BUG-2640','BUG-2641'])
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=14,originalWhole=8,owner=6,toolReceipts=50,sha256=sha(O/'manifest.json'))))
