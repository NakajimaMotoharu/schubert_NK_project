"""Independent terminal/XML/input/oracle/receipt qualification, no test replay or Main coverage claim."""
from pathlib import Path
import collections,datetime as dt,hashlib,json,re,subprocess,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';S=R.parent/'pgpt-runs/PG379/pg26096-inspector-whole8-owner6-v1';O=B/'evidence/PG26100-inspector-eight-six-independent-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
p=B/'evidence/PG26096-inspector-whole8-owner6-v1/manifest.json';assert sha(p)=='989fd36da0f361a49adb17f3a77decdd45d5565081fe2a7c88ab14a293702671';m=load(p);assert sha(S/'manifest.safe.json')==sha(p)
assert type(m['actualExit']) is int and m['actualExit']==0 and m['source']=='46d7f20c825ec69cc18f2aa42396d55624df1b52' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
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
assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str(p.relative_to(R)),sha256=sha(p)),tests=14,originalWholeTests=8,additionalIndependentOwnerTests=6,failures=0,errors=0,skipped=0,aborted=0,containersFailed=0,containersAborted=0,allFourProfiles=[4,5,5,6],originalWholeBodiesPreservedExceptApprovedOwnerOracle=True,toolReceiptCounts=expectedReceiptCounts,static=dict(path=pf['staticManifest']['path'],sha256=pf['staticManifest']['sha256'],pmdRaw=13,applicable=0,checkstyle=0),inputPins=pf['testSourceHashes'],oldCompileFailurePreserved='PG26092 compile1/tests0',originalSuccessfulTestsReplayedForConfirmation=False,changedSourceRequalification=True,parentHeldFourInitializations=0,actualServiceVmDbActions=0,javaMainCoverage=None,javaMainCoverageClaimed=False,childNativeCoverageMeasured=False,newAcceptance=0,formalUpdated=False,effortRate=None,productTestsReexecutedByPost=0,bugs=['BUG-2631','BUG-2632','BUG-2633','BUG-2634'],toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,tests=14,originalWhole=8,owner=6,toolReceipts=50,sha256=sha(O/'manifest.json'))))
