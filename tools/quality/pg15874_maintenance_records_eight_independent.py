"""Independent literal maintenance codec8 oracle; actual trace bytes and complete Source denominator."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15870_maintenance_records_eight_pt as original
import pg15872_maintenance_records_eight_post as post

PIN='deee7008abb150f9a857f063540e5ddca0691afa01cc0b2ebae2f975c2ee60d7'
OUT=data.BASE/'PG15874-maintenance-records-eight-independent-v1'
P='dev/codex/schubert/nk/batch/'
CLOSURES={P+'file/MaintenanceRecords':[P+'file/MaintenanceRecords'],P+'repository/MaintenanceCompletion':[P+'repository/MaintenanceCompletion',P+'repository/MaintenanceCompletion$Outcome']}
TOTALS={k:dict(covered=c,missed=m) for k,c,m in [('LINE',66,17),('METHOD',18,2),('CLASS',3,0),('BRANCH',21,0)]}
TRUE=['singleSession','officialGeneratedFiltersUnchanged','onlyPublicLiteralMaintenanceRecordContracts','testOwnedCwdTraceWrites','independentPublicRecordByteLiterals','ownEightThreadPoolUsed']
FALSE=['targetUnitFour100','allMeasuredApplicableCountersCovered','cryptoOrKeyOperationsInvoked','actualFilesOpenedByProduct','actualPrivateFilesOpened','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused','rootMainInvoked']
ZERO=['failures','errors','skipped','reruns','newAccepted','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']
def require(ok,message):
    if not ok:raise ValueError(message)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW and type(p['tests']) is int and p['tests']==8 and p['suites']==1,'same current source whole8')
    require(all(p[k] is True for k in TRUE) and all(p[k] is False for k in FALSE) and all(type(p[k]) is int and p[k]==0 for k in ZERO) and p['effortPercent'] is None,'typed reviewed literal scope without real lifecycle')
    require(p['strictFour100GateExit']==1 and p['crcMismatch']==0 and p['sessionIdentity']==original.SESSION and p['totals']==TOTALS,'strict partial Source remains HOLD despite branch100')
    names={n for group in CLOSURES.values() for n in group}
    require(p['completeSourceUnitClosure']==CLOSURES and set(p['fullSourceUnits'])==set(CLOSURES) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])==names,'full two Source/three Code denominator')
    require(p['metadataClasses']==p['manualCounterExclusions']==p['unexecutedCodeClasses']==[] and all(any(m['hasCode'] for m in row['methods']) for row in p['sourcePhysicalInventory'].values()),'no Code converted to metadata')
    require(all(type(v) is int for row in p['executable'].values() for c in row['counters'].values() for v in c.values()),'typed actual counters')
    require({k:{role:sum(r['counters'][k][role] for r in p['executable'].values()) for role in ['covered','missed']} for k in TOTALS}==TOTALS,'independent physical sums')
    codec=p['fullSourceUnits'][P+'file/MaintenanceRecords'];complete=p['fullSourceUnits'][P+'repository/MaintenanceCompletion']
    require(codec['four100'] is codec['threeCounter100'] is codec['branchNaturallyZero'] is False and codec['totals']['LINE']==dict(covered=49,missed=17) and codec['totals']['METHOD']==dict(covered=13,missed=2),'unexecuted retirement methods retained as 17line/2method missed')
    require(complete['four100'] is complete['threeCounter100'] is True and complete['branchNaturallyZero'] is False,'one complete two-Code Source only')
    require(len(p['owners'])==3 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==2 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==1,'existing Main ownership/unknown Test not inferred')
    require((p['concurrentRecordTasks'],p['concurrentWarningRecords'])==(64,32) and p['cryptoOperationKind']=='NONE_IN_REVIEWED_DOMAIN_BODY','deterministic own threads, no synthetic identity generation')
    require(p['forbiddenProductProbeHits']==0 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive scope boundaries')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN);raw=data.read_checked(data.BASE/'PG15870-maintenance-records-eight-pt-v1/manifest.json',post.RAW);post.assess(raw);assess(p)
    require(p['cases']==raw['cases'] and len({(r['classname'],r['name']) for r in p['cases']})==8,'eight actual unique original methods')
    identity='12345678-9abc-def0-8123-456789abcdef';activation='fedcba98-7654-3210-8fed-cba987654321'
    cutoff='2026-09-12T04:05:06.123456Z';end='2026-09-12T05:06:07.234567Z'
    done='NKDONE1\n'+identity+'\n'+cutoff+'\n'+activation+'\n'+end+'\n'
    expected={'PT-BAT-038-anchor.txt':('NKRUN1\n'+identity+'\n'+cutoff+'\n').encode('ascii'),'PT-BAT-038-activation.txt':('NKACT1\n'+identity+'\n'+cutoff+'\n'+activation+'\n').encode('ascii'),'PT-BAT-038-completion-0.txt':(done+'0\n').encode('ascii'),'PT-BAT-038-completion-10.txt':(done+'10\n').encode('ascii')}
    traces=post.RUN/'target/maintenance-record-traces';require({v.name for v in traces.iterdir()}==set(expected),'only four source-declared public synthetic traces')
    results=[]
    for name,bytes_expected in expected.items():
        file=traces/name;require(file.resolve()==file and not file.is_symlink() and file.read_bytes()==bytes_expected,'actual original output exactly independent literal, no Product expected generator')
        results.append(dict(testId='PT-BAT-038',name=name,bytes=len(bytes_expected),expectedSha256=data.sha(bytes_expected),actualSha256=data.sha(file.read_bytes()),equal=True))
    require(sorted(r['bytes'] for r in results)==[72,109,140,141],'independent literal record sizes')
    text=original.TESTS['MaintenanceRecordsTest'].read_text()
    require(text.count('@Test')==8,'original eight preserved')
    require(all(v in text for v in ['value < 256','assertEquals(64, actual.size())','assertEquals(32, warnings)','Executors.newFixedThreadPool(8)','future.get(5, TimeUnit.SECONDS)','for (Executable operation','failure.getSuppressed().length']) and 'UUID.randomUUID' not in text,'independent byte mutation, explicit null/parallel/redaction oracle')
    vectors=[('source','source','OLD'),('tests','tests',True),('totals','totals',{}),('closure','completeSourceUnitClosure',{}),('classes','physicalClasses',{}),('Code','sourcePhysicalInventory',{}),('metadata','metadataClasses',['X']),('exclude','manualCounterExclusions',['X']),('strict','strictFour100GateExit',0),('crc','crcMismatch',1),('owners','owners',{}),('tasks','concurrentRecordTasks',0),('warnings','concurrentWarningRecords',0),('effort','effortPercent',100)]
    vectors.extend((k,k,False) for k in TRUE);vectors.extend((k,k,True) for k in FALSE);vectors.extend((k,k,1) for k in ['newAccepted','actualVmActions'])
    labels=[]
    for label,key,value in vectors:
        require(json.dumps(p[key],sort_keys=True)!=json.dumps(value,sort_keys=True),'nondegenerate negative')
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false literal codec qualification '+label)
    verify(raw['begin']['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'independent-public-trace-oracles.json',results)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=8,suites=1,sourcePrograms=2,newSourcePrograms=2,physicalClasses=3,executablePhysicalClasses=3,metadataPhysicalClasses=0,four100SourcePrograms=1,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=1,semanticNegativeVectors=len(labels),negativeLabels=labels,publicTraceOracleCount=4,publicTraceOraclesSha256=data.sha((OUT/'independent-public-trace-oracles.json').read_bytes()),onlyPublicLiteralMaintenanceRecordContracts=True,testOwnedCwdTraceWrites=True,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualPrivateFilesOpened=False,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=8,semanticNegativeVectors=len(labels),newSourcePrograms=2,incompleteSourcePrograms=1)))
if __name__=='__main__':main()
