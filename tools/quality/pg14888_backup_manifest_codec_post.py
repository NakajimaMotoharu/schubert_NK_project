"""Whole original codec8, one own exec and entire codec Source; fixed public golden, not backup authentication."""
import copy
import json
import os
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import classfile_code_metadata as code
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg14886_backup_manifest_codec_eight_pt as original
import scoped_prometheus_post as validator
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='2ac97c21726f3a44d77919e7b7aaa80c9ebf3642ed6b10ee167694a2cf38cb92'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14886-backup-manifest-codec-eight-pt-v1'
OUT=data.BASE/'PG14888-backup-manifest-codec-eight-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14888-backup-manifest-codec-eight-post-v1'
NAME='dev/codex/schubert/nk/batch/file/BackupManifestCodec'
PATH='src/schubert-nk-batch/src/main/java/'+NAME+'.java'

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS
    validator.EXPECTED_FIXTURE_HASHES={str(data.ROOT/p):h for p,h in original.FIXTURES.items()}
    validator.EXPECTED_FIXTURE_HASHES.update({str(RUN/'fresh-test-classes'/p.split('/src/test/resources/',1)[1]):h for p,h in original.FIXTURES.items()});validator.assess(raw)

def main():
    invocation=capture(__file__);assert not OUT.exists() and not SLOT.exists()
    raw=data.read_checked(data.BASE/'PG14886-backup-manifest-codec-eight-pt-v1/manifest.json',RAW);assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    normal=data.read_checked(original.COMPILE/'manifest.safe.json',original.COMPILE_SHA);hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static=data.read_checked(data.BASE/'PG14224-typed-marker-guard-v1/manifest.json','294810b2dab116dbc73bdf41ee39940378f89e173f8100a6109ff5571f3e159e')
    assert raw['source']==normal['source']==static['source']==original.SOURCE and normal['actualExit']==static['actualExit']==normal['testsExecuted']==0
    assert hashes==raw['begin']['sourceHashes'] and all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    assert hashes[PATH]=='7e9fdc5ea08e7616d3a8b5e77c5d3d194fbe61872d738ff5281419bcb6eb1d12'
    for role in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:assert all(data.sha(Path(p).read_bytes())==h for p,h in raw['begin'][role].items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256']
    cases=[]
    for filename,h in raw['xmlHashes'].items():
        value=(RUN/'xml'/filename).read_bytes();assert data.sha(value)==h;root=ET.fromstring(value)
        assert int(root.get('tests'))==8 and all(int(root.get(k))==0 for k in ['failures','errors','skipped'])
        for c in root.findall('testcase'):assert not list(c);cases.append((c.get('classname'),c.get('name')))
    assert len(cases)==len(set(cases))==8 and set(cases)=={(c['classname'],c['name']) for c in raw['cases']}
    agent='-javaagent:'+str(validator.common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION
    assert agent in raw['stages'][1]['command'] and raw['begin']['selectedSuites']==original.COUNTS
    prefix=[]
    with (RUN/'selected-junit.log').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if not line:break
            if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):prefix.append(line.strip().split('=',1))
    assert len(prefix)==4 and dict(prefix)==raw['stages'][1]['reportedEnvironment'] and raw['stages'][1]['environmentBasis']=='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION'
    negative=[]
    for label,change in [('source',lambda v:v.update(source='OLD')),('failure',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('scope',lambda v:v['begin'].update(selectedSuites={'Unknown':8})),('union',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('fixture',lambda v:v['begin']['fixtureHashes'].update({'unknown':'0'*64}))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:negative.append(label)
        else:raise AssertionError('false codec8 qualification '+label)
    registry=data.read_checked(data.BASE/'PG14876-current914-carrier-registry-v1/manifest.json','f75bcddfec1b33a972f607881b2de07a129ac5bb0d01f344bb5ce0f5cf74979b')
    assert NAME not in registry['fullSourceUnits'] and not set(cases)&{(c['classname'],c['name']) for c in registry['cases']}
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:
        closure={p[:-6] for p in jar.namelist() if p==NAME+'.class' or p.startswith(NAME+'$') and p.endswith('.class')};assert closure=={NAME}
        value=(snapshot/'src/schubert-nk-batch/target/classes'/(NAME+'.class')).read_bytes();assert jar.read(NAME+'.class')==value
    parsed=code.decode(value,NAME+'.class');assert parsed['sourceFile']=='BackupManifestCodec.java' and any(m['hasCode'] for m in parsed['methods'])
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882');tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses'];audit=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/audit'
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled) and all(data.sha((audit/n).read_bytes())==h for n,h in compiled.items())
    receipt=data.read_checked(audit.parent/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b');cp=receipt['command'][2]
    entries=cp.split(os.pathsep);assert entries[0]==str(audit) and set(entries[1:])=={p for p in tools if p.endswith('.jar')} and len(entries)==5
    diagnostic=data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java';classes=data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    assert data.sha(diagnostic.read_bytes())=='fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6' and data.sha((classes/'ComponentCoverageDiagnostic.class').read_bytes())=='3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';target=component/(NAME+'.class');target.parent.mkdir(parents=True);shutil.copyfile(snapshot/'src/schubert-nk-batch/target/classes'/(NAME+'.class'),target)
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),NAME])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    rows={};missed=[]
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        f=line.split('\t')
        if f[0]=='CLASS':rows[f[1]]=dict(crc64=f[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in f[3:]})
        if f[0]=='MISSED_LINE':missed.append(f[1:])
    assert set(rows)=={NAME};counters=rows[NAME]['counters'];four=all(v['missed']==0 and v['covered']>0 for v in counters.values())
    trace=RUN/'target/backup-manifest-traces/PT-BAT-186-manifest.json';golden=data.ROOT/next(iter(original.FIXTURES));assert trace.read_bytes()==golden.read_bytes() and len(trace.read_bytes())==965 and data.sha(trace.read_bytes())==original.FIXTURES[str(golden.relative_to(data.ROOT))]
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']};paths=[PATH,*[str(p.relative_to(data.ROOT)) for p in [original.TESTS['BackupManifestCodecTest'],original.EXTRA]]];owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    assert owners[PATH]['canonicalOwner']==owners[PATH]['canonicalCostOwner']=='WBS-P017-05'
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items());verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes())==h
    shutil.copyfile(trace,OUT/trace.name)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=original.COMPILE_SHA,tests=8,suites=1,failures=0,errors=0,skipped=0,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=original.SESSION,singleSession=True,crcMismatch=0,physicalClasses={NAME:data.sha(value)},sourcePhysicalInventory={NAME:dict(sha256=data.sha(value),sourceFile=parsed['sourceFile'],flags=parsed['flags'],methods=parsed['methods'])},executable=rows,metadataClasses=[],totals=counters,completeSourceUnitClosure={NAME:[NAME]},fullSourceUnits={NAME:dict(physical=[NAME],totals=counters,four100=four,metadataOnly=False,branchNaturallyZero=counters['BRANCH']==dict(missed=0,covered=0),threeCounter100=all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']))},targetUnitFour100=four,strictFour100GateExit=0 if four else 1,missedLines=missed,owners=owners,metadataNegativeVectors=len(negative),negativeLabels=negative,stages=stages,fixtureHashes=original.FIXTURES,ownedSyntheticTrace=dict(path=trace.name,sha256=data.sha(trace.read_bytes()),bytes=965,basis='PUBLIC_GOLDEN_CLAIMS_NOT_ACTUAL_BACKUP'),reportedEnvironment=raw['stages'][1]['reportedEnvironment'],manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,productTestsReexecutedByPost=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,oldCoverageTransferred=False,coverageExecUnion=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,rootMainInvoked=False,helperSourceProgramsNotAcceptedByTheseTargetCounters=True));print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(counters))

if __name__=='__main__':main()
