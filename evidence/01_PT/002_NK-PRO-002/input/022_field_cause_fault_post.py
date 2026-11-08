"""Independent negative-control classification; new oracle fails only on intentional fault."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as E,re,datetime,copy,subprocess
R=Path.cwd();B=R/'evidence/01_PT/002_NK-PRO-002';RUNS=R.parent/'pgpt-runs/PG379';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();S=B/'evidence/PG24644-field-cause-drop-negative-control-v1';mp=S/'manifest.json';assert sha(mp)=='71dbb5e4e57d963c81bd8f422604b4aa2c34cf491e845bd6886c101fabcf9741';m=load(mp);O=B/'evidence/PG24650-field-cause-fault-independent-v1';assert not O.exists();D=RUNS/'pg24644-field-cause-drop-negative-control-v1';assert load(D/'manifest.json')==m and load(D/'begin.json')==m['begin']
normalp=B/'evidence/PG24642-protocol-whole120-independent-v1/manifest.json';assert sha(normalp)=='8ebe6365bc701ba6432b1b55275004024dc71bc452d31b66d31c53894e3ae128';normal=load(normalp);assert normal['actualExit']==0 and normal['tests']==120 and normal['newIndependentCauseCasePassed'] is True and normal['newUniqueTests']==1
for label,stage in m['stages'].items():
 assert stage==load(D/(label+'-exit.safe.json')) and stage['timedOut'] is False
 assert stage['actualExit']==(0 if label=='javac' else 1)
 for stream in ['stdout','stderr']:assert sha(D/(label+'.'+stream))==stage[stream+'Sha256']
cmd=m['stages']['negative']['command'];assert cmd.count('--select-class')==2 and '--select-method' not in cmd and '--scan-classpath' not in cmd and not any('javaagent' in s for s in cmd);cp=cmd[cmd.index('--class-path')+1].split(':');assert cp[0]==str(D/'classes') and cp[1].endswith('/pg24634-protocol-whole120-compile-v1/classes');assert len(cp)==5
fixture=R/m['begin']['fixture']['path'];assert sha(fixture)==m['begin']['fixture']['sha256'];source=fixture.read_text();assert 'NONPRODUCTION ORACLE FAULT' in source and 'super(message); // Intentional negative control' in source and 'super(message, cause)' not in source;shadow=D/'classes/dev/codex/schubert/nk/protocol/codec/FieldEncodingException.class';ix=load(R/'evidence/01_PT/018_NK-OPS-001/evidence/PG23360-base59-named-proof-supplement-v1/current-normal-physical-index.json');assert sha(shadow)!=ix['dev/codex/schubert/nk/protocol/codec/FieldEncodingException']['sha256']
loads=(D/'class-load.log').read_text();assert any('FieldEncodingException source:' in l and str(D/'classes') in l for l in loads.splitlines());assert any('protocol.codec.FieldCodec source:' in l and '/pg22084-api-stop-state-six-main-compile-v1/' in l for l in loads.splitlines());assert not any(h in loads for h in ['TemporaryInfrastructureException','FingerprintKeyRing','ResponseSnapshotCodec','WebStartupException'])
rows=[]
for p in sorted((D/'xml').glob('TEST-*.xml')):
 assert sha(p)==m['originalXmlPins'][p.name]
 for t in E.parse(p).getroot().findall('testcase'):rows.append((t.get('classname'),t.get('name'),bool(t.findall('failure')),bool(t.findall('error')),bool(t.findall('skipped'))))
assert len(rows)==10 and len(set((x[0],x[1]) for x in rows))==10 and sum(x[2] for x in rows)==1 and not any(x[3] or x[4] for x in rows)
new=('dev.codex.schubert.nk.protocol.codec.FieldCodecTest','malformedAndOverflowFailuresRetainDiagnosticCauseWithoutEchoingInput()');assert next((r[0],r[1]) for r in rows if r[2])==new
safe=E.parse(S/'testcases.safe.xml').getroot();assert len(safe.findall('testcase'))==10 and len(safe.findall('.//failure'))==1 and next(t for t in safe.findall('testcase') if t.find('failure') is not None).get('name')==new[1]
normalCases=E.parse(normalp.parent/'testcases.safe.xml').getroot().findall('testcase');assert len(normalCases)==120 and any((t.get('classname'),t.get('name'))==new for t in normalCases) and not any(t.find('failure') is not None for t in normalCases)
assert not subprocess.check_output(['git','diff','--name-only','64f3a72753434347889f0eabd5d9f9dca67c6bfb','--',':(glob)src/**/src/main/java/**/*.java']).strip()
def contract(v):
 for k,n in {'actualExit':0,'testsExecutedUnderFault':10,'junitActualExit':1,'expectedFailures':1,'unexpectedFailures':0,'normalProductTestsAccepted':0,'newUniqueProductTests':0,'newAcceptance':0}.items():assert type(v[k]) is int and v[k]==n
 assert v['oldNinePassed'] is True and v['newOneRejected'] is True and v['normalSourceModified'] is False and v['faultFixtureOnly'] is True and v['coverage'] is None and v['oldExecUnion'] is False and v['formalUpdated'] is False
contract(m);checks=0
for k,v in [('junitActualExit',0),('normalProductTestsAccepted',10),('newUniqueProductTests',1),('oldNinePassed',False),('newOneRejected',False),('normalSourceModified',True),('faultFixtureOnly',False),('coverage',{}),('actualExit',False),('oldExecUnion',True)]:
 bad=copy.deepcopy(m);bad[k]=v;assert json.dumps(bad,sort_keys=True)!=json.dumps(m,sort_keys=True)
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false negative-control PASS credit')
O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],sourceMeaning='Committed test/normal-jar source only; intentional fault source separately pinned by SHA, not that production commit',productionCoreMain=m['productionCoreMain'],normalProof=dict(path=str(normalp.relative_to(R)),sha256=sha(normalp)),faultProof=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),faultFixture=m['begin']['fixture'],faultClassSha256=sha(shadow),normalFieldExceptionClassSha256=ix['dev/codex/schubert/nk/protocol/codec/FieldEncodingException']['sha256'],wholeFixtures=2,testsUnderFault=10,onlyNewOneRejected=True,oldNinePassed=True,expectedJUnitExit=1,actualJUnitExit=1,metadataNegativeChecks=checks,normalSourceModified=False,normalProductTestsAccepted=0,newUniqueProductTests=0,productTestsExecuted=0,coverage=None,noCoverageUnion=True,heldFourInitializations=0,actualRootVmDbNativeKeyOperations=False,newAcceptance=0,formalUpdated=False,effortRate=None,toolSha256=sha(Path(__file__)));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,onlyNewOneRejected=True,normalProductPassCredit=0,metadataNegatives=checks,manifestSha256=sha(O/'manifest.json'))))
