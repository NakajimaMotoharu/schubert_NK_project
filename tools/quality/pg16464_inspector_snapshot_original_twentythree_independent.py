"""Independent pure observation profile oracles, all23 original cases and whole Source counters."""
import copy
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg16460_inspector_snapshot_original_twentythree_pt as original
SOURCE=original.SOURCE
NAME=original.NAME
POST=('PG16462-inspector-snapshot-original-twentythree-post-v1','1a169f60c441da38c1e72a8147dc24bd80b47c6f3768e93cd467bf32900d2f5a')
RAW=('PG16460-inspector-snapshot-original-twentythree-pt-v1','53a2b8e9ce30a72bcd7e3155089ee9768bd791f4a58cde4102bc63eb5abd339a')
PREV=('PG16450-current2201-config-resource-registry-v1','1a5c0cce5b094ca859c66e83d74987ed4c65ef8c5c6a1ff89c88bf379b05e9b5')
OUT=data.BASE/'PG16464-inspector-snapshot-original-twentythree-independent-v1'
def require(ok,why):
    if not ok:raise ValueError(why)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p,raw,old=[read(v) for v in [POST,RAW,PREV]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [p,raw,old]),'genuine same source')
    texts={};expected=set()
    decl=old['currentOrdinaryTestDeclarationReference'];inventory=read(('PG15950-g13-current-test-declaration-inventory-v1',decl['inventoryManifestSha256']))
    bindings=data.read_checked(data.BASE/'PG15950-g13-current-test-declaration-inventory-v1/exact-ordinary-bindings.json',inventory['files']['exact-ordinary-bindings.json'])
    for name,path in original.TESTS.items():
        blob=path.read_bytes();require(data.sha(blob)==raw['begin']['testSourceHashes'][str(path)]==original.TEST_PINS[name],'unchanged whole original Test');texts[name]=blob.decode()
        methods=re.findall(r'@Test\s+void\s+(\w+)\(',texts[name]);require(len(methods)==original.COUNTS[name],'whole original method count')
        catalog={(v['className'],v['method']) for v in bindings if v['className']=='dev.codex.schubert.nk.batch.platform.'+name}
        local={('dev.codex.schubert.nk.batch.platform.'+name,n) for n in methods};require(local==catalog,'independent closed normal declarations');expected|=local
    actual=[]
    for file,pin in p['xmlHashes'].items():
        blob=(data.BASE/POST[0]/file).read_bytes();require(data.sha(blob)==pin,'original XML')
        xml=ET.fromstring(blob);require(all(xml.get(k)=='0' for k in ['failures','errors','skipped']),'FES0')
        for case in xml.findall('testcase'):require(not list(case),'no nonpass');actual.append((case.get('classname'),case.get('name')))
    require(len(actual)==23 and set(actual)==expected and not expected&{(v['classname'],v['name']) for v in old['cases']},'new current original23 no repeat credit')
    snapshot=texts['InspectorUnitSnapshotTest'];held=texts['InspectorHeldStateContractTest'];broker=texts['ArtemisUnitSnapshotTest']
    literal=re.search(r'static final String GOLDEN\s*=\s*("(?:[^"\\]|\\.)*");',snapshot)
    require(literal is not None,'manual golden declaration');golden=json.loads(literal.group(1)).encode('ascii')
    require(len(golden)==373 and hashlib.sha256(golden).hexdigest()==original.FIXTURES[original.GOLDEN] and golden==(data.ROOT/original.GOLDEN).read_bytes(),'independent literal bytes/length/hash, no Production expected')
    oracle_tokens=[
        (snapshot,['code == 1 && (status == 0 || status == 10)','code <= 6','status <= 255']),
        (snapshot,['"inactive/dead", "active/exited", "failed/failed"','active + "/" + sub']),
        (snapshot,['new int[] {0, 1, 10, 30, 70, 143, 255}','new int[] {0, 2, 3, 4, 5, 6}','assertEquals(status, state.normalExitCode())']),
        (snapshot,['"18446744073709551615"','"18446744073709551616"','"4294967296"','"9".repeat(21)']),
        (snapshot,['for (byte bad : new byte[] {0, 13, (byte) 128})','Collections.reverse(lines)','unknown.set(i, "Unknown=x")']),
        (snapshot,['actual previously captured receipt required','GC alone is no receipt','before.failedRootGeneration(null)','before.failedRootStillStoppedAfter(null)']),
        (snapshot,['Executors.newFixedThreadPool(8)','tasks.get(i).get(10, TimeUnit.SECONDS)','assertFalse(state.toString().contains(ID.toString()))']),
        (held,['"schubert-nk-morning-controller.service"','"schubert-nk-api.service"','"schubert-nk-web.service"','"artemis.service"']),
        (held,['"A completed-execution default is not a live daemon; SS341 SSC125 start>0/end0"','"143"','"70"','"30"']),
        (held,['"unknown-state"','"unknown-substate"','"unknown-result"','failed ? Optional.of(MorningBackupUnitCycle.Outcome.FAILED) : Optional.empty()']),
        (held,['original execution','snapshot911008StoppedGenerationRequiresAllFiveOriginalExecutionValues','snapshot911009StatusTenIsOnlyRecognizedForApprovedMaintenanceTargets']),
        (broker,['"MainPID=2147483648"','"MainPID=2147483647"','"Type=oneshot"','"Restart=no"','"RemainAfterExit=yes"']),
        (broker,['live data read is never empty-process authority','"InspectorUnitSnapshot[redacted]"','"Type=simple", "Restart=on-failure"'])]
    # Fixed method identity supplies the five-field oracle title; no free prose assumption.
    oracle_tokens[10]=(held,['snapshot911008StoppedGenerationRequiresAllFiveOriginalExecutionValues','Map.of(FIXTURE_EXECMAINSTATUS_179A8E0B, "30")','snapshot911009StatusTenIsOnlyRecognizedForApprovedMaintenanceTargets'])
    require(all(all(t in body for t in tokens) for body,tokens in oracle_tokens),'independent original literal/partition/boundary oracles')
    trace=(data.BASE/POST[0]/p['scalarTraceCopy']).read_bytes()
    expected_trace=b'quiescent=true\nreceipt=10\nsameInvocationReceipt=none\n'
    require(trace==expected_trace and data.sha(trace)==p['scalarTraceAtOriginalStageEndSha256']==raw['stages'][1]['scalarTraceAtOwnedStageEnd'][original.TRACE],'original stage-end trace identity, not post-first hash')
    design_hashes={}
    for number in ['341','343']:
        paths=list((data.ROOT/'documents/300_SS/340_batch・基盤').glob(number+'_*.md'));require(len(paths)==1,'unique approved design')
        relative=str(paths[0].relative_to(data.ROOT));approved=paths[0].read_bytes();require(approved==subprocess.check_output(['git','show','origin/main:'+relative],cwd=data.ROOT),'approved same byte');design_hashes[relative]=data.sha(approved)
    counts={k:dict(covered=c,missed=0) for k,c in [('LINE',222),('METHOD',34),('CLASS',2),('BRANCH',320)]}
    def contract(v):
        require(type(v['actualExit']) is int and v['actualExit']==0 and v['source']==SOURCE and v['originalManifestSha256']==RAW[1],'actual source/run')
        require((v['tests'],v['suites'],v['newTestIds'],v['targetSourceUnits'])==(23,3,0,1) and v['cases']==raw['cases'],'whole original23')
        require(v['completeSourceUnitClosure']==original.CLOSURES and set(v['physicalClasses'])==set(v['executable'])==set(original.CLOSURES[NAME]) and set(v['fullSourceUnits'])=={NAME} and v['metadataClasses']==[],'exact complete two Code keysets')
        require(v['totals']==v['fullSourceUnits'][NAME]['totals']==counts and all(c['missed']==0 for row in v['executable'].values() for c in row['counters'].values()),'all Source counters no miss')
        require(v['singleSession'] is True and v['crcMismatch']==0 and v['strictFour100GateExit']==0 and v['targetUnitFour100'] is v['allMeasuredApplicableCountersCovered'] is True and v['manualCounterExclusions']==[],'one actual full exec no exclusions')
        require(v['cryptoOrKeyOperationsInvoked'] is v['publicDigestOnly'] is v['testPublicUnitSourceRead'] is v['testOwnScalarTraceWritten'] is v['syntheticStateFieldsOnly'] is True,'honest test SHA/public-read/own-write disclosure')
        require(v['scalarTraceAtOriginalStageEndSha256']==data.sha(expected_trace) and v['publicUnitSourceSha256']==original.PUBLIC_UNIT_SHA and v['rootRecoveryProbeAudit'] and all(r['trueProbeHits']==0 for r in v['rootRecoveryProbeAudit'].values()),'bounded trace/public input and no Root authority probes')
        require(v['actualRootRecoveryOperations']==v['actualFailedCohortCollectionOperations']==0 and v['ownThreadCount'] is None and v['declaredOwnWorkerPoolSize']==8 and v['ownTaskCount']==64,'pure fields/declared own tasks not actual Root/cohort operations')
        require(all(v[k] is False for k in ['actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','oldCoverageTransferred','formalUpdated','whole451Accepted']) and v['effortPercent'] is None,'no authority/formal transfer')
    contract(p);labels=[]
    for key,value in [('actualExit',True),('source','OLD'),('originalManifestSha256','0'*64),('tests',24),('suites',2),('newTestIds',1),('targetSourceUnits',2),('cases',[]),('completeSourceUnitClosure',{}),('physicalClasses',{}),('fullSourceUnits',{}),('executable',{}),('metadataClasses',[NAME]),('totals',{}),('singleSession',False),('crcMismatch',1),('strictFour100GateExit',1),('targetUnitFour100',False),('allMeasuredApplicableCountersCovered',False),('manualCounterExclusions',[NAME]),('cryptoOrKeyOperationsInvoked',False),('testPublicUnitSourceRead',False),('testOwnScalarTraceWritten',False),('scalarTraceAtOriginalStageEndSha256','0'*64),('rootRecoveryProbeAudit',{}),('actualRootRecoveryOperations',1),('actualFailedCohortCollectionOperations',1),('ownThreadCount',8),('actualSecretKeysLoaded',True),('formalUpdated',True),('effortPercent',100)]:
        bad=copy.deepcopy(p);bad[key]=value
        try:contract(bad)
        except ValueError:labels.append(key)
        else:raise ValueError('false observation qualification '+key)
    for v in [p,old]:verify(v['invocation'])
    verify(raw['begin']['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,postSha256=POST[1],rawSha256=RAW[1],tests=23,suites=3,semanticNegativeVectors=len(labels),negativeLabels=labels,independentOracleVectors=len(oracle_tokens),newSourcePrograms=1,newPhysicalClasses=2,metadataPhysicalClasses=0,four100SourcePrograms=1,wholeSourceIncompleteCount=0,originalGoldenBytes=373,originalGoldenSha256=data.sha(golden),approvedDesignHashes=design_hashes,scalarTraceAtOriginalStageEndSha256=data.sha(trace),cryptoOrKeyOperationsInvoked=True,actualSecretKeysLoaded=False,actualRootRecoveryOperations=0,actualFailedCohortCollectionOperations=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
