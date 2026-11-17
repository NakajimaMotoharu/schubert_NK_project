"""Resolve exact raw sites without suppression; refresh only changed Test, reuse exact Main/SB."""
from pathlib import Path
import datetime,hashlib,json,os,subprocess,xml.etree.ElementTree as E
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';w=r.parent/'pgpt-runs/PG379/pg37300-p020-prepare-v1';out=b/'evidence/PG37304-p020-static-admission-v1';assert not out.exists();out.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));p0=b/'evidence/PG37300-p020-prepare-v1';p2=b/'evidence/PG37302-p020-static-current-v1';prior=ld(p2/'manifest.json');assert prior['actualExit']==0
jdk=tc/'jdk-25.0.4/bin';classes=w/'snapshot/program/characterization/target/classes';cfg=ld(r.parent/'pgpt-runs/PG379/pg37008-p020-public-package-v1/package.json');sdk=r.parent/'pgpt-runs/PG379/pg37008-p020-public-package-v1/sdk';cp=':'.join([str(classes),*[str(sdk/n) for n in cfg['compileSdk']]]);tests=[r/'program/characterization/tests/java/dev/codex/schubert/characterization'/(n+'.java') for n in ['CharacterizationIoScopeTest','GateOutputFailureContractTest']]
p=tests[0];x=subprocess.run([str(jdk/'java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--assume-filename',p.name,'-'],input=p.read_bytes(),capture_output=True,timeout=30);assert x.returncode==0;p.write_bytes(x.stdout)
env=dict(PATH=str(jdk)+':/usr/bin:/bin',JAVA_HOME=str(jdk.parent),LANG='C.UTF-8');stages={}
def run(name,cmd):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with (out/(name+'.stdout')).open('xb') as stdout,(out/(name+'.stderr')).open('xb') as stderr:x=subprocess.run(cmd,cwd=r,env=env,stdout=stdout,stderr=stderr,timeout=120)
 stages[name]=dict(actualExit=x.returncode,command=cmd,startUTC=start,endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());return x.returncode
assert run('changed-test-compile',[str(jdk/'javac'),'-Xlint:all','-Werror','--release','25','-cp',cp,'-d',str(w/'testclasses'),str(p)])==0
assert run('changed-test-checkstyle',[str(jdk/'java'),'-jar',str(tc/'static-gates-20261015/checkstyle-14.3.0-all.jar'),'-c',str(r/'tools/quality/static/checkstyle.xml'),'-f','xml','-o',str(out/'checkstyle.xml'),str(p)])==0
assert run('changed-test-pmd',[str(tc/'static-gates-20261015/pmd-bin-7.28.0/bin/pmd'),'check','-d',str(p),'--aux-classpath',cp,'--rulesets',str(r/'tools/quality/static/pmd.xml'),'--format','xml','--report-file',str(out/'pmd.xml'),'--no-cache']) in [0,4]
decisions=[]
for report in [p0/'main-pmd.xml',out/'pmd.xml',p2/'test-pmd.xml']:
 for f in E.parse(report).getroot():
  if not f.tag.endswith('file'):continue
  path=Path(f.get('name'));name=path.name
  if report==p2/'test-pmd.xml' and name=='CharacterizationIoScopeTest.java':continue
  for v in f:
   assert v.tag.endswith('violation');rule=v.get('rule');line=int(v.get('beginline'));anchor=path.read_text().splitlines()[line-1].strip()
   if rule=='UseConcurrentHashMap':
    assert any(x in anchor for x in ['new TreeMap<>','new HashMap<>','new LinkedHashMap<>']);reason='Fresh method-local ordered/index map, confined to one comparison/report/validator invocation; no shared map mutation. Sequential stream callbacks only. ACTIVE_OUTPUTS shared claims stay ConcurrentHashMap.newKeySet. Retain deterministic iteration; full142 independent concurrent output/tree tests will qualify the changed source before acceptance.'
   elif rule=='AvoidCatchingGenericException':
    assert name=='CharacterizationIoScope.java' and ('primary)' in anchor or 'secondary)' in anchor);reason='Resource-owner cleanup boundary, not normal return: catches IO/runtime/Error solely to close once, retain/rethrow identical primary and suppress only a distinct secondary, including Error. New RAW002..006 assert identity/once/ordering/null/secondary semantics.'
   elif rule=='CompareObjectsWithEquals':
    assert anchor=='if (primary != secondary) primary.addSuppressed(secondary);';reason='Throwable self-suppression is forbidden by reference identity, independent of equals. Calling equals would be incorrect for distinct equal-looking Throwable. RAW004/005 distinguish same and different instances.'
   elif rule=='AvoidAccessibilityAlteration':
    assert name=='CharacterizationIoScopeTest.java' and anchor=='constructor.setAccessible(true);';reason='Narrow whitebox contract for five pure static utility private zero-arg constructors only. Exact class allowlist; TargetAdapter parameterized valid constructor excluded; access flag restored in finally and asserted. No keys/Root/authority/runtime class access.'
   else:raise AssertionError((name,rule,line))
   decisions.append(dict(path=str(path.relative_to(r)),sourceSha256=sha(path),line=line,rule=rule,anchor=anchor,decision='NOT_APPLICABLE',reason=reason))
assert len(decisions)==21
sb=E.parse(p2/'spotbugsXml.xml').getroot();stats={x.get('class') for x in sb.findall('.//ClassStats')};assert stats=={n[:-6].replace('/','.') for n in prior['physicalClassHashes']} and len(stats)==16
assert not sb.findall('BugInstance') and not sb.findall('.//MissingClass') and not sb.findall('.//Error')
assert all(sha(r/path)==h for path,h in prior['inputHashes'].items() if '/src/main/' in path)
(out/'pmd-decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),mainCompileProof=ref(p0/'manifest.json'),spotbugsProof=ref(p2/'manifest.json'),changedTestStages=stages,sourceHashes={str(p.relative_to(r)):sha(p) for p in sorted(r.glob('program/characterization/src/main/java/**/*.java'))+tests},physicalClassHashes=prior['physicalClassHashes'],rawPmdSites=21,applicable=0,unclassified=0,spotbugsClassStats16=True,spotbugsBugsMissingErrors=0,noSuppressionOrRuleChanges=True,testInvocationsExecuted=0,whole451Accepted=False,formalUpdated=False)
(out/'manifest.json').open('x').write(json.dumps(v,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rawPmdSites=21,applicable=0,unclassified=0,physical=16,productTests=0)))
