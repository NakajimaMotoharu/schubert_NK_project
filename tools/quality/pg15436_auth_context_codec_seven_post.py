"""Original whole AES public-synthetic-key seven, four Source closure, truthful crypto and own-JVM JCA flags."""
import copy
import json
import os
from pathlib import Path
import shutil
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import scoped_prometheus_post as validator
import pg15435_auth_context_codec_seven_pt_v2 as original
import typed_marker_guard_qualified_v1 as cfg
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='fad68cf7e30c38831e7928eb1a17b3effa2cb1326085cd6add557ec4e6e8be85'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg15435-auth-context-codec-seven-pt-v2'
OUT=data.BASE/'PG15436-auth-context-codec-seven-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15436-auth-context-codec-seven-post-v1'
PREFIX='dev/codex/schubert/nk/api/security/'
MAINS={"AuthContextCodec":"6cbdc8b0bc006e036ac3e127685d06c19bbb3c1e05d854cb52c8620d6a6065d6","AuthContextIdentity":"b9dbed4233756c481cdb747d96f6de8843e9d910a4c18f51c30454d16130d7dd","EncryptedAuthContext":"d503847e6b1b1a3853033cbe82eb53678b529d616f36d1dfc0a354b3635954b7","AuthContextCryptoException":"a54b29289de7d08e01d6cbc814e9a815ae2162de559e02eebdb6e677a850066f"}
NAMES=[PREFIX+n for n in MAINS]
TOTAL=7

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={};validator.assess(raw)

def main():
    invocation=capture(__file__);assert isinstance(RAW,str) and len(RAW)==64 and not SLOT.exists() and not OUT.exists()
    raw=data.read_checked(data.BASE/'PG15435-auth-context-codec-seven-pt-v2/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static_pin='294810b2dab116dbc73bdf41ee39940378f89e173f8100a6109ff5571f3e159e'
    static=data.read_checked(cfg.out(cfg,14224)/'manifest.json',static_pin)
    assert raw['source']==normal['source']==static['source']==original.SOURCE
    assert normal['actualExit']==static['actualExit']==normal['testsExecuted']==0
    assert hashes==raw['begin']['sourceHashes'] and all(hashes['src/schubert-nk-api/src/main/java/'+PREFIX+n+'.java']==h for n,h in MAINS.items())
    assert all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
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
    prefix=[]
    with (RUN/'selected-junit.log').open() as stream:
        for _ in range(32):
            line=stream.readline(513)
            if any(line.startswith(k+'=') for k in ['runtime.version','os.name','os.arch','os.version']):prefix.append(line.strip().split('=',1))
    assert len(prefix)==len(dict(prefix))==4 and dict(prefix)==raw['stages'][1]['reportedEnvironment'] and raw['stages'][1]['environmentBasis']=='ORIGINAL_OWN_JVM_PREFIX_NOT_CURRENT_HOST_SUBSTITUTION'
    agent='-javaagent:'+str(validator.common.AGENT)+'=destfile='+str(RUN/'jacoco.exec')+',append=false,sessionid='+original.SESSION
    assert agent in raw['stages'][1]['command'] and raw['begin']['selectedSuites']==original.COUNTS
    labels=[]
    for label,change in [('source',lambda v:v.update(source='0'*40)),('failed',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].append(copy.deepcopy(v['cases'][0]))),('scope',lambda v:v['begin'].update(selectedSuites={'UnknownTest':TOTAL})),('union',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('fixture',lambda v:v['begin']['fixtureHashes'].update({'unknown':'0'*64}))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise AssertionError('false current ordinary qualification')
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit=tool_slot/'audit'
    tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled)
    assert all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    receipt=data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];entries=cp.split(os.pathsep);libraries={p for p in tools if p.endswith('.jar')}
    assert entries[0]==str(audit) and set(entries[1:])==libraries and len(entries)==len(libraries)+1==5
    import classfile_code_metadata as code
    closure={};paths={};inventory={}
    with zipfile.ZipFile(normal['jars']['api']['path']) as jar:
        for name in NAMES:
            group={v[:-6] for v in jar.namelist() if v==name+'.class' or v.startswith(name+'$') and v.endswith('.class')}
            assert group==({name,name+'$Reason'} if name.endswith('Exception') else {name})
            closure[name]=sorted(group)
            for physical_name in group:
                path=snapshot/'src/schubert-nk-api/target/classes'/(physical_name+'.class')
                assert jar.read(physical_name+'.class')==path.read_bytes()
                decoded=code.decode(path.read_bytes(),physical_name+'.class');assert any(m['hasCode'] for m in decoded['methods'])
                paths[physical_name]=path;inventory[physical_name]=dict(sha256=data.sha(path.read_bytes()),flags=decoded['flags'],sourceFile=decoded['sourceFile'],methods=decoded['methods'])
    assert len(closure)==4 and len(paths)==5
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    main_paths=['src/schubert-nk-api/src/main/java/'+name+'.java' for name in NAMES]
    owners={path:dict(sha256=hashes[path],**canonical(path,logical)) for path in [*main_paths,*[str(v.relative_to(data.ROOT)) for v in original.TESTS.values()]]}
    assert all(owners[path]['canonicalOwner']==owners[path]['canonicalCostOwner']=='WBS-P007-03' for path in main_paths)
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';component.mkdir()
    physical={}
    for name,path in paths.items():
        target=component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        physical[name]=data.sha(path.read_bytes());assert data.sha(target.read_bytes())==physical[name]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=normal_pin,physicalClasses=physical,priorProductResultsReused=False,productTestsReexecuted=0))
    diagnostic=data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java'
    diagnostic_pin='fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6'
    classes=data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    assert data.sha(diagnostic.read_bytes())==diagnostic_pin and data.sha((classes/'ComponentCoverageDiagnostic.class').read_bytes())=='3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),PREFIX[:-1]])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows={}
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS':rows[fields[1]]=dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
    assert set(rows)==set(paths) and all(set(v['counters'])=={'LINE','METHOD','CLASS','BRANCH'} for v in rows.values())
    def counters(names):return {k:dict(missed=sum(rows[n]['counters'][k]['missed'] for n in names),covered=sum(rows[n]['counters'][k]['covered'] for n in names)) for k in ['LINE','METHOD','CLASS','BRANCH']}
    full={}
    for name,group in closure.items():
        values=counters(group)
        full[name]=dict(physical=group,totals=values,four100=all(v['missed']==0 and v['covered']>0 for v in values.values()),metadataOnly=False,branchNaturallyZero=values['BRANCH']==dict(missed=0,covered=0),threeCounter100=all(values[k]['missed']==0 and values[k]['covered']>0 for k in ['LINE','METHOD','CLASS']))
    totals=counters(paths);four100=all(v['four100'] for v in full.values());applicable=all(v['missed']==0 for v in totals.values())
    natural_branch=totals['BRANCH']==dict(missed=0,covered=0)
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items())
    verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes())==h
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=1,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,sourceChanged=False,
      targetSourceUnits=4,completeSourceUnitClosure=closure,sourcePhysicalInventory=inventory,fullSourceUnits=full,metadataClasses=[],manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,helperSourceProgramsNotAcceptedByTheseTargetCounters=True,completeSourceCoverageMeasured=True,naturalZeroBranch=natural_branch,branchPercent=None if natural_branch else 100*totals['BRANCH']['covered']/(totals['BRANCH']['covered']+totals['BRANCH']['missed']),branchReason='MEASURED_FULL_SOURCE_WITHOUT_MANUAL_EXCLUSION',targetUnitFour100=four100,allMeasuredApplicableCountersCovered=applicable,strictFour100GateExit=0 if four100 else 1,
      cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=totals,stages=stages,owners=owners,registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,childLocalJcaRegistryRestorationTested=True,ownFreshJvmProviderStateOnly=True,cryptoOrKeyOperationsInvoked=True,cryptoOperationKind='AES256GCM_PUBLIC_SYNTHETIC_TEST_KEYS_ONLY',publicSyntheticTestKeysUsed=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,onlyReviewedPureValueSuites=False,actualFilesOpenedByProduct=False,reportedEnvironment=raw['stages'][1]['reportedEnvironment'],rootMainInvoked=False))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=7,suites=1,totals=totals,crcMismatch=0,singleSession=True,naturalBranchNA=natural_branch)))
if __name__=='__main__':main()
