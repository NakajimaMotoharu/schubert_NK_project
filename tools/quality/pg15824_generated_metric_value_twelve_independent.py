"""Independent generated values12 JDK hash/literal oracle; all prior Source qualifications immutable."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
import pg15820_generated_metric_value_twelve_pt as original
import pg15823_generated_metric_value_twelve_post as post

PIN='d6443771465d6c1e12c31e52fac3eb45987ffe8ae1d25186b4f62d792013f6c9'
OUT=data.BASE/'PG15824-generated-metric-value-twelve-independent-v1'
P='dev/codex/schubert/nk/'
CLOSURES={"api/monitoring/DbPoolMetricRecorder":["api/monitoring/DbPoolMetricRecorder","api/monitoring/DbPoolMetricRecorder$Counts","api/monitoring/DbPoolMetricRecorder$State"],"api/monitoring/OutboxRowsMetricRecorder":["api/monitoring/OutboxRowsMetricRecorder","api/monitoring/OutboxRowsMetricRecorder$Counts","api/monitoring/OutboxRowsMetricRecorder$Status"],"api/monitoring/AsyncJobMetricRecorder":["api/monitoring/AsyncJobMetricRecorder","api/monitoring/AsyncJobMetricRecorder$Snapshot","api/monitoring/AsyncJobMetricRecorder$State"],"api/monitoring/OperationMismatchMetricRecorder":["api/monitoring/OperationMismatchMetricRecorder","api/monitoring/OperationMismatchMetricRecorder$Operation"],"web/monitoring/HttpMetricContract":["web/monitoring/HttpMetricContract","web/monitoring/HttpMetricContract$Labels","web/monitoring/HttpMetricContract$Method","web/monitoring/HttpMetricContract$Metric","web/monitoring/HttpMetricContract$Route","web/monitoring/HttpMetricContract$Status"]}
TOTALS={k:dict(covered=c,missed=m) for k,c,m in [('LINE',110,176),('METHOD',16,53),('CLASS',11,6),('BRANCH',9,86)]}
TRUE_FIELDS=['singleSession','officialGeneratedFiltersUnchanged','unexecutedCodeIncludedInAllDenominators','onlyGeneratedMetricValueContracts','jdkNonCryptographicHashVectorsOnly','noOuterRecorderMethodInvocations','sameExecMeasurementSupplementalOnly','previousSourceProofsNotReplaced']
FALSE_FIELDS=['targetUnitFour100','allMeasuredApplicableCountersCovered','meterRegistryOrRecorderConstructed','actualCollectorOrExporterStarted','cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused','currentSourceQualificationProofsReplaced']
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p,old,logical):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW and type(p['tests']) is int and p['tests']==12 and type(p['suites']) is int and p['suites']==2,'genuine original12/2')
    require(all(p[k] is True for k in TRUE_FIELDS) and all(p[k] is False for k in FALSE_FIELDS) and p['effortPercent'] is None,'exact effects and no qualification replacement')
    require(all(type(p[k]) is int and p[k]==0 for k in ['newAccepted','failures','errors','skipped','reruns','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']),'no failed/skipped accepted/live operation')
    require(p['strictFour100GateExit']==1 and p['crcMismatch']==0 and p['sessionIdentity']=='PG15820-GENERATED-METRIC-VALUE-WHOLE12','real partial scope gate/session/CRC')
    expected={P+n:sorted(P+q for q in group) for n,group in CLOSURES.items()};physical={n for group in expected.values() for n in group}
    require(p['completeSourceUnitClosure']==expected and set(p['fullSourceUnits'])==set(expected) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])==physical and len(physical)==17,'five complete Source/seventeen Code')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and all(any(m['hasCode'] for m in v['methods']) for v in p['sourcePhysicalInventory'].values()),'no true Code omitted/NoCode forged')
    unexecuted=set(expected)|{P+'api/monitoring/AsyncJobMetricRecorder$Snapshot'}
    require(set(p['unexecutedCodeClasses'])==unexecuted and len(p['unexecutedCodeClasses'])==6 and all(v['covered']==0 for n in unexecuted for v in p['executable'][n]['counters'].values()),'six genuinely unexecuted Code in all denominators')
    require(all(type(v) is int for row in p['executable'].values() for counter in row['counters'].values() for v in counter.values()),'typed genuine counters')
    totals={k:{role:sum(row['counters'][k][role] for row in p['executable'].values()) for role in ['covered','missed']} for k in TOTALS}
    require(wire(totals)==wire(p['totals'])==wire(TOTALS),'independent measured scope sums')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==expected[name] and all(u[k] is False for k in ['four100','metadataOnly','branchNaturallyZero','threeCounter100']),'five partial scope units not whole qualification')
        require(u['totals']=={k:{role:sum(p['executable'][n]['counters'][k][role] for n in u['physical']) for role in ['covered','missed']} for k in totals},'independent per-source sums')
    require(p['targetSourcesAlreadyQualified']==5 and set(p['currentTargetPriorSourceProofs'])==set(expected) and all(u==old['fullSourceUnits'][n] and u['four100'] is True for n,u in p['currentTargetPriorSourceProofs'].items()),'all five previous four100 proofs immutable, new scope separate')
    require(len(p['owners'])==7 and all(row['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' and row['canonicalOwner']==row['canonicalCostOwner']=='WBS-P018-09' and all(row[k]==v for k,v in canonical(path,logical).items()) for path,row in p['owners'].items()),'seven actual candidate roles not promoted to baseline/accepted')
    require(all(path not in old['owners'] or row==old['owners'][path] for path,row in p['owners'].items()),'old owner rows unchanged')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(v['actualExit']==0 and not v['timedOut'] for v in p['stages']),'passive held/native checks actual0')
def jint(value):return (value+2**31)%2**32-2**31
def long_hash(value):return jint((value^(value>>32))&0xffffffff)
def record_hash(values):
    h=0
    for v in values:h=jint(31*h+long_hash(v))
    return h
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN);raw=data.read_checked(data.BASE/'PG15820-generated-metric-value-twelve-pt-v1/manifest.json',post.RAW);post.assess(raw)
    old=data.read_checked(data.BASE/'PG15810-current2031-web-identity-registry-v1/manifest.json','49c59a5f449b1da48a00abd6461db5deda2ee9e64b98029c03201fd199d9416b')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    assess(p,old,logical)
    require(p['cases']==raw['cases'] and len({(c['classname'],c['name']) for c in p['cases']})==12 and not {(c['classname'],c['name']) for c in p['cases']}&{(c['classname'],c['name']) for c in old['cases']},'twelve genuinely new methods, no old replay')
    api=original.TESTS['GeneratedMetricValueContractTest'].read_text();web=original.TESTS['GeneratedWebValueContractTest'].read_text()
    require(api.count('@Test')==8 and web.count('@Test')==4 and all(v in api for v in ['assertEquals(94248, actual.hashCode())','assertEquals(3040, actual.hashCode())','assertEquals(0, maximum.hashCode())','assertEquals(Integer.MIN_VALUE, maximum.hashCode())','Counts[active=3, idle=5, pending=2, maximum=8]','Counts[pending=3, sent=5, error=2]','Long.MAX_VALUE','assertTrue(actual.equals(sameInstance))','assertFalse(actual.equals(absent))','assertFalse(actual.equals(otherType))','State.valueOf(null)','Status.valueOf(null)','Operation.valueOf(null)','copy[0]']), 'original fixed API hash/equality/getter/text/enum-negative/copy assertions')
    require(all(v in web for v in ['System.identityHashCode(Route.LOGIN)','System.identityHashCode(Method.POST)','System.identityHashCode(Status.SUCCESS)','Labels[route=LOGIN, method=POST, status=SUCCESS]','assertEquals(expected, actual.hashCode())','lookup.apply("UNKNOWN_ENUM")','lookup.apply(null)','actual[0] = expected.getLast().constant()','assertSame(expected.getFirst().constant(), values.get()[0])','e("ROOT", Route.ROOT)','e("UNKNOWN", Route.UNKNOWN)']),'independent public Web value oracle, not Main expected')
    vectors_hash={'pool':record_hash([3,5,2,8]),'outbox':record_hash([3,5,2]),'max4':record_hash([2**63-1]*4),'max3':record_hash([2**63-1]*3),'zero':record_hash([0,0,0])}
    require(vectors_hash=={'pool':94248,'outbox':3040,'max4':0,'max3':-2147483648,'zero':0},'independent JDK25 signed-long hash vectors')
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/1652_API生成Value契約_実Jar・品質追跡.md'
    spec_pin='f04a8e384c43dbc91b333f3f8722a8974d2c8b397bc4469517441a6098ec8b38'
    require(data.sha(spec.read_bytes())==spec_pin and '生成21method契約' in spec.read_text() and 'counter52methodへ21を加算0' in spec.read_text(),'official generated filters unchanged, semantic cases separate from coverage methods')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('tests','tests',11),('bool-tests','tests',True),('suites','suites',1),('closure','completeSourceUnitClosure',{}),('physical','physicalClasses',{}),('units','fullSourceUnits',{}),('inventory','sourcePhysicalInventory',{}),('executable','executable',{}),('metadata','metadataClasses',['X']),('exclude','manualCounterExclusions',['X']),('unexecuted','unexecutedCodeClasses',[]),('totals','totals',{}),('prior-proof','currentTargetPriorSourceProofs',{}),('already-qualified','targetSourcesAlreadyQualified',0),('owners','owners',{}),('strict','strictFour100GateExit',0),('crc','crcMismatch',1),('effort','effortPercent',100),('accepted','newAccepted',1)]
    vectors.extend((k,k,False) for k in TRUE_FIELDS)
    vectors.extend((k,k,True) for k in FALSE_FIELDS)
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad,old,logical)
        except ValueError:labels.append(label)
        else:raise ValueError('false generated value qualification '+label)
    for label,change in [('candidate-to-baseline',lambda b:next(iter(b['owners'].values())).update(ownershipStatus='BASELINE_LOGICAL_REFERENCE')),('canonical-owner-changed',lambda b:next(iter(b['owners'].values())).update(canonicalOwner='WBS-F03'))]:
        bad=copy.deepcopy(p);change(bad)
        try:assess(bad,old,logical)
        except ValueError:labels.append(label)
        else:raise ValueError('BUG2149 role regression')
    for v in [raw['begin'],p,old]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=12,suites=2,sourcePrograms=5,newSourcePrograms=0,physicalClasses=17,executablePhysicalClasses=17,metadataPhysicalClasses=0,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=5,baselineMainOwnerRows=0,candidateMainOwnerRows=5,candidateTestOwnerRows=2,unknownTestOwnerRows=0,semanticNegativeVectors=len(labels),negativeLabels=labels,previousQualifiedSourcePrograms=5,previousSourceProofsNotReplaced=True,previousSourceProofs=p['currentTargetPriorSourceProofs'],sameExecMeasurementSupplementalOnly=True,onlyGeneratedMetricValueContracts=True,jdkNonCryptographicHashVectorsOnly=True,meterRegistryOrRecorderConstructed=False,actualCollectorOrExporterStarted=False,noOuterRecorderMethodInvocations=True,independentHashVectors=vectors_hash,priorIndependentSpecPath=str(spec.relative_to(data.ROOT)),priorIndependentSpecSha256=spec_pin,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=12,semanticNegativeVectors=len(labels),newSourcePrograms=0,priorSourcesPreserved=5)))
if __name__=='__main__':main()
