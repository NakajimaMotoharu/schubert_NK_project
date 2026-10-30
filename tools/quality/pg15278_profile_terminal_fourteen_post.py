"""Two complete Profile/Terminal Sources from original14; passive native-boundary absence and true NoCode interface."""
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
import pg15276_profile_terminal_fourteen_pt as original
import scoped_prometheus_post as validator
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='5904cdcde28f372b55148118f1e28a52ab8e282c1b9b473079d76c07316cfa1d'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg15276-profile-terminal-fourteen-pt-v1'
OUT=data.BASE/'PG15278-profile-terminal-fourteen-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15278-profile-terminal-fourteen-post-v1'
PREFIX='dev/codex/schubert/nk/bootstrap/'
DEFS={"FixedNativeCoverageProfile":("b07dec9433f1259f1f3269f0c74a158357d422977d60906e37070899e421bddd",["Phase","TerminalRole"]),"FixedNativeCoverageTerminal":("38e22ded1b51714c4718a08834199ed6a9653d7d2039c6d8be6fa74081df10ff",["Factory"])}
CLOSURES={PREFIX+n:sorted([PREFIX+n,*[PREFIX+n+'$'+v for v in nested]]) for n,(pin,nested) in DEFS.items()}
NAMES=set().union(*(set(v) for v in CLOSURES.values()))
METADATA={PREFIX+'FixedNativeCoverageTerminal$Factory'}

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS
    validator.EXPECTED_FIXTURE_HASHES={str(data.ROOT/p):h for p,h in original.FIXTURES.items()}
    validator.EXPECTED_FIXTURE_HASHES.update({str(RUN/'fresh-test-classes'/p.split('/src/test/resources/',1)[1]):h for p,h in original.FIXTURES.items()});validator.assess(raw)

def main():
    invocation=capture(__file__);assert not OUT.exists() and not SLOT.exists()
    raw=data.read_checked(data.BASE/'PG15276-profile-terminal-fourteen-pt-v1/manifest.json',RAW);assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    normal=data.read_checked(original.COMPILE/'manifest.safe.json',original.COMPILE_SHA);hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static=data.read_checked(data.BASE/'PG14224-typed-marker-guard-v1/manifest.json','294810b2dab116dbc73bdf41ee39940378f89e173f8100a6109ff5571f3e159e')
    assert raw['source']==normal['source']==static['source']==original.SOURCE and normal['actualExit']==static['actualExit']==normal['testsExecuted']==0
    assert hashes==raw['begin']['sourceHashes'] and all(data.sha((data.ROOT/p).read_bytes())==data.sha((snapshot/p).read_bytes())==h for p,h in hashes.items())
    for role in ['dependencyHashes','testSourceHashes','emptyConfigHashes','fixtureHashes']:assert all(data.sha(Path(p).read_bytes())==h for p,h in raw['begin'][role].items())
    assert data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'];cases=[]
    for filename,h in raw['xmlHashes'].items():
        content=(RUN/'xml'/filename).read_bytes();assert data.sha(content)==h;root=ET.fromstring(content);simple=root.get('name').rsplit('.',1)[-1]
        assert int(root.get('tests'))==original.COUNTS[simple] and all(int(root.get(k))==0 for k in ['failures','errors','skipped'])
        for c in root.findall('testcase'):assert not list(c);cases.append((c.get('classname'),c.get('name')))
    assert len(cases)==len(set(cases))==14 and len(raw['xmlHashes'])==3 and set(cases)=={(c['classname'],c['name']) for c in raw['cases']}
    registry=data.read_checked(data.BASE/'PG15266-current1734-fixed-argv-registry-v1/manifest.json','e4a78ab9db65ca49e2f673682e37fe3bf768b031d119e7d5a4ad367f8024952e')
    assert not CLOSURES.keys()&registry['fullSourceUnits'].keys() and not set(cases)&{(c['classname'],c['name']) for c in registry['cases']}
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
    for label,change in [('source',lambda v:v.update(source='OLD')),('failure',lambda v:v['cases'][0].update(result='NOT_PASS')),('duplicate',lambda v:v['cases'].__setitem__(1,copy.deepcopy(v['cases'][0]))),('scope',lambda v:v['begin'].update(selectedSuites={'Unknown':55})),('union',lambda v:v['begin'].update(priorCoverageTransferred=True)),('formal',lambda v:v.update(formalUpdated=True)),('timeout',lambda v:v['stages'][1].update(timedOut=True)),('fixture',lambda v:v['begin']['fixtureHashes'].update({'unknown':'0'*64}))]:
        bad=copy.deepcopy(raw);change(bad)
        try:assess(bad)
        except ValueError:negative.append(label)
        else:raise AssertionError('false Web-pool-context56 qualification '+label)
    physical={};inventory={}
    with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:
        for simple,(pin,nested) in DEFS.items():
            name=PREFIX+simple;path='src/schubert-nk-bootstrap/src/main/java/'+name+'.java';assert hashes[path]==pin
            assert {p[:-6] for p in jar.namelist() if p==name+'.class' or p.startswith(name+'$') and p.endswith('.class')}==set(CLOSURES[name])
            for n in CLOSURES[name]:
                value=(snapshot/'src/schubert-nk-bootstrap/target/classes'/(n+'.class')).read_bytes();assert jar.read(n+'.class')==value;parsed=code.decode(value,n+'.class')
                assert parsed['sourceFile']==simple+'.java' and (not any(m['hasCode'] for m in parsed['methods']) if n in METADATA else any(m['hasCode'] for m in parsed['methods']))
                physical[n]=data.sha(value);inventory[n]=dict(sha256=physical[n],sourceFile=parsed['sourceFile'],flags=parsed['flags'],methods=parsed['methods'])
    assert set(physical)==NAMES and len(NAMES)==5
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=['src/schubert-nk-bootstrap/src/main/java/'+n+'.java' for n in CLOSURES]+[str(p.relative_to(data.ROOT)) for p in original.TESTS.values()]
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    assert len(owners)==5
    for path,v in owners.items():
        if '/src/main/java/' in path:assert v['canonicalOwner']==v['canonicalCostOwner']=='WBS-P018-08' and v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE'
        else:assert v['canonicalOwner'] is v['canonicalCostOwner'] is None and v['ownershipStatus']=='UNKNOWN'
    assert raw['begin']['environment']==original.run.ENV and len([v for v in raw['stages'][1]['command'] if v.startswith('-javaagent:')])==1
    assert not any(v.startswith('-javaagent:/opt/pgpt-tools-pg390/') for v in raw['stages'][1]['command'])
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882');tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses'];audit=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1/audit'
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled) and all(data.sha((audit/n).read_bytes())==h for n,h in compiled.items())
    receipt=data.read_checked(audit.parent/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b');cp=receipt['command'][2];entries=cp.split(os.pathsep)
    assert entries[0]==str(audit) and set(entries[1:])=={p for p in tools if p.endswith('.jar')} and len(entries)==5
    diagnostic=data.ROOT/'tools/quality/architecture/ComponentCoverageDiagnostic.java';classes=data.ROOT.parent/'pgpt-runs/PG379/pg13586-lgs-boundary-whole-eight-measured-post-v1/diagnostic-classes'
    assert data.sha(diagnostic.read_bytes())=='fa4bbb49ea151813cc936b8943646b4e98454de25b4d109a0f76217788526ec6' and data.sha((classes/'ComponentCoverageDiagnostic.class').read_bytes())=='3e422b4d874c97ecd09542207e2ccbca0ad4cf1addd0a3c5ddb3e22eebacec5f'
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';component.mkdir()
    for n in NAMES:
        target=component/(n+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(snapshot/'src/schubert-nk-bootstrap/target/classes'/(n+'.class'),target);assert data.sha(target.read_bytes())==physical[n]
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'ComponentCoverageDiagnostic',str(RUN/'jacoco.exec'),str(component),*sorted(NAMES-METADATA),*['--metadata='+n for n in sorted(METADATA)]])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    reader=data.ROOT/'tools/quality/architecture/OwnedProfileNativeProbeAbsence.java';reader_hash=data.sha(reader.read_bytes());reader_classes=SLOT/'passive-classes';reader_classes.mkdir()
    for label,command,expected in [
        ('passive-compile',[str(jdk/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader_classes),str(reader)],0),
        ('passive-native-absence',[str(jdk/'java'),'-cp',str(reader_classes)+os.pathsep+cp,'OwnedProfileNativeProbeAbsence',str(RUN/'jacoco.exec'),original.SESSION],0),
        ('passive-wrong-session',[str(jdk/'java'),'-cp',str(reader_classes)+os.pathsep+cp,'OwnedProfileNativeProbeAbsence',str(RUN/'jacoco.exec'),'WRONG_PUBLIC_SESSION'],1),
        ('passive-missing-args',[str(jdk/'java'),'-cp',str(reader_classes)+os.pathsep+cp,'OwnedProfileNativeProbeAbsence'],1)]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==expected and not stage['timedOut']
    prefixes=[PREFIX+'NativeCoveragePrivateFile',PREFIX+'FixedNativeCoverageCheckpoint$PublicAgent',PREFIX+'FixedServiceIdentity$NativeQuery']
    passive_rows=[line.split(chr(9)) for line in (SLOT/'passive-native-absence.stdout').read_text().splitlines()]
    assert len(passive_rows)==3 and {r[1] for r in passive_rows}==set(prefixes) and all(r[0]=='OWNED_PROFILE_NATIVE_PREFIX_NO_TRUE_PROBES' and len(r)==4 and r[2].isdigit() and r[3]=='0' for r in passive_rows)
    with zipfile.ZipFile(normal['jars']['bootstrap']['path']) as jar:assert all(prefix+'.class' in jar.namelist() for prefix in prefixes)
    assert data.sha(reader.read_bytes())==reader_hash
    passive=dict(readerSourcePath=str(reader.relative_to(data.ROOT)),readerSourceSha256=reader_hash,readerClassSha256=data.sha((reader_classes/'OwnedProfileNativeProbeAbsence.class').read_bytes()),sessionIdentity=original.SESSION,execSha256=raw['execSha256'],rows=passive_rows,prefixes=prefixes,productClassesLoaded=False,productMethodsInvoked=False,allPrefixesNormalJarPresent=True,toolNegativeExpectedExits=[1,1])
    rows={};missed=[];metadata=set()
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        f=line.split('\t')
        if f[0]=='CLASS':rows[f[1]]=dict(crc64=f[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in f[3:]})
        if f[0]=='METADATA':metadata.add(f[1])
        if f[0]=='MISSED_LINE':missed.append(f[1:])
    assert metadata==METADATA and set(rows)==NAMES-METADATA and all(set(v['counters'])=={'LINE','METHOD','CLASS','BRANCH'} for v in rows.values())
    def totals(names):return {k:{role:sum(rows[n]['counters'][k][role] for n in names if n not in METADATA) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    units={}
    for name,closure in CLOSURES.items():
        counters=totals(closure);units[name]=dict(physical=closure,totals=counters,four100=all(v['missed']==0 and v['covered']>0 for v in counters.values()),metadataOnly=False,branchNaturallyZero=counters['BRANCH']==dict(missed=0,covered=0),threeCounter100=all(counters[k]['missed']==0 and counters[k]['covered']>0 for k in ['LINE','METHOD','CLASS']))
    four=all(u['four100'] for u in units.values())
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and data.sha((RUN/'jacoco.exec').read_bytes())==raw['execSha256'] and all(data.sha((data.ROOT/p).read_bytes())==h for p,h in hashes.items());verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    for filename,h in raw['xmlHashes'].items():shutil.copyfile(RUN/'xml'/filename,OUT/filename);assert data.sha((OUT/filename).read_bytes())==h
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=original.COMPILE_SHA,tests=14,suites=3,failures=0,errors=0,skipped=0,cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],sessionIdentity=original.SESSION,singleSession=True,crcMismatch=0,physicalClasses=physical,sourcePhysicalInventory=inventory,executable=rows,metadataClasses=sorted(METADATA),metadataZeroCountersVerified=True,totals=totals(NAMES),completeSourceUnitClosure=CLOSURES,fullSourceUnits=units,targetUnitFour100=four,strictFour100GateExit=0 if four else 1,missedLines=missed,owners=owners,metadataNegativeVectors=len(negative),negativeLabels=negative,stages=stages,fixtureHashes=original.FIXTURES,reportedEnvironment=raw['stages'][1]['reportedEnvironment'],passiveNativeBoundaryAbsence=passive,manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,productTestsReexecutedByPost=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,oldCoverageTransferred=False,coverageExecUnion=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,actualServiceActions=0,ownChildJvmStandardSdkObserved=False,forcedGcOrHeapDump=False,externalVmOrTargetProcessObserved=False,rootMainInvoked=False,helperSourceProgramsNotAcceptedByTheseTargetCounters=True,canonicalOwnersRemainCandidateNotAccepted=True));print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(totals=totals(NAMES),four100={n:u['four100'] for n,u in units.items()})))

if __name__=='__main__':main()
