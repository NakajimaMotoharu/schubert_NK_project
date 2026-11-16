"""Join the actual162 run to literal SQL, all12 cleanup sites and unchanged public ABI."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
c=load(b/'input/4522_ssc450_all162_profile.json')
pp=r/c['slots']['post']/'manifest.json';post=load(pp)
rp=b/'evidence/PG36946-ssc450-original162-unfiltered-v1/manifest.json';raw=load(rp)
up=r/c['slots']['unit']/'manifest.json';unit=load(up)
assert unit['actualExit']==post['actualExit']==raw['actualExit']==0
assert unit['tests']==post['tests']==162 and all(unit[k]==0 for k in ['failures','errors','skipped'])
assert raw['targetRawFour100'] and not raw['componentRawFour100'] and not raw['oldExecCombined']
assert all(v['missed']==0 for v in raw['targetRawCounters'].values())
prep=load(r/c['slots']['prepare']/'manifest.json')
oldp=b/'evidence/PG36844-ssc449-four-main-compile-v1/manifest.json'
newp=b/'evidence/PG36872-ssc450-four-main-compile-v1/manifest.json'
old=load(oldp);new=load(newp);assert old['actualExit']==new['actualExit']==0
assert new['sourceCore']==c['productionCoreMain']==raw['sourceCore']
assert all(new['physicalClassHashes']['bootstrap'][n]==h for n,h in prep['physicalClassHashes'].items())
for module in ['protocol','storage','batch']:
    assert old['physicalClassHashes'][module]==new['physicalClassHashes'][module]
targets=c['targetClasses'];outer=sorted(n for n in targets if '$' not in n)
assert len(outer)==6
oldhash=old['physicalClassHashes']['bootstrap'];newhash=new['physicalClassHashes']['bootstrap']
changed=sorted(n for n,h in oldhash.items() if newhash.get(n)!=h)
assert set(changed)=={n+'.class' for n in targets if n+'.class' in oldhash}
added=sorted(set(newhash)-set(oldhash));assert len(added)==9
assert not (set(oldhash)-set(newhash))
assert all(not raw['classes'][n[:-6]]['counters']['METHOD']['missed'] and
           sum(v['covered']+v['missed'] for v in raw['classes'][n[:-6]]['counters'].values())==0 for n in added)
eqp=b/'evidence/PG36870-ssc450-sql-equivalence-v1/manifest.json';eq=load(eqp)
assert eq['actualExit']==0 and eq['sqlCallsites']==76 and eq['originalTestSourcesUnchanged']
assert all(sha(r/p)==h for p,h in eq['originalTestSourceHashes'].items())
xml=ET.parse(pp.parent/'original-coverage.xml').getroot();sites=[]
for path in c['mainSources']:
    if Path(path).stem not in {n.rsplit('/',1)[1] for n in outer}:continue
    sf=next(n for n in xml.findall('.//sourcefile') if n.get('name')==Path(path).name)
    for index,line in enumerate((r/path).read_text().splitlines(),1):
        if 'cleanup != primary' not in line:continue
        measured=next(n for n in sf.findall('line') if n.get('nr')==str(index))
        assert measured.get('mb')=='0' and int(measured.get('cb'))==2
        sites.append(dict(path=path,line=index,missedBranches=0,coveredBranches=2))
assert len(sites)==12
staticp=r/c['slots']['static']/'manifest.json';static=load(staticp)
assert static['actualExit']==0 and len(static['rawFindings'])==134 and not static['processingErrors']
assert all(static['spotbugs'][key]==0 for key in ['bugs','missing','errors'])
assert len(static['spotbugs']['classStats'])==46
out=b/'evidence/PG36948-ssc450-six-main-quality-join-v1';assert not out.exists();out.mkdir()
javap=r.parent/'toolchain/jdk-25.0.4/bin/javap';abis=[]
for name in outer:
    texts=[];records=[]
    for role,manifest in [('before',old),('after',new)]:
        classes=Path(manifest['cwd'])/'src/schubert-nk-bootstrap/target/classes'
        file=classes/(name+'.class');assert sha(file)==manifest['physicalClassHashes']['bootstrap'][name+'.class']
        command=[str(javap),'-public','-classpath',str(classes),name.replace('/','.')]
        result=subprocess.run(command,capture_output=True,timeout=30);assert result.returncode==0 and not result.stderr
        p=out/(name.rsplit('/',1)[1]+'-'+role+'.txt');p.open('xb').write(result.stdout)
        texts.append(result.stdout);records.append(dict(role=role,command=command,exit=0,file=ref(p)))
    assert texts[0]==texts[1]
    abis.append(dict(className=name,publicAbiExact=True,measurements=records))
value=dict(actualExit=0,source=c['productionCoreMain'],sourceCore=c['productionCoreMain'],
    actualUnitSource=post['source'],terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    run=c['id'],tests=162,failed=0,errors=0,skipped=0,notRun=0,
    original160TestSourcesUnchanged=True,independentNewDefinitions=2,
    literalSqlOperations=76,sqlEquivalence=ref(eqp),unit=ref(up),post=ref(pp),raw=ref(rp),
    static=ref(staticp),staticAdmission=ref(b/'input/4524_ssc450_all162_static_admission.json'),
    targetRawCounters=raw['targetRawCounters'],targetSixSourceRawFour100=True,
    wholeComponentRawFour100=False,all46PhysicalCountersRetained=True,
    helperMissedMethods=raw['helperMissedMethods'],all12CleanupSites=sites,publicAbi=abis,
    all46BytesMatchOriginalRoot=True,otherBootstrap184PhysicalUnchanged=len(oldhash)-len(changed),
    changedBootstrapPhysical=changed,trueNoCodeAddedPhysical=added,
    otherProtocol175Storage80Batch646BytesUnchanged=True,rootCompile=ref(newp),
    staticApplicable=0,staticUnclassified=0,spotbugsBugs=0,
    manualExclusions=[],newSuppressions=0,oldExecCombined=False,
    canonicalCostOwner='WBS-P019-03',resultRecipient='WBS-F03',
    wholeF03Accepted=False,wholeP01903Accepted=False,whole451Accepted=False,
    formalUpdated=False,newOriginal190Acceptance=0,effortCompletionRate=None)
(out/'manifest.json').open('x').write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,tests=162,targetRaw=raw['targetRawCounters'],cleanupSites=len(sites),publicApis=len(abis),otherBootstrapPhysicalUnchanged=len(oldhash)-len(changed),newOriginalAcceptance=0)))
