"""Seven original semantic31 suites; full38 Source/40 physical, standard filters unchanged."""
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
import pg14360_protocol_semantic_whole_thirty_one_pt as original
import typed_marker_guard_qualified_v1 as cfg
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='4123691e8775684b13142b4b9c319bca82956c008163c63793dedb5b4de7ebd2'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg14360-protocol-semantic-whole-thirty-one-pt-v1'
OUT=data.BASE/'PG14362-protocol-semantic-whole-thirty-one-post-v1'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg14362-protocol-semantic-whole-thirty-one-post-v1'
PREFIX='dev/codex/schubert/nk/protocol/layout/'
SOURCES={PREFIX+n:h for n,h in {"TypedFieldValues":"1f109d93cb6e8e802ab1a9c0484cfe48689253a34f1322111dfbce58bd0a8cde","TypedPayloadValues":"5db4c6b32786b0803334a4c8f7949bf4be0b6936a71c94658f6cef78e970286b","PayloadTypeCatalog":"39c381766f47ebf2e71ccac4709ebb13272ee2c1dde8720ab888774456b62440","PayloadSemanticValidator":"f2b7b23daa77b820b218089247a82adb0daac8fe8188287b42a8b69c62a502a9","semantic/AnimationCategory":"a2adaa30dca9965fdccf883af5fe78686d3b4350b1a600195b9f61e049c982cd","semantic/AnimationListCategory":"0e7c5503c97d12aa835735ff8b968c6d5126f9f1a9867540af60432a8c41ba32","semantic/AnswerState":"bf012f1ce68157a7d4b62e17f6f996362454d58684301de5fb079d9e2281d29c","semantic/AsyncJobId":"cc3a28d386fbfccd8f1508439706f8f7b033bc826d1b25a2a4b72fd82f1806d2","semantic/AudioId":"76ef923a1a3252318a475663b45559a2233f1e65c5ad3d22b6cf9c92026bf3f6","semantic/ContentDisposition":"1fa2440174428ce5529c8334891d36cfcc407fa12afeed607cf9077d4abbd629","semantic/DeliveryMode":"5b4b7af1fc8cd8d9049ac0da29be74c82e61d1b68653eb3767690962778955a9","semantic/DisplayPath":"2718fe6494806fc87dc3d081f82ed220616a07d53bf6eb39a23de579b3c6e7e3","semantic/ElapsedMilliseconds":"cd23948f05d7b3b3b6b24b8c39f6d7efd6682b61903658d0bcff016b17036b13","semantic/EntryId":"f4a1642d932924d09fc9364fddbc8f5f2a6b017f40a1fe3cc13b0ff86b7d552e","semantic/EntryType":"91fad6df8d86dea4d97d122955f93bb830388197eb3bbb173eb5838d598104fd","semantic/GameCode":"fd1c8af391cdd029dca64986c4bf8e7660ef06382c2ac6ce199c0e22bca40b92","semantic/HttpStatusCode":"b55789756f4af3ec1480a1dd7ec123d037efd0d0208a3d9699f06285b1e1b275","semantic/IdValue":"3bf4d89066c5da24649c0f970e5f0655c37d34f0bbd6120539b9a518c4905cd1","semantic/LogId":"5a8e7b00184d66c21d08dfd9fa49a46bb787b944e455715f3348fea8230a4cea","semantic/LogLevel":"34f8fe67f4f97f1ff339402003a11bd7ae5fe4e38208813f4562dc0eb9919839","semantic/LogType":"6977e3028c290197f23cc2d71f6ca241160d30720ebc8a71fdf65a83b71bdc88","semantic/MediaMimeType":"a138a9d06104be25bf52c0401b34bea3230ae7670c65a1bcffd087469d6fd556","semantic/NotificationErrorCode":"3d1c92bd613a428b5fa25dc6622fd90f71dd2d912d1c34cb7f93b9d952df3f9a","semantic/NotificationId":"9754a3220c258db45262d9447bdbaadf95a80348e57eeb202b1a8fbbecc83ffd","semantic/NotificationState":"4cc72ad360d739a54818f19d87d7e83dde2cb7b5975f6fbf9f544e34b94a4f54","semantic/NotificationType":"0226b90638a1c81e4a60cedb85ac3aa261069a982a745d79711a691bc0f76753","semantic/PairRole":"b881ac09eba717b335039d9deb660ceaf1c7d40de7692ae583647f9efb94c454","semantic/PathSyntax":"891c1c2ad213be265b4535abebdf8ee43a332ab952cabc4a9ca76372657b07b3","semantic/QuestionId":"a0c57ac09481d1a033b35faf9059c7f9c2d152ad62563f9099078c97e3febf3c","semantic/RelativePath":"0700ba6f2ef1263a690a0acd3030ad97455951c8dd66ebf632debeca6ff80fa1","semantic/ScriptFileId":"c4e173ae47563d5220fac49b5664d2d7493f5e273eefaabca97899f3e93ccae7","semantic/Sha256Hex":"263a31fb0dc97901550336ceccc8d46ced8ecfd7cc78e8585f7ceb880bbebc4a","semantic/SpeakerId":"b873745a1447f68db8c40d5742171b773af788f11c6c3e1a9efe792fc2ce7974","semantic/UserId":"482cd1b41f0f5e2408086ca0ea4e6742a2a1c0c80bc541249261c9c339564383","semantic/UserRole":"b68402e5705ca2ac5093a1b98a44de5a9f45ed69cb9b231658b4903c51e0bf69","semantic/UserState":"39ae05a1645dd3297a674075a8cb63832ccdb31f00921e1167dfa6eb2be8c13c","semantic/VideoCategory":"e879c3cb991e034111d597f8d25bdf34c9796a54e242c74ce6da04e1203d54db","semantic/VoiceCondition":"decf1959f0a024b84a91980853b213f010c0fa94b633e30c8dabc371cf036c39"}.items()}
CLOSURES={n:set(v) for n,v in {"dev/codex/schubert/nk/protocol/layout/TypedFieldValues":["dev/codex/schubert/nk/protocol/layout/TypedFieldValues"],"dev/codex/schubert/nk/protocol/layout/TypedPayloadValues":["dev/codex/schubert/nk/protocol/layout/TypedPayloadValues"],"dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog":["dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog$Mapping","dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog","dev/codex/schubert/nk/protocol/layout/PayloadTypeCatalog$RecordMapping"],"dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator":["dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator"],"dev/codex/schubert/nk/protocol/layout/semantic/AnimationCategory":["dev/codex/schubert/nk/protocol/layout/semantic/AnimationCategory"],"dev/codex/schubert/nk/protocol/layout/semantic/AnimationListCategory":["dev/codex/schubert/nk/protocol/layout/semantic/AnimationListCategory"],"dev/codex/schubert/nk/protocol/layout/semantic/AnswerState":["dev/codex/schubert/nk/protocol/layout/semantic/AnswerState"],"dev/codex/schubert/nk/protocol/layout/semantic/AsyncJobId":["dev/codex/schubert/nk/protocol/layout/semantic/AsyncJobId"],"dev/codex/schubert/nk/protocol/layout/semantic/AudioId":["dev/codex/schubert/nk/protocol/layout/semantic/AudioId"],"dev/codex/schubert/nk/protocol/layout/semantic/ContentDisposition":["dev/codex/schubert/nk/protocol/layout/semantic/ContentDisposition"],"dev/codex/schubert/nk/protocol/layout/semantic/DeliveryMode":["dev/codex/schubert/nk/protocol/layout/semantic/DeliveryMode"],"dev/codex/schubert/nk/protocol/layout/semantic/DisplayPath":["dev/codex/schubert/nk/protocol/layout/semantic/DisplayPath"],"dev/codex/schubert/nk/protocol/layout/semantic/ElapsedMilliseconds":["dev/codex/schubert/nk/protocol/layout/semantic/ElapsedMilliseconds"],"dev/codex/schubert/nk/protocol/layout/semantic/EntryId":["dev/codex/schubert/nk/protocol/layout/semantic/EntryId"],"dev/codex/schubert/nk/protocol/layout/semantic/EntryType":["dev/codex/schubert/nk/protocol/layout/semantic/EntryType"],"dev/codex/schubert/nk/protocol/layout/semantic/GameCode":["dev/codex/schubert/nk/protocol/layout/semantic/GameCode"],"dev/codex/schubert/nk/protocol/layout/semantic/HttpStatusCode":["dev/codex/schubert/nk/protocol/layout/semantic/HttpStatusCode"],"dev/codex/schubert/nk/protocol/layout/semantic/IdValue":["dev/codex/schubert/nk/protocol/layout/semantic/IdValue"],"dev/codex/schubert/nk/protocol/layout/semantic/LogId":["dev/codex/schubert/nk/protocol/layout/semantic/LogId"],"dev/codex/schubert/nk/protocol/layout/semantic/LogLevel":["dev/codex/schubert/nk/protocol/layout/semantic/LogLevel"],"dev/codex/schubert/nk/protocol/layout/semantic/LogType":["dev/codex/schubert/nk/protocol/layout/semantic/LogType"],"dev/codex/schubert/nk/protocol/layout/semantic/MediaMimeType":["dev/codex/schubert/nk/protocol/layout/semantic/MediaMimeType"],"dev/codex/schubert/nk/protocol/layout/semantic/NotificationErrorCode":["dev/codex/schubert/nk/protocol/layout/semantic/NotificationErrorCode"],"dev/codex/schubert/nk/protocol/layout/semantic/NotificationId":["dev/codex/schubert/nk/protocol/layout/semantic/NotificationId"],"dev/codex/schubert/nk/protocol/layout/semantic/NotificationState":["dev/codex/schubert/nk/protocol/layout/semantic/NotificationState"],"dev/codex/schubert/nk/protocol/layout/semantic/NotificationType":["dev/codex/schubert/nk/protocol/layout/semantic/NotificationType"],"dev/codex/schubert/nk/protocol/layout/semantic/PairRole":["dev/codex/schubert/nk/protocol/layout/semantic/PairRole"],"dev/codex/schubert/nk/protocol/layout/semantic/PathSyntax":["dev/codex/schubert/nk/protocol/layout/semantic/PathSyntax"],"dev/codex/schubert/nk/protocol/layout/semantic/QuestionId":["dev/codex/schubert/nk/protocol/layout/semantic/QuestionId"],"dev/codex/schubert/nk/protocol/layout/semantic/RelativePath":["dev/codex/schubert/nk/protocol/layout/semantic/RelativePath"],"dev/codex/schubert/nk/protocol/layout/semantic/ScriptFileId":["dev/codex/schubert/nk/protocol/layout/semantic/ScriptFileId"],"dev/codex/schubert/nk/protocol/layout/semantic/Sha256Hex":["dev/codex/schubert/nk/protocol/layout/semantic/Sha256Hex"],"dev/codex/schubert/nk/protocol/layout/semantic/SpeakerId":["dev/codex/schubert/nk/protocol/layout/semantic/SpeakerId"],"dev/codex/schubert/nk/protocol/layout/semantic/UserId":["dev/codex/schubert/nk/protocol/layout/semantic/UserId"],"dev/codex/schubert/nk/protocol/layout/semantic/UserRole":["dev/codex/schubert/nk/protocol/layout/semantic/UserRole"],"dev/codex/schubert/nk/protocol/layout/semantic/UserState":["dev/codex/schubert/nk/protocol/layout/semantic/UserState"],"dev/codex/schubert/nk/protocol/layout/semantic/VideoCategory":["dev/codex/schubert/nk/protocol/layout/semantic/VideoCategory"],"dev/codex/schubert/nk/protocol/layout/semantic/VoiceCondition":["dev/codex/schubert/nk/protocol/layout/semantic/VoiceCondition"]}.items()}
NAMES=set().union(*CLOSURES.values())
METADATA=set()
EXECUTABLE=NAMES-METADATA
TOTAL=31

def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={str(data.ROOT/p):h for p,h in original.FIXTURES.items()};validator.EXPECTED_FIXTURE_HASHES.update({str(RUN/'fresh-test-classes'/p.split('/src/test/resources/',1)[1]):h for p,h in original.FIXTURES.items()});validator.assess(raw)

def main():
    invocation=capture(__file__);assert not SLOT.exists() and not OUT.exists()
    raw=data.read_checked(data.BASE/'PG14360-protocol-semantic-whole-thirty-one-pt-v1/manifest.json',RAW)
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
        else:raise AssertionError('false original31 qualification')
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
            if name in METADATA:raise ValueError('unexpected generated metadata in these complete target closures')
            inventory[name]=dict(sha256=data.sha(path.read_bytes()),flags=parsed['flags'],sourceFile=parsed['sourceFile'],methods=parsed['methods'])
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    paths=['src/schubert-nk-protocol/src/main/java/'+name+'.java' for name in SOURCES]+[str(p.relative_to(data.ROOT)) for p in [*original.TESTS.values(),original.ROOT/'IndependentNamedFieldOracle.java']]
    owners={p:dict(sha256=hashes[p],**canonical(p,logical)) for p in paths}
    expected_owners={n:('WBS-P002-01' if n.startswith('semantic/') else {'TypedFieldValues':'WBS-P001-03','TypedPayloadValues':'WBS-P001-03','PayloadTypeCatalog':'WBS-P001-02','PayloadSemanticValidator':'WBS-P002-02'}[n]) for n in ["TypedFieldValues","TypedPayloadValues","PayloadTypeCatalog","PayloadSemanticValidator","semantic/AnimationCategory","semantic/AnimationListCategory","semantic/AnswerState","semantic/AsyncJobId","semantic/AudioId","semantic/ContentDisposition","semantic/DeliveryMode","semantic/DisplayPath","semantic/ElapsedMilliseconds","semantic/EntryId","semantic/EntryType","semantic/GameCode","semantic/HttpStatusCode","semantic/IdValue","semantic/LogId","semantic/LogLevel","semantic/LogType","semantic/MediaMimeType","semantic/NotificationErrorCode","semantic/NotificationId","semantic/NotificationState","semantic/NotificationType","semantic/PairRole","semantic/PathSyntax","semantic/QuestionId","semantic/RelativePath","semantic/ScriptFileId","semantic/Sha256Hex","semantic/SpeakerId","semantic/UserId","semantic/UserRole","semantic/UserState","semantic/VideoCategory","semantic/VoiceCondition"]}
    for name,expected_owner in expected_owners.items():
        path='src/schubert-nk-protocol/src/main/java/'+PREFIX+name+'.java'
        assert owners[path]['canonicalOwner']==owners[path]['canonicalCostOwner']==expected_owner
    assert all(owners[str(p.relative_to(data.ROOT))]['canonicalOwner'] is None and owners[str(p.relative_to(data.ROOT))]['canonicalCostOwner'] is None and owners[str(p.relative_to(data.ROOT))]['ownershipStatus']=='UNKNOWN' for p in [*original.TESTS.values(),original.ROOT/'IndependentNamedFieldOracle.java'])
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
    assert set(rows)==EXECUTABLE and set(metadata)==METADATA and len(metadata)==0 and all(set(r['counters'])=={'LINE','METHOD','CLASS','BRANCH'} for r in rows.values())
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=7,failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,sourceChanged=False,
      targetSourceUnits=38,completeSourceUnitClosure=closures,sourcePhysicalInventory=inventory,completeSourceCoverageMeasured=True,fullSourceUnits=units,targetUnitFour100=four100,strictFour100GateExit=0 if four100 else 1,missedLines=missed_lines,
      cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=overall,stages=stages,owners=owners,registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,reusedToolRuntimeOnly=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,onlySuppliedObservationsAndOwnThreads=True,rootMainInvoked=False,manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,helperSourceProgramsNotAcceptedByTheseTargetCounters=True,metadataClasses=sorted(METADATA),metadataKind='NONE',naturalZeroBranchSourceUnits=[n for n,v in units.items() if v['branchNaturallyZero']],metadataSourceUnits=[n for n,v in units.items() if v['metadataOnly']],reportedEnvironment=raw['stages'][1]['reportedEnvironment'],branch='dev-foundation'))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=TOTAL,suites=7,sourcePrograms=len(SOURCES),executablePhysical=len(EXECUTABLE),metadataPhysical=len(METADATA),totals=overall,perSourceFour100={n:v['four100'] for n,v in units.items()},crcMismatch=0,singleSession=True)))
if __name__=='__main__':main()
