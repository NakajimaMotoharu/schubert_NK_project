"""Five original codec24 suites, complete9 Source/10 physical with existing standard synthetic filter only."""
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
import scoped_prometheus_post as validator
import pg14326_protocol_frame_payload_whole_twenty_four_pt as original
import typed_marker_guard_qualified_v1 as cfg
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='2f93e52f6af6eec17f7b9a6f05fdfa48ce8365f4e8e097d02e191d491e126985'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14326-protocol-frame-payload-whole-twenty-four-pt-v1'
OUT=data.BASE/'PG14328-protocol-frame-payload-whole-twenty-four-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14328-protocol-frame-payload-whole-twenty-four-post-v1'
PREFIX='dev/codex/schubert/nk/protocol/codec/'
SOURCES={PREFIX+'HeaderCodec':'9a4c85c4794558cd0cfe00a87567c707dea439b879c840c0a766c761fda288f3',PREFIX+'FixedWidthEncoder':'69f271a7a06d71ee1092b5a0513e47514829662c6389582f77e99eb340887a21',PREFIX+'FixedWidthDecoder':'dd3701dd1c9bad9d8e0116ffbec56287afefe3a618a25f954ebb6cc70f4ec9d5',PREFIX+'ProtocolValidator':'34b7707426eadec20b44d245c8a6dde5e2b7ad4cd3323625eb30a0a8822a5b70',PREFIX+'ExpectedRoute':'e512bf8bb9a289e5ef3d12ecc4c11f4e01feec3a1e0b8716e2db64ffd416baf2',PREFIX+'TransportMetadata':'198dac5e9cad2046e8e78a4323bfe2e0e2a4a3842044015e8088c1149fcdf646',PREFIX+'TransportBodyType':'e0fdf54397d7d935407d498fcb0679fd957b7af091727fd978c9d67df74f81b8',PREFIX+'MessageEncodingException':'7728bc86a1258f37488c72d0c7eb392cbc9891da33906d6965962526e4f64ab3',PREFIX+'PayloadCodec':'38f9b8d4e5a4aee7afef87edb102317a55182b3e1b958ec2f0f6496770cff181'}
CLOSURES={name:({name,name+'$1'} if name.endswith('/PayloadCodec') else {name}) for name in SOURCES}
NAMES=set().union(*CLOSURES.values())
METADATA={PREFIX+'PayloadCodec$1'}
EXECUTABLE=NAMES-METADATA
TOTAL=24

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={str(data.ROOT/p):h for p,h in original.FIXTURES.items()};validator.EXPECTED_FIXTURE_HASHES.update({str(RUN/'fresh-test-classes'/p.split('/src/test/resources/',1)[1]):h for p,h in original.FIXTURES.items()});validator.assess(raw)

def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    raw=data.read_checked(data.BASE/'PG14326-protocol-frame-payload-whole-twenty-four-pt-v1/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    prefix=[]
    with (RUN/'selected-junit.log').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if not line:break
            if any(line.startswith(k+'=') for k in ('runtime.version','os.name','os.arch','os.version')):
                prefix.append(line.strip().split('=',1))
    assert len(prefix)==4 and len(dict(prefix))==4 and dict(prefix)==raw['stages'][1]['reportedEnvironment']
    assert raw['stages'][1]['environmentBasis']=='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION'
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static_pin='294810b2dab116dbc73bdf41ee39940378f89e173f8100a6109ff5571f3e159e'
    static=data.read_checked(cfg.out(cfg,14224)/'manifest.json',static_pin)
    assert raw['source']==normal['source']==static['source']==original.SOURCE
    assert normal['actualExit']==static['actualExit']==normal['testsExecuted']==0 and hashes==raw['begin']['sourceHashes']
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    for name,h in SOURCES.items():assert hashes['src/schubert-nk-protocol/src/main/java/'+name+'.java']==h
    for key in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:
        assert all(data.sha(Path(p).read_bytes())==h for p,h in raw['begin'][key].items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256']
    actual=[]
    for filename,h in raw['xmlHashes'].items():
        path=RUN/'xml'/filename;assert data.sha(path.read_bytes())==h;root=ET.parse(path).getroot()
        assert raw['suites'][root.get('name')]=={k:int(root.get(k,'0')) for k in ['tests','failures','errors','skipped']}
        for case in root.findall('testcase'):
            assert not list(case);actual.append((case.get('classname'),case.get('name')))
    assert len(actual)==len(set(actual))==TOTAL and set(actual)=={(r['classname'],r['name']) for r in raw['cases']}
    agent='-javaagent:'+str(validator.common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION
    assert agent in raw['stages'][1]['command'] and raw['begin']['selectedSuites']==original.COUNTS
    labels=[]
    for label,change in [('source',lambda v:v.update(source='0'*40)),('failed',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('scope',lambda v:v['begin'].update(selectedSuites={'UnknownTest':TOTAL})),('union',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('fixture',lambda v:v['begin']['fixtureHashes'].update({'unknown':'0'*64}))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false original36 qualification')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit=tool_slot/'audit'
    tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled)
    assert all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    receipt=data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];entries=cp.split(os.pathsep);libraries={p for p in tools if p.endswith('.jar')}
    assert entries[0]==str(audit) and set(entries[1:])==libraries and len(entries)==len(libraries)+1==5
    inventory={};closures={}
    with zipfile.ZipFile(normal['jars']['protocol']['path']) as jar:
        for name in SOURCES:
            closure={p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}
            assert closure==CLOSURES[name];closures[name]=sorted(closure)
        assert set().union(*[set(v) for v in closures.values()])==NAMES
        for name in sorted(NAMES):
            path=snapshot/'src/schubert-nk-protocol/target/classes'/(name+'.class')
            assert jar.read(name+'.class')==path.read_bytes()
            parsed=code.decode(path.read_bytes(),name+'.class')
            assert any(m['hasCode'] for m in parsed['methods'])
            if name in METADATA:
                assert parsed['flags']==4128 and parsed['sourceFile']=='PayloadCodec.java' and parsed['fields']==1 and parsed['methods']==[dict(name='<clinit>',descriptor='()V',flags=8,hasCode=True,codeLength=55)]
            inventory[name]=dict(sha256=data.sha(path.read_bytes()),flags=parsed['flags'],sourceFile=parsed['sourceFile'],methods=parsed['methods'])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=['src/schubert-nk-protocol/src/main/java/'+name+'.java' for name in SOURCES]+[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    expected_owners={'HeaderCodec':'WBS-P002-03','FixedWidthEncoder':'WBS-P002-01','FixedWidthDecoder':'WBS-P002-01','ProtocolValidator':'WBS-P002-01','ExpectedRoute':'WBS-P002-03','TransportMetadata':'WBS-P002-03','TransportBodyType':'WBS-P002-03','MessageEncodingException':'WBS-P002-03','PayloadCodec':'WBS-P002-02'}
    for name,expected_owner in expected_owners.items():
        path='src/schubert-nk-protocol/src/main/java/'+PREFIX+name+'.java'
        assert owners[path]['canonicalOwner']==owners[path]['canonicalCostOwner']==expected_owner
    assert all(owners[str(p.relative_to(data.ROOT))]['canonicalOwner'] is None and owners[str(p.relative_to(data.ROOT))]['canonicalCostOwner'] is None and owners[str(p.relative_to(data.ROOT))]['ownershipStatus']=='UNKNOWN' for p in original.TESTS.values())
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';component.mkdir();physical={}
    for name in sorted(NAMES):
        path=snapshot/'src/schubert-nk-protocol/target/classes'/(name+'.class');target=component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        physical[name]=data.sha(path.read_bytes());assert data.sha(target.read_bytes())==physical[name]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=normal_pin,physicalClasses=physical,priorProductResultsReused=False,productTestsReexecuted=0))
    diagnostic=data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java';diagnostic_pin='fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6'
    classes=data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    assert data.sha(diagnostic.read_bytes())==diagnostic_pin and data.sha((classes/'ComponentCoverageDiagnostic.class').read_bytes())=='3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),*sorted(EXECUTABLE),*['--metadata='+n for n in sorted(METADATA)]])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows={};missed_lines=[];metadata=[]
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS':rows[fields[1]]=dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
        if fields[0]=='MISSED_LINE':missed_lines.append(fields[1:])
        if fields[0]=='METADATA':metadata.append(fields[1])
    assert set(rows)==EXECUTABLE and set(metadata)==METADATA and len(metadata)==1 and all(set(r['counters'])=={'LINE','METHOD','CLASS','BRANCH'} for r in rows.values())
    kinds=['LINE','METHOD','CLASS','BRANCH']
    def totals(names):return {k:dict(missed=sum(rows[n]['counters'][k]['missed'] for n in names if n in rows),covered=sum(rows[n]['counters'][k]['covered'] for n in names if n in rows)) for k in kinds}
    units={}
    for name,closure in closures.items():
        counters=totals(closure)
        units[name]=dict(physical=closure,totals=counters,four100=all(v['missed']==0 and v['covered']>0 for v in counters.values()),metadataOnly=set(closure)<=METADATA,branchNaturallyZero=counters['BRANCH']==dict(missed=0,covered=0) and not set(closure)<=METADATA,threeCounter100=all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']))
    overall=totals(NAMES);four100=all(v['four100'] for v in units.values())
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes())==h
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=5,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,sourceChanged=False,
      targetSourceUnits=9,completeSourceUnitClosure=closures,sourcePhysicalInventory=inventory,completeSourceCoverageMeasured=True,fullSourceUnits=units,targetUnitFour100=four100,strictFour100GateExit=0 if four100 else 1,missedLines=missed_lines,
      cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=overall,stages=stages,owners=owners,registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,onlySuppliedObservationsAndOwnThreads=True,rootMainInvoked=False,manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,helperSourceProgramsNotAcceptedByTheseTargetCounters=True,metadataClasses=sorted(METADATA),metadataKind='COMPILER_SYNTHETIC_ENUM_SWITCH_STANDARD_JACOCO_FILTER_NOT_NO_CODE',naturalZeroBranchSourceUnits=[n for n,v in units.items() if v['branchNaturallyZero']],metadataSourceUnits=[n for n,v in units.items() if v['metadataOnly']],reportedEnvironment=raw['stages'][1]['reportedEnvironment'],branch='dev-foundation'))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=24,suites=5,sourcePrograms=9,executablePhysical=9,metadataPhysical=1,totals=overall,perSourceFour100={n:v['four100'] for n,v in units.items()},crcMismatch=0,singleSession=True)))
if __name__=='__main__':main()
