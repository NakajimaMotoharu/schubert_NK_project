"""Independent unknown identity/sentinel oracles and passive held/native/Root absence; no Product replay."""
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16540_artemis_unknown_original_four_pt as original
import pg16542_artemis_unknown_shared_post as profile
import pg9666_pagination_static as runner

POST=('PG16542-artemis-unknown-shared-post-v1','58accb16df5f39790011956a8c3f2b182d1d13f1795ad616e77f78d3c9020bf3')
RAW=('PG16540-artemis-unknown-original-four-pt-v1','c834461f1359389ac727a89539d2c23d4b29c51e80733cbaa7b5ee303c03a52f')
PREV=('PG16530-current2260-public-signature-registry-v1','7ece9543a6701d06707a9b5d53b572d440403ab9948645652391a32dc26bffb3')
RUN=original.COMPILE.parent/'pg16540-artemis-unknown-original-four-pt-v1'
SLOT=RUN.parent/'pg16544-artemis-unknown-original-four-independent-v1'
OUT=data.BASE/'PG16544-artemis-unknown-original-four-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists() and not SLOT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==original.SOURCE for v in [p,raw,old]),'actual same source')
    source=original.TESTS['ArtemisUnknownBoundaryTest'];blob=source.read_bytes();text=blob.decode();name='dev.codex.schubert.nk.batch.mq.ArtemisUnknownBoundaryTest'
    require(data.sha(blob)==original.TEST_PINS['ArtemisUnknownBoundaryTest']==raw['begin']['testSourceHashes'][str(source)],'unchanged whole original Test')
    methods=re.findall(r'@Test\s+void\s+(\w+)\(',text);require(len(methods)==4,'whole four');expected={(name,m) for m in methods}
    decl=old['currentOrdinaryTestDeclarationReference'];catalog=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',catalog['files']['exact-ordinary-bindings.json'])
    require(expected=={(v['className'],v['method']) for v in bindings if v['className']==name} and not expected&{(v['classname'],v['name']) for v in old['cases']},'new exact current normal declarations, no old-source transfer')
    actual=[]
    for file,pin in p['xmlHashes'].items():
        content=(data.BASE/POST[0]/file).read_bytes();require(data.sha(content)==pin,'original XML')
        root=ET.fromstring(content);require(all(root.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in root.findall('testcase'):require(not list(case),'actual PASS');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==len(set(actual))==4 and set(actual)==expected,'four exact actual cases')
    vectors=[
      ['assertSame(fatal, assertThrows(AssertionError.class, action))','putAcceptorsOperation','putRolesOperation','putAddressSettingsOperation','putExpiryOperation'],
      ['new IllegalStateException(FIXTURE_SYNTHETIC_UNKNOWN_76302106)','new NullPointerException(FIXTURE_SYNTHETIC_UNKNOWN_76302106)','assertEquals(2, calls.get())'],
      ['selected < 6','position < 5','assertEquals(selected + 1, calls.get())','throw unknown'],
      ['new ArtemisReadinessException()','assertThrows(ArtemisManagementReadinessException.class','s -> fail()'],
      ['new ArtemisExpiryPurgeClient.Operations()','public long count','throw supplied','public long remove','fail()'],
      ['new ArtemisExpiryPurgeClient.Observation(1789916400000L, 0, 0, 0, 0)','client.observe(session, run)','client.purgeObserved(session, run, observation)'],
      ['supplied = known ? new ArtemisManagementReadinessException() : unknown','assertThrows(ArtemisExpiryPurgeException.class','assertThrows(NullPointerException.class'],
      ['ClientSession.class.getClassLoader()','ClientMessage.class.getClassLoader()','Proxy.newProxyInstance','Instant.parse("2026-09-27T15:00:00Z")']]
    require(all(all(v in text for v in group) for group in vectors),'independent identity/count/known-only/sentinel oracles')
    require(not any(v in text for v in ['EmbeddedActiveMQ','ActiveMQClient','DriverManager','ProcessBuilder','Files.','KeyFactory','TemporaryInfrastructureException','WebStartupException','withParentDeadline']),'throw-only original, no backend/Graph/owner binding')
    require(data.sha((data.ROOT/'tools/quality/reviewed_whole_pure_source_post_v3.py').read_bytes())=='f41c2d98d5611a4519e2cc71de74998a6c24a491570242664767318e219e145f' and p['effectDisclosureGuardVersion']==3,'unchanged conservative shared v3')
    qualification=data.read_checked(data.BASE/'PG15476-nonsecret-digest-disclosure-post-v1/manifest.json','1c0d87141e7c9b3145aa2196db78347f43731f6306e4392dd6285ea3d90efa7b')
    require(qualification['actualExit']==qualification['productTestsExecuted']==0 and qualification['metadataNegativeVectors']==21,'existing shared guard qualification, not Product replay')
    counts={k:dict(missed=m,covered=c) for k,m,c in [('LINE',43,14),('METHOD',2,6),('CLASS',0,4),('BRANCH',35,1)]}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==original.SOURCE and v['originalManifestSha256']==RAW[1],'actual source/run')
        require((v['tests'],v['suites'],v['targetSourceUnits'],v['newTestIds'])==(4,1,4,0) and v['cases']==raw['cases'],'whole four fourSource')
        require(v['profile']==profile.PROFILE and v['completeSourceUnitClosure']==original.CLOSURES and set(v['physicalClasses'])==set(v['executable'])==set(original.MAIN_UNITS) and v['metadataClasses']==[],'all four complete Code')
        require(wire(v['totals'])==wire(counts) and v['strictFour100GateExit']==1 and v['targetUnitFour100'] is False,'misses retained not four100')
        require(sum(u['branchNaturallyZero'] and u['threeCounter100'] for u in v['fullSourceUnits'].values())==3,'three branchzero complete exception values only')
        require(v['singleSession'] is True and type(v['crcMismatch']) is int and v['crcMismatch']==0 and v['manualCounterExclusions']==[],'one exec CRC/exclusion contract')
        require(v['onlyReviewedPureValueSuites'] is True and v['effectDisclosureGuardVersion']==3 and v['cryptoOrKeyOperationsInvoked'] is False,'reviewed memory callback scope, no helper guard broadening')
        require(all(v[k] is False for k in ['backendReceiverConstructed','actualFilesOpenedByProduct','rootMainInvoked','formalUpdated','whole451Accepted','oldCoverageTransferred','currentSourceExistingExecReanalyzed','originalTestsCountedElsewhere']) and v['effortPercent'] is None,'no backend/old-source/formal inference')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',5),('suites',2),('targetSourceUnits',1),('newTestIds',1),('cases',[]),('profile',{}),('completeSourceUnitClosure',{}),('physicalClasses',{}),('executable',{}),('metadataClasses',['missing']),('totals',{}),('strictFour100GateExit',0),('targetUnitFour100',True),('singleSession',False),('crcMismatch',1),('manualCounterExclusions',['hidden']),('onlyReviewedPureValueSuites',False),('effectDisclosureGuardVersion',2),('cryptoOrKeyOperationsInvoked',True),('backendReceiverConstructed',True),('currentSourceExistingExecReanalyzed',True),('originalTestsCountedElsewhere',True),('formalUpdated',True),('effortPercent',100)]:
        require(wire(p[key])!=wire(value),'nondegenerate '+key);bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false unknown qualification '+key)
    runtime=data.read_checked(data.BASE/'PG13378-db-duration-eight-post-recovery-v3/manifest.json','adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882')
    tool_slot=data.ROOT.parent/'pgpt-runs/PG379/pg13376-db-duration-eight-post-v1';audit=tool_slot/'audit'
    tools=runtime['toolAndDependencyHashes'];compiled=runtime['reusedCompiledClasses']
    assert all(data.sha(Path(p).read_bytes())==h for p,h in tools.items()) and {p.name for p in audit.iterdir()}==set(compiled)
    assert all(data.sha((audit/name).read_bytes())==h for name,h in compiled.items())
    receipt=data.read_checked(tool_slot/'session-identity-exit.safe.json','2bbd55eefa4fc2b0532660748a0f35bfeca6cb69e45e732fc67759add964a84b')
    cp=receipt['command'][2];entries=cp.split(os.pathsep);libraries={p for p in tools if p.endswith('.jar')}
    assert entries[0]==str(audit) and set(entries[1:])==libraries and len(entries)==len(libraries)+1==5

    SLOT.mkdir();runner.SLOT=SLOT;jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
    held_helper=data.ROOT/'tools/quality/architecture/ReviewedProjectionHeldProbeAudit.java'
    held_source_pin='b0db809993acdc26b9e6f961c65ba4d92d19965a6221e555b924acc9171d547b'
    held_classes=data.ROOT.parent/'pgpt-runs/PG379/pg14762-question-sql-joint-eighteen-post-v1/probe-classes'
    held_class_pin='59259d0206719c9b32138b0bed646601593b38989e0ca4a92277e23dcd977f62'
    held_runtime=data.read_checked(data.BASE/'PG14762-question-sql-joint-eighteen-post-v1/manifest.json','9653028e361d41a2b0793e485797ff93c00c4500acf9a06249a54c2f1179c84e')
    assert held_runtime['actualExit']==0 and held_runtime['heldProbeToolMetadataChecks']==10 and held_runtime['heldProbeHelperSha256']==held_source_pin
    assert data.sha(held_helper.read_bytes())==held_source_pin and data.sha((held_classes/'ReviewedProjectionHeldProbeAudit.class').read_bytes())==held_class_pin
    stage=runner.step('passive-held-probe-audit',[str(jdk/'java'),'-cp',str(held_classes)+os.pathsep+cp,'ReviewedProjectionHeldProbeAudit',str(RUN/'jacoco.exec'),original.SESSION],SLOT,timeout=120)
    stages.append(stage);data.write(SLOT/'passive-held-probe-audit-stage.safe.json',stage)
    assert stage['actualExit']==0 and not stage['timedOut'] and (SLOT/'passive-held-probe-audit.stdout').read_text().strip()=='FORBIDDEN_PROBE_HITS=0'
    native_source=data.ROOT/'tools/quality/architecture/OwnedApiPortBoundaryProbeAbsence.java'
    native_classes=data.ROOT.parent/'pgpt-runs/PG379/pg15302-api-config-readiness-eleven-post-v1/passive-classes'
    native_proof=data.read_checked(data.BASE/'PG15302-api-config-readiness-eleven-post-v1/manifest.json','ff665193ddb62c0ed11afac98a9bc5465167ad5348552b2d1d093951de59b92b')
    native=native_proof['passiveNativeBoundaryAbsence']
    assert native_proof['actualExit']==0 and native['productClassesLoaded'] is native['productMethodsInvoked'] is False
    assert data.sha(native_source.read_bytes())==native['readerSourceSha256']=='7cc43c0254642e490fc4f4875f63c4e8a580ac7b793f35ab51626c16ba1778d1'
    assert data.sha((native_classes/'OwnedApiPortBoundaryProbeAbsence.class').read_bytes())==native['readerClassSha256']=='77bf5fb8b9c8f950205050842b94939143cb76263ccae967c4fff9cfed47b973'
    stage=runner.step('passive-native-absence',[str(jdk/'java'),'-cp',str(native_classes)+os.pathsep+cp,'OwnedApiPortBoundaryProbeAbsence',str(RUN/'jacoco.exec'),original.SESSION],SLOT,timeout=120)
    stages.append(stage);data.write(SLOT/'passive-native-absence-stage.safe.json',stage)
    assert stage['actualExit']==0 and not stage['timedOut']
    native_rows=[line.split(chr(9)) for line in (SLOT/'passive-native-absence.stdout').read_text().splitlines()]
    assert len(native_rows)==6 and {r[1] for r in native_rows}==set(native['prefixes']) and all(len(r)==4 and r[0]=='OWNED_API_PORT_NATIVE_PREFIX_NO_TRUE_PROBES' and r[2].isdigit() and r[3]=='0' for r in native_rows)
    passive_native=dict(readerSourceSha256=native['readerSourceSha256'],readerClassSha256=native['readerClassSha256'],rows=native_rows,sessionIdentity=original.SESSION,execSha256=raw['execSha256'],productClassesLoaded=False,productMethodsInvoked=False)

    import jacoco_readonly_exec_subset as decoder
    exec_blob=(RUN/'jacoco.exec').read_bytes();valid=decoder.decode(exec_blob,set())
    require(valid['sessions'][0]['labelBytesHex']==original.SESSION.encode().hex(),'exact raw session')
    normal=data.read_checked(original.COMPILE/'manifest.safe.json',original.COMPILE_SHA)
    prefixes=['dev/codex/schubert/nk/batch/file/RootFailedStartRecovery','dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle']
    allowed='dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle$Outcome'
    with zipfile.ZipFile(normal['jars']['batch']['path']) as jar:names=sorted(n[:-6] for n in jar.namelist() if n.endswith('.class') and any(n.startswith(k) for k in prefixes) and n[:-6]!=allowed)
    root_rows={}
    for n in names:
        try:
            record=decoder.decode(exec_blob,{n})['classes'][n];require(not record['hitProbeIds'],'no Root recovery probes')
            root_rows[n]=dict(recordPresent=True,trueProbeHits=0)
        except ValueError as error:
            require(error.args==('one session and all exact target records required',),'only exact absent record after full exec validation')
            root_rows[n]=dict(recordPresent=False,trueProbeHits=0)
    require(len(root_rows)==27 and all(not r['recordPresent'] and r['trueProbeHits']==0 for r in root_rows.values()),'all recovery classes absent, no Source content read')
    design={}
    for number in ['321','343']:
        paths=list((data.ROOT/'documents/300_SS').glob('*/'+number+'_*.md'));require(len(paths)==1,'unique SS')
        relative=str(paths[0].relative_to(data.ROOT));content=paths[0].read_bytes();require(content==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved SS byte');design[relative]=data.sha(content)
    for v in [p,old,qualification]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=4,suites=1,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=8,approvedDesignHashes=design,passiveNativeBoundaryAbsence=passive_native,forbiddenProductProbeHits=0,passiveHeldReaderSourceSha256=held_source_pin,passiveHeldReaderClassSha256=held_class_pin,rootRecoveryProbeAudit=root_rows,stages=stages,execSha256=raw['execSha256'],actualRootRecoveryOperations=0,actualFailedCohortCollectionOperations=0,actualJmsConnectionsCreated=0,actualMessagesRemoved=0,actualSecretKeysLoaded=False,cryptoOrKeyOperationsInvoked=False,ownThreadCount=0,effectDisclosureBasis='FULL_ORIGINAL_THROW_ONLY_PROXY_CALL_PATH_REVIEW_AND_EXACT_PASSIVE_PREFIXES_NOT_GLOBAL_OS_TRACE',newSourcePrograms=3,newPhysicalClasses=3,metadataPhysicalClasses=0,partialSourceProgramsMeasured=1,naturalZeroBranchSourceProgramsMeasured=3,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
