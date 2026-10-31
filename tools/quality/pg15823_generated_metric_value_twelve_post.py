"""Full supplemental measurement of original generated values12; five prior Source proofs unchanged."""
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
import pg15820_generated_metric_value_twelve_pt as original
import typed_marker_guard_qualified_v1 as cfg
import pg9666_pagination_static as runner
from trace_owner_join import canonical

RAW='0d20fa3da66eae1885864237d777f4626bdc9d8aefc443f58e65280c886a29d3'
RUN=data.ROOT.parent/'pgpt-runs/PG379/pg15820-generated-metric-value-twelve-pt-v1'
OUT=data.BASE/'PG15823-generated-metric-value-twelve-post-v2'
SLOT=data.ROOT.parent/'pgpt-runs/PG379/pg15823-generated-metric-value-twelve-post-v2'
PREFIX='dev/codex/schubert/nk/'
MAINS={"api/monitoring/DbPoolMetricRecorder":"11a8f25926ef4727e019349b1965b97c456eb46f5f82d2697506610f12e4241c","api/monitoring/OutboxRowsMetricRecorder":"c0d709475517e31192afe8486be24f7a88232a87dd43d0db4e77ce34dd78a7d5","api/monitoring/AsyncJobMetricRecorder":"bcbe814f37ba7a9cdba482369fa7ab70c5688713249ab780c35b6eeba3190cd6","api/monitoring/OperationMismatchMetricRecorder":"74cef118229b3163b561702d8001e9cd0509bcc6ff6d6a56d2ccccf98de9de55","web/monitoring/HttpMetricContract":"019f126d38fdfbfd60baf8f38c254201db2427e7a0c2087e052712812a889c03"}
CLOSURES={"api/monitoring/DbPoolMetricRecorder":["api/monitoring/DbPoolMetricRecorder","api/monitoring/DbPoolMetricRecorder$Counts","api/monitoring/DbPoolMetricRecorder$State"],"api/monitoring/OutboxRowsMetricRecorder":["api/monitoring/OutboxRowsMetricRecorder","api/monitoring/OutboxRowsMetricRecorder$Counts","api/monitoring/OutboxRowsMetricRecorder$Status"],"api/monitoring/AsyncJobMetricRecorder":["api/monitoring/AsyncJobMetricRecorder","api/monitoring/AsyncJobMetricRecorder$Snapshot","api/monitoring/AsyncJobMetricRecorder$State"],"api/monitoring/OperationMismatchMetricRecorder":["api/monitoring/OperationMismatchMetricRecorder","api/monitoring/OperationMismatchMetricRecorder$Operation"],"web/monitoring/HttpMetricContract":["web/monitoring/HttpMetricContract","web/monitoring/HttpMetricContract$Labels","web/monitoring/HttpMetricContract$Method","web/monitoring/HttpMetricContract$Metric","web/monitoring/HttpMetricContract$Route","web/monitoring/HttpMetricContract$Status"]}
METADATA=set()
NAMES=[PREFIX+n for n in MAINS]
TOTAL=12
UNEXECUTED=set(NAMES)|{PREFIX+'api/monitoring/AsyncJobMetricRecorder$Snapshot'}
def assess(raw):
    validator.common.SOURCE=original.SOURCE;validator.COUNTS=original.COUNTS;validator.EXPECTED_FIXTURE_HASHES={};validator.assess(raw)

def main():
    invocation=capture(__file__);assert isinstance(RAW,str) and len(RAW)==64 and not SLOT.exists() and not OUT.exists()
    raw=data.read_checked(data.BASE/'PG15820-generated-metric-value-twelve-pt-v1/manifest.json',RAW)
    assert data.sha((RUN/'manifest.safe.json').read_bytes())==RAW;assess(raw)
    normal,normal_pin=cfg.normal();hashes=normal['begin']['inputHashes'];snapshot=original.COMPILE/'snapshot'
    static_pin='294810b2dab116dbc73bdf41ee39940378f89e173f8100a6109ff5571f3e159e'
    static=data.read_checked(cfg.out(cfg,14224)/'manifest.json',static_pin)
    assert raw['source']==normal['source']==static['source']==original.SOURCE
    assert normal['actualExit']==static['actualExit']==normal['testsExecuted']==0
    assert hashes==raw['begin']['sourceHashes'] and all(hashes[original.main_path(n)]==h for n,h in MAINS.items())
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
    for name in NAMES:
        with zipfile.ZipFile(normal['jars'][original.module(name[len(PREFIX):])]['path']) as jar:
            group={v[:-6] for v in jar.namelist() if v==name+'.class' or v.startswith(name+'$') and v.endswith('.class')}
            assert group=={PREFIX+n for n in CLOSURES[name[len(PREFIX):]]}
            closure[name]=sorted(group)
            for physical_name in group:
                path=snapshot/('src/schubert-nk-'+original.module(name[len(PREFIX):])+'/target/classes')/(physical_name+'.class')
                assert jar.read(physical_name+'.class')==path.read_bytes()
                decoded=code.decode(path.read_bytes(),physical_name+'.class')
                if physical_name in METADATA:
                    assert decoded['flags']==(1537 if physical_name==PREFIX+'mq/ArtemisManagementReadinessClient$OwnedOperation' else 1536) and decoded['methods'] and not any(m['hasCode'] for m in decoded['methods'])
                else:assert any(m['hasCode'] for m in decoded['methods'])
                paths[physical_name]=path;inventory[physical_name]=dict(sha256=data.sha(path.read_bytes()),flags=decoded['flags'],sourceFile=decoded['sourceFile'],methods=decoded['methods'])
    assert len(closure)==5 and len(paths)==17
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    main_paths=[original.main_path(name[len(PREFIX):]) for name in NAMES]
    owners={path:dict(sha256=hashes[path],**canonical(path,logical)) for path in [*main_paths,*[str(v.relative_to(data.ROOT)) for v in original.TESTS.values()]]}
    previous=data.read_checked(data.BASE/'PG15810-current2031-web-identity-registry-v1/manifest.json','49c59a5f449b1da48a00abd6461db5deda2ee9e64b98029c03201fd199d9416b')
    assert all(owners[path]==previous['owners'][path] for path in main_paths)
    prior_proofs={name:previous['fullSourceUnits'][name] for name in NAMES}
    assert len(prior_proofs)==5 and all(v['four100'] is True for v in prior_proofs.values())
    SLOT.mkdir();runner.SLOT=SLOT;component=SLOT/'component';component.mkdir()
    physical={}
    for name,path in paths.items():
        target=component/(name+'.class');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
        physical[name]=data.sha(path.read_bytes());assert data.sha(target.read_bytes())==physical[name]
    data.write(SLOT/'begin.safe.json',dict(source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,execSha256=raw['execSha256'],normalManifestSha256=normal_pin,physicalClasses=physical,priorProductResultsReused=False,productTestsReexecuted=0))
    diagnostic=data.ROOT/'tools/quality/architecture/WholeSourceCoverageMeasureV1.java'
    diagnostic_pin='97cecbbff82e9c93d41f13e94872b792f374f84d34973a930daefb79bb7be260'
    assert data.sha(diagnostic.read_bytes())==diagnostic_pin
    classes=data.ROOT.parent/'pgpt-runs/PG379/pg15713-caddy-public-value-nine-post-v2/diagnostic-classes'
    diagnostic_class_pin='9977e1c733e40e4752261c38e6a679a91cf2d33b6d2be72180e1f67af01a94a3'
    assert data.sha((classes/'WholeSourceCoverageMeasureV1.class').read_bytes())==diagnostic_class_pin
    reader_qualification=data.read_checked(data.BASE/'PG15714-caddy-public-value-nine-independent-v1/manifest.json','d3900d79c6dc63338d18804f0b4aaa05fc00e1f88dcbe54451aba898cc565242')
    assert reader_qualification['actualExit']==0 and reader_qualification['passiveReaderNegativeChecks']==5
    jdk=runner.TC/'jdk-25.0.4/bin';stages=[]
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
    for label,command in [('session-identity',[str(jdk/'java'),'-cp',cp,'CoverageSessionIdentity',str(RUN/'jacoco.exec'),original.SESSION]),('coverage-audit',[str(jdk/'java'),'-cp',str(classes)+os.pathsep+cp,'WholeSourceCoverageMeasureV1',str(RUN/'jacoco.exec'),str(component),*sorted(set(physical)-METADATA-UNEXECUTED),*["--unexecuted="+n for n in sorted(UNEXECUTED)],*["--metadata="+n for n in sorted(METADATA)]])]:
        stage=runner.step(label,command,SLOT,timeout=120);stages.append(stage);data.write(SLOT/(label+'-stage.safe.json'),stage);assert stage['actualExit']==0 and not stage['timedOut']
    data.write(SLOT/'audit-stages.safe.json',stages);rows={};observed_metadata=[];observed_unexecuted=[]
    for line in (SLOT/'coverage-audit.stdout').read_text().splitlines():
        fields=line.split('\t')
        if fields[0]=='CLASS':rows[fields[1]]=dict(crc64=fields[2],counters={v.split(':')[0]:dict(missed=int(v.split(':')[1]),covered=int(v.split(':')[2])) for v in fields[3:]})
        if fields[0]=='UNEXECUTED_CODE':observed_unexecuted.append(fields[1])
        if fields[0]=='METADATA':observed_metadata.append(fields[1])
    assert set(observed_unexecuted)==UNEXECUTED and len(observed_unexecuted)==6 and all(v['covered']==0 for n in UNEXECUTED for v in rows[n]['counters'].values())
    assert set(observed_metadata)==METADATA and len(observed_metadata)==0
    assert set(rows)==set(paths)-METADATA and all(set(v['counters'])=={'LINE','METHOD','CLASS','BRANCH'} for v in rows.values())
    def counters(names):return {k:dict(missed=sum(rows[n]['counters'][k]['missed'] for n in names if n in rows),covered=sum(rows[n]['counters'][k]['covered'] for n in names if n in rows)) for k in ['LINE','METHOD','CLASS','BRANCH']}
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
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,originalManifestSha256=RAW,normalManifestSha256=normal_pin,staticPostManifestSha256=static_pin,tests=TOTAL,suites=len(original.COUNTS),failures=0,errors=0,skipped=0,reruns=0,newTestIds=0,newAccepted=0,sourceChanged=False,
      targetSourceUnits=5,completeSourceUnitClosure=closure,sourcePhysicalInventory=inventory,fullSourceUnits=full,metadataClasses=sorted(METADATA),manualCounterExclusions=[],officialGeneratedFiltersUnchanged=True,helperSourceProgramsNotAcceptedByTheseTargetCounters=True,completeSourceCoverageMeasured=True,naturalZeroBranch=natural_branch,branchPercent=None if natural_branch else 100*totals['BRANCH']['covered']/(totals['BRANCH']['covered']+totals['BRANCH']['missed']),branchReason='MEASURED_FULL_SOURCE_WITHOUT_MANUAL_EXCLUSION',targetUnitFour100=four100,allMeasuredApplicableCountersCovered=applicable,strictFour100GateExit=0 if four100 else 1,
      cases=raw['cases'],xmlHashes=raw['xmlHashes'],execSha256=raw['execSha256'],singleSession=True,sessionIdentity=original.SESSION,crcMismatch=0,physicalClasses=physical,executable=rows,totals=totals,stages=stages,owners=owners,registryChanged=False,metadataNegativeVectors=len(labels),negativeLabels=labels,reusedToolRuntimeOnly=True,newPassiveReaderCompiled=False,reusedSuccessfulPassiveStageLabels=[],previousPassiveCoverageFailureRetained=False,passiveCoverageReaderSourceSha256=diagnostic_pin,passiveCoverageReaderClassSha256=diagnostic_class_pin,unexecutedCodeClasses=sorted(UNEXECUTED),unexecutedCodeIncludedInAllDenominators=True,toolRuntimeManifestSha256='adcb55b80aa70a449e74280aa465f752308310c41c876cf83a5a78c3dda3c882',priorProductResultsReused=False,productTestsReexecutedByPost=0,oldCoverageTransferred=False,whole451Accepted=False,wholeF03Accepted=False,formalUpdated=False,effortPercent=None,actualVmActions=0,actualDatabaseActions=0,actualServiceActions=0,actualNetworkActions=0,childLocalJcaRegistryRestorationTested=False,ownedJcaProviderOrderRestored=None,ownFreshJvmProviderStateOnly=False,cryptoOrKeyOperationsInvoked=False,cryptoOperationKind='NONE_IN_REVIEWED_DOMAIN_BODY',publicSyntheticTestKeysUsed=False,publicNonSecretCanonicalConfigDigestOnly=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,onlyReviewedPureValueSuites=False,onlyInjectedArtemisReaders=False,onlySyntheticWebRequestIdentityContracts=False,syntheticMockServletAttributesOnly=False,literalRequestUuidFixtures=False,onlyGeneratedMetricValueContracts=True,jdkNonCryptographicHashVectorsOnly=True,meterRegistryOrRecorderConstructed=False,actualCollectorOrExporterStarted=False,noOuterRecorderMethodInvocations=True,uuidSupplierGeneratedValues=False,systemLoggerFactoryUsed=False,actualAuditRecordsWritten=0,auditRecordInvoked=False,publicSyntheticFixtureCredentialsUsed=False,actualHttpSessionsIssued=0,actualApiAuthenticationGrantsIssued=0,currentTargetPriorSourceProofs=prior_proofs,targetSourcesAlreadyQualified=5,previousSourceProofsNotReplaced=True,actualBorrowedCoreSessionMethodsInvoked=0,actualManagementOperationsInvoked=0,actualParentDeadlineOperationsInvoked=0,outerStartupObservationInvoked=False,unusedCoreSessionProxyConstructed=False,onlyPreSqlZeroJdbcCallContracts=False,sameExecMeasurementSupplementalOnly=True,currentSourceQualificationProofsReplaced=False,actualJdbcBackendConnected=False,actualJdbcMethodsInvoked=0,actualSqlStatementsPreparedOrExecuted=0,actualJdbcProxyObjectsConstructed=False,unselectedOriginalGoldenHelperMethods=0,unselectedOriginalGoldenHelperMethodsExecuted=0,numericIpv6LiteralParsingOnly=False,numericIpLiteralParsingOnly=False,actualDnsRequestsIssued=False,actualFilesOpenedByProduct=False,immutablePackagedTemplateResourcesRead=False,actualPrivateFilesOpened=False,testOwnNewSlotPublicEvidenceWrites=False,mockMvcOnly=False,jmsFactoryObjectsConstructed=False,onlyCredentialFreeUnconnectedLocators=False,onlySyntheticJmsProxyMessages=False,jmsDestinationValueObjectsConstructed=False,actualJmsConnectionsCreated=0,actualJmsContextsCreated=0,actualBrokerOrListenerStarted=False,actualBoundSockets=0,actualBrowserActions=0,characterizationAccepted=False,packagedResourceHashes={},effectDisclosureDomain='REVIEWED_PRODUCT_AND_ORIGINAL_TEST_BODY_NOT_EVIDENCE_HASHING_OR_SDK_INTERNAL_BOOTSTRAP',forbiddenProductProbeHits=0,passiveHeldReaderSourceSha256=held_source_pin,passiveHeldReaderClassSha256=held_class_pin,passiveHeldReaderRuntimeReference='9653028e361d41a2b0793e485797ff93c00c4500acf9a06249a54c2f1179c84e',passiveNativeBoundaryAbsence=passive_native,reportedEnvironment=raw['stages'][1]['reportedEnvironment'],rootMainInvoked=False))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=TOTAL,suites=len(original.COUNTS),totals=totals,crcMismatch=0,singleSession=True,naturalBranchNA=natural_branch)))
if __name__=='__main__':main()
