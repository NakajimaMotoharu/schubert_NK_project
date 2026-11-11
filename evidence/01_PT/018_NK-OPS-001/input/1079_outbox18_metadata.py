"""A4-03 public metadata-only correspondence; old results unchanged, no product/job/private read."""
from pathlib import Path
import datetime as dt,hashlib,json,re,subprocess,xml.etree.ElementTree as X
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';E=B/'evidence';O=E/'PG26030-outbox18-metadata-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text())
post=E/'PG25454-api-outbox-jdbc-whole18-independent-v1/manifest.json'
assert sha(post)=='66ac318ff158abf1b95330988401f42e8424f6a9ff590a62791fed978b6a5ee7';m=load(post)
assert type(m['actualExit']) is int and m['actualExit']==0 and m['tests']==18 and m['wholeFixtures']==2
assert m['source']=='103ae01acff5f25b4d25c48c932e520892856811' and m['productionCoreMain']=='7aed8eace7c844c2f79f2e39db766faf914890d5'
for ref in [m['producerManifest'],m['preflight']]:assert sha(R/ref['path'])==ref['sha256']
raw=load(R/m['producerManifest']['path']);pf=load(R/m['preflight']['path'])
assert raw['actualExit']==0 and raw['productTestsExecuted']==18 and raw['source']==m['source']
for key in ['compile','unit','coverage','execinfo','classinfo']:assert raw['stages'][key]['actualExit']==0 and raw['stages'][key]['timedOut'] is False
expect={'dev.codex.schubert.nk.api.monitoring.OutboxObservationRepositoryTest':10,'dev.codex.schubert.nk.api.monitoring.OutboxMetricCollectorTest':8}
assert pf['expectedCaseCounts']==expect and pf['expectedTests']==18
for p,h in pf['inputHashes'].items():assert sha(R/p)==h==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+p])).hexdigest()
appref=pf['sourceContinuityAndStatic'];assert sha(R/appref['path'])==appref['sha256'];app=load(R/appref['path'])
assert app['originalWholeCases']==18 and len(app['sourceContinuity'])==2 and all(v['originalWholeBodiesExactlyRestored'] is True for v in app['sourceContinuity'])
expectedPairs=set();before=load(E/'PG25442-api-outbox-jdbc-owner-before-v1/manifest.json')
for r in before['sources']:
 # Saved safe metadata plus content-addressed Git blob; no historical raw logs or DB.
 old=subprocess.check_output(['git','show',r['gitBlobObjectIdSHA1']],text=True);assert hashlib.sha256(old.encode()).hexdigest()==r['sha256']
 cls='dev.codex.schubert.nk.api.monitoring.'+Path(r['path']).stem
 names=re.findall(r'^  void ([A-Za-z0-9_]+)\(',old,re.M);assert len(names)==expect[cls]
 expectedPairs.update((cls,n+'()') for n in names)
for name,h in m['files'].items():assert sha(post.parent/name)==h
actualPairs=[]
for t in X.parse(post.parent/'testcases.safe.xml').getroot().findall('testcase'):
 assert not any(t.findall(tag) for tag in ['failure','error','skipped']);actualPairs.append((t.get('classname'),t.get('name')))
assert len(actualPairs)==len(set(actualPairs))==18 and set(actualPairs)==expectedPairs
assert len(raw['cases'])==18 and {(v['className'],v['name']) for v in raw['cases']}==expectedPairs and all(not v['nonPass'] for v in raw['cases'])
source=R/'evidence/01_PT/018_NK-OPS-001/input/970_api_outbox_jdbc_whole18_independent.py'
assert sha(source)==m['toolSha256'];text=source.read_text();assert "len(actual)==len(set(actual))==18" in text and 'originalSixteenAssertionsUnchanged=True' in text
# The sibling is named Sixteen correctly; no rewrite or duplicate verification run.
sibling=R/'evidence/01_PT/018_NK-OPS-001/input/963_api_async_jdbc_whole16_independent.py'
assert 'originalSixteenAssertionsUnchanged=True' in sibling.read_text() and "len(actual)==len(set(actual))==16" in sibling.read_text()
assert not O.exists();O.mkdir()
v=dict(actualExit=0,atJST=dt.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=m['productionCoreMain'],originalManifest=dict(path=str(post.relative_to(R)),sha256=sha(post)),originalArtifactsUnmodified=True,legacyFieldName='originalSixteenAssertionsUnchanged',legacyLabelDisposition='DEPRECATED_TEMPLATE_LABEL_NOT_A_16_TEST_LIMIT',originalWholeAssertionsUnchanged=True,originalWholeAssertionCount=18,fixtureCount=2,expectedCaseCounts=expect,casePairs=[dict(className=c,name=n) for c,n in sorted(actualPairs)],sameCurrentInputBytes=True,currentByteReuseNotNewRun=True,allSourceFour100ExistingOnly=m['allSourceFour100'],requalifiedProductTestsByThisTool=0,productTestsExecuted=0,productTestsReexecuted=0,oldSourceSuccessTransferred=False,originalFailures=0,originalErrors=0,originalSkipped=0,bug='BUG2625',ykt='YKT2307',horizontalTargets=[dict(path=str(source.relative_to(R)),disposition='EXPLICIT18_SUPPLEMENT'),dict(path=str(sibling.relative_to(R)),disposition='CORRECT16_LABEL_NONAPPLICABLE')],newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');assert sha(post)==v['originalManifest']['sha256'];print(json.dumps(dict(actualExit=0,existingPairs=18,fixtures=2,newPt=0,manifestSha256=sha(O/'manifest.json'))))
