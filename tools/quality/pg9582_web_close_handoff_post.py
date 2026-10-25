"""Independent XML/selection/source/CRC/missed-counter qualification of one necessary host PT."""
import copy
import datetime as dt
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture,verify

ROOT=data.ROOT;BASE=data.BASE;SOURCE=data.SOURCE
RUN=ROOT.parent/'pgpt-runs/PG379/pg9580-web-close-handoff-host-v1'
HOST_SHA='d3de468ea11251f37122b32239d7166bd8b239952b8ba112737380ab2e013991'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg9582-web-close-handoff-post-v1'
OUT=BASE/'PG9582-web-close-handoff-post-v1'
TYPE='dev.codex.schubert.nk.web.bootstrap.WebProcessLifetimeTest'
METHOD='life002ForeignHookWaitsForActualOwnerNotificationAndPreservesInterrupt'
CLASS='dev/codex/schubert/nk/web/bootstrap/WebProcessLifetime'
SPEC=ROOT/'evidence/01_PT/018_NK-OPS-001/1942_WebCloseHandoff_当source限定回帰仕様.md'
SPEC_SHA='5a25b9b738bb58256cb7ac8f9389baee6784edf0d5970c6534861a1d204a0bce'
HELPER=ROOT/'tools/quality/architecture/WebCloseHandoffCoverageMeasure.java'

def valid_cases(cases):
    if cases!=[dict(classname=TYPE,name=METHOD,result='PASS',nonPass=[])]:
        raise ValueError('the one actual original selected method only; no native test or fabricated PASS')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists() and not SLOT.exists()
    assert data.sha(SPEC.read_bytes())==SPEC_SHA
    run=data.read_checked(RUN/'manifest.safe.json',HOST_SHA)
    assert data.sha((BASE/'PG9580-web-close-handoff-host-v1/manifest.json').read_bytes())==HOST_SHA
    normal=data.read_checked(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json',data.PINS['normal'][1])
    assert run['actualExit']==0 and run['source']==normal['source']==SOURCE
    assert run['begin']['compileManifestSha256']==data.PINS['normal'][1]
    assert run['begin']['selectedSuites']=={'WebProcessLifetimeTest':1} and len(run['stages'])==2
    assert all(stage['actualExit']==0 and not stage['timedOut'] for stage in run['stages'])
    valid_cases(run['cases'])
    xml=RUN/'xml'/('TEST-'+TYPE+'.xml');root=ET.parse(xml).getroot()
    assert root.get('name')==TYPE and {k:int(root.get(k)) for k in ('tests','failures','errors','skipped')}==dict(tests=1,failures=0,errors=0,skipped=0)
    assert len(root.findall('testcase'))==1 and root.find('testcase').get('name')==METHOD and not list(root.find('testcase'))
    assert run['xmlHashes']=={xml.name:data.sha(xml.read_bytes())} and data.sha((RUN/'jacoco.exec').read_bytes())==run['execSha256']
    summary=(RUN/'xml/summary.safe.txt').read_text()
    assert summary=='found=1;started=1;succeeded=1;failed=0;skipped=0;aborted=0;containerFailed=0;containerAborted=0;passed=true'
    for path,digest in run['begin']['dependencyHashes'].items():assert data.sha(Path(path).read_bytes())==digest
    for path,digest in run['begin']['testSourceHashes'].items():assert data.sha(Path(path).read_bytes())==digest
    assert all(data.sha((ROOT/path).read_bytes())==digest for path,digest in run['begin']['sourceHashes'].items())
    assert all(data.sha((data.NORMAL/path).read_bytes())==digest for path,digest in run['begin']['sourceHashes'].items())
    expected_agent='-javaagent:'+str(ROOT.parent/'toolchain/m2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar')+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid=PG9580-WEB-CLOSE-HANDOFF'
    assert expected_agent in run['stages'][-1]['command']
    owners=data.read_checked(BASE/'PG9546-shared-fixture7-source-join-v1/manifest.json','4d82743eb894ccd448a2ef88b40f566bc0fb08a8ee4b5128a925e49c08b7dd61')
    path='src/schubert-nk-web/src/test/java/'+TYPE.replace('.','/')+'.java'
    # TYPE includes package but source root already ends at java; no namespace or group guessing.
    row=[r for r in owners['sourceRows'] if r['path']==path]
    assert len(row)==1 and row[0]['canonicalOwner']==row[0]['canonicalCostOwner']=='WBS-P018-06'
    assert row[0]['sha256']==data.sha((ROOT/path).read_bytes())
    os.umask(0o077);SLOT.mkdir();jar=data.regular_normal_jar('web',normal['jars']['web'])
    with zipfile.ZipFile(jar) as archive:
        actual={p for p in archive.namelist() if p.startswith(CLASS) and p.endswith('.class')}
        assert actual=={CLASS+'.class'}
        target=SLOT/'WebProcessLifetime.class'
        with target.open('xb') as stream:stream.write(archive.read(CLASS+'.class'))
    physical_sha=data.sha(target.read_bytes());helper_sha=data.sha(HELPER.read_bytes())
    tc=ROOT.parent/'toolchain';libs=[tc/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar',
      *[tc/f'm2/repository/org/ow2/asm/{n}/9.10.1/{n}-9.10.1.jar' for n in ('asm','asm-tree','asm-commons')]]
    library_hashes={str(p):data.sha(p.read_bytes()) for p in libs};cp=os.pathsep.join(map(str,libs));classes=SLOT/'reader';classes.mkdir();steps.SLOT=SLOT
    stages=[steps.step('compile-report',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(classes),str(HELPER)])]
    assert stages[0]['actualExit']==0 and not stages[0]['timedOut']
    stages.append(steps.step('measure-whole-class',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(classes)+os.pathsep+cp,HELPER.stem,str(RUN/'jacoco.exec'),str(target)]))
    assert stages[-1]['actualExit']==0 and not stages[-1]['timedOut']
    lines=(SLOT/'measure-whole-class.stdout').read_text().splitlines();first=lines[0].split('\t')
    assert first[:2]==['CLASS',CLASS] and len(first)==3
    counters={}
    for line in lines[1:]:
        label,kind,missed,covered=line.split('\t');assert label=='COUNTER' and kind not in counters
        counters[kind]=dict(missed=int(missed),covered=int(covered))
    assert set(counters)=={'LINE','METHOD','CLASS','BRANCH'} and all(v>=0 for c in counters.values() for v in c.values())
    assert any(c['missed']>0 for c in counters.values()) and counters['CLASS']==dict(missed=0,covered=1)
    rejected=[]
    for label,change in (('missing',lambda x:x.pop()),('duplicate',lambda x:x.append(copy.deepcopy(x[0]))),
      ('native-method',lambda x:x[0].update(name='life004OwnedJvmTermClosesWhileShutdownIsInProgress')),
      ('not-pass',lambda x:x[0].update(result='NOT_PASS')),('skipped',lambda x:x[0].update(nonPass=['skipped']))):
        cases=copy.deepcopy(run['cases']);change(cases)
        try:valid_cases(cases)
        except ValueError:rejected.append(label)
        else:raise AssertionError('invalid selected-method record accepted')
    assert data.sha(HELPER.read_bytes())==helper_sha and data.sha(target.read_bytes())==physical_sha
    assert all(data.sha(Path(p).read_bytes())==digest for p,digest in library_hashes.items())
    verify(invocation);OUT.mkdir()
    value=dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
      specSha256=SPEC_SHA,hostManifestSha256=HOST_SHA,normalManifestSha256=data.PINS['normal'][1],sourceOwnerProof=row[0],
      actualTests=1,suites=1,newTestIds=0,necessaryRegression=1,failures=0,errors=0,skipped=0,aborted=0,
      exactSelectedCaseIds=[METHOD],testId='NATIVE-LIFE002',ordinaryUninstalledComponentOnly=True,
      actualRuntimeHookRegistered=False,actualNativeTestSelected=False,actualVmActions=0,actualDatabaseActions=0,
      wholeSourceUnitCounters=counters,physicalClassSha256=physical_sha,crc64=first[2],sessionId='PG9580-WEB-CLOSE-HANDOFF',
      execSha256=run['execSha256'],xmlSha256=data.sha(xml.read_bytes()),summarySha256=data.sha(summary.encode()),
      reportHelperSha256=helper_sha,reportLibraryHashes=library_hashes,reportStages=stages,metadataCounterexamples=rejected,
      coverageUnion=False,exclusionsAdded=False,requiredWholeClassFour100=False,programPtComplete=False,
      productTestsExecutedByPost=0,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None,
      bug1743Status='STATIC_FIXED_PT_HOLD_ACTUAL_HOOK_AND_UNKNOWN_INTERVAL_UNRUN')
    data.write(SLOT/'manifest.safe.json',value);data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,tests=1,wholeSourceUnitCounters=counters,requiredWholeClassFour100=False)))
    print('manifestSha256='+data.sha((OUT/'manifest.json').read_bytes()))

if __name__=='__main__':main()
