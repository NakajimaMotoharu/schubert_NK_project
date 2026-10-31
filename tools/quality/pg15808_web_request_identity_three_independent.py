"""Independent original Mock identity3 oracle and complete four-source measured denominator."""
import copy
import json
import uuid
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15804_web_request_identity_three_pt as original
import pg15806_web_request_identity_three_post as post

PIN='d6011b2c5768a404b9ecfa9dfacd7527eb3e0e00367f8095bbd45dc7ad7d1349'
OUT=data.BASE/'PG15808-web-request-identity-three-independent-v1'
P='dev/codex/schubert/nk/web/'
CLOSURES={'security/WebRequestContext':['security/WebRequestContext'],'security/CaddyTransportContextFilter':['security/CaddyTransportContextFilter'],'security/CaddyClientAddressResolver':['security/CaddyClientAddressResolver'],'logging/WebSecurityAudit':['logging/WebSecurityAudit','logging/WebSecurityAudit$Event','logging/WebSecurityAudit$Route']}
TOTALS={k:dict(covered=c,missed=m) for k,c,m in [('LINE',93,83),('METHOD',16,9),('CLASS',5,1),('BRANCH',26,68)]}
TRUE_FIELDS=['singleSession','officialGeneratedFiltersUnchanged','unexecutedCodeIncludedInAllDenominators','onlySyntheticWebRequestIdentityContracts','syntheticMockServletAttributesOnly','literalRequestUuidFixtures','numericIpLiteralParsingOnly','systemLoggerFactoryUsed','previousHelpersNotReaccepted']
FALSE_FIELDS=['targetUnitFour100','allMeasuredApplicableCountersCovered','metadataOnly','uuidSupplierGeneratedValues','auditRecordInvoked','publicSyntheticFixtureCredentialsUsed','cryptoOrKeyOperationsInvoked','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused']
ZERO_FIELDS=['failures','errors','skipped','reruns','newAccepted','actualAuditRecordsWritten','actualHttpSessionsIssued','actualApiAuthenticationGrantsIssued','actualBorrowedCoreSessionMethodsInvoked','actualManagementOperationsInvoked','actualParentDeadlineOperationsInvoked','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW and type(p['tests']) is int and p['tests']==3 and type(p['suites']) is int and p['suites']==1,'genuine original source/3/1')
    require(all(p[k] is True for k in TRUE_FIELDS) and all(p[k] is False for k in FALSE_FIELDS if k!='metadataOnly') and all(type(p[k]) is int and p[k]==0 for k in ZERO_FIELDS) and p['effortPercent'] is None,'typed genuine effects/not formal acceptance')
    require(p['strictFour100GateExit']==1 and p['crcMismatch']==0 and p['sessionIdentity']=='PG15804-WEB-REQUEST-IDENTITY-WHOLE3','strict real missed gate/session/CRC')
    expected={P+n:sorted(P+q for q in group) for n,group in CLOSURES.items()};physical={n for group in expected.values() for n in group}
    require(p['completeSourceUnitClosure']==expected and set(p['fullSourceUnits'])==set(expected) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])==physical and len(physical)==6,'four complete Source/six Code, no omitted physical')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and all(any(m['hasCode'] for m in row['methods']) for row in p['sourcePhysicalInventory'].values()),'no Code converted to NoCode')
    require(p['unexecutedCodeClasses']==[P+'logging/WebSecurityAudit$Route'] and p['executable'][P+'logging/WebSecurityAudit$Route']['counters']=={k:dict(covered=0,missed=m) for k,m in [('LINE',9),('METHOD',2),('CLASS',1),('BRANCH',0)]},'unloaded Route full missed denominator')
    require(all(type(x) is int for row in p['executable'].values() for counter in row['counters'].values() for x in counter.values()),'typed counters')
    total={k:{role:sum(row['counters'][k][role] for row in p['executable'].values()) for role in ['covered','missed']} for k in TOTALS}
    require(wire(total)==wire(p['totals'])==wire(TOTALS),'independent whole denominator sums')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==expected[name] and all(u[k] is False for k in ['four100','metadataOnly','branchNaturallyZero','threeCounter100']),'four incomplete sources not accepted')
        require(u['totals']=={k:{role:sum(p['executable'][n]['counters'][k][role] for n in u['physical']) for role in ['covered','missed']} for k in total},'independent source sums')
    require(len(p['helperPreviousSourceProofs'])==1 and p['helperPreviousSourceProofs'][P+'security/LoginClientAddress']['four100'] is True,'previous Address qualification not replaced')
    require(len(p['owners'])==6 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==5 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==1,'four Main plus old helper and unknown Test')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive terminals and no held/native hit')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN);raw=data.read_checked(data.BASE/'PG15804-web-request-identity-three-pt-v1/manifest.json',post.RAW);post.assess(raw);assess(p)
    require(p['cases']==raw['cases'] and len({(c['classname'],c['name']) for c in p['cases']})==3,'unchanged original actual cases')
    old=data.read_checked(data.BASE/'PG15794-current2028-acceptor-json-registry-v1/manifest.json','d1484938af6778e1d3e019eb792de2d60d094ef56c10f56c425788a80f4396b3')
    require(all(old['fullSourceUnits'][n]==u for n,u in p['helperPreviousSourceProofs'].items()) and not set(p['fullSourceUnits'])&old['fullSourceUnits'].keys(),'old helpers exact and new Source disjoint')
    text=original.TESTS['WebRequestIdentityConsistencyTest'].read_text()
    ids=['00000000-0000-4000-8000-00000000000'+str(n) for n in [1,2,3,4]]
    require(all(str(uuid.UUID(v))==v and uuid.UUID(v).version==4 and v in text for v in ids),'independent fixed public UUID literals not generated identity')
    required=['contextSuppliesMissingInternalIdWithoutGeneratingAnother','transportContextSaveFailureStopsBeforeDownstreamWithoutCauseOrFallback','existingVerifiedContextCannotBeReboundToAnotherServerIdentity','verified context is the only identity','untrusted context must not dispatch','must not mint replacement','must not remint','assertSame(context, WebRequestContext.require(request))','assertNull(failure.getCause())','assertEquals(0, failure.getSuppressed().length)','assertNull(underlying.getAttribute(WebRequestContext.class.getName()))','for (boolean stateFailure : new boolean[] {false, true})','"X-Forwarded-For", "203.0.113.1"','"X-Forwarded-Proto", "https"','"127.0.0.1"']
    require(all(v in text for v in required) and 'UUID.randomUUID' not in text and text.count('@Test')==3,'original independent fixed IDs/no generator/failure order/retained context assertions')
    spec_path=data.ROOT/'evidence/01_PT/018_NK-OPS-001/354_NK-OPS-001_Web部分所有・request整合単体テスト仕様書.md';spec_pin='d5c3e3c9a350e57f42b01227fa99101e066de78561d63c1ff412b58eb2e655c0'
    require(data.sha(spec_path.read_bytes())==spec_pin and all(v in spec_path.read_text() for v in ['generator0','chain0','context0','一request一identity']),'prior independent SSC172 identity-only oracle, no mixed runtime execution')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('tests','tests',4),('bool-tests','tests',True),('closure','completeSourceUnitClosure',{}),('physical','physicalClasses',{}),('units','fullSourceUnits',{}),('inventory','sourcePhysicalInventory',{}),('executable','executable',{}),('metadata','metadataClasses',['X']),('excluded','manualCounterExclusions',['X']),('unexecuted','unexecutedCodeClasses',[]),('totals','totals',{}),('strict','strictFour100GateExit',0),('crc','crcMismatch',1),('previous','helperPreviousSourceProofs',{}),('owners','owners',{}),('effort','effortPercent',100)]
    vectors.extend((k,k,False) for k in TRUE_FIELDS)
    vectors.extend((k,k,True) for k in FALSE_FIELDS if k!='metadataOnly')
    vectors.extend((k,k,1) for k in ['newAccepted','actualAuditRecordsWritten','actualHttpSessionsIssued','actualApiAuthenticationGrantsIssued'])
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false original request identity '+label)
    for value in [raw['begin'],p,old]:verify(value['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=3,suites=1,sourcePrograms=4,newSourcePrograms=4,physicalClasses=6,executablePhysicalClasses=6,metadataPhysicalClasses=0,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=4,baselineMainOwnerRows=5,unknownTestOwnerRows=1,semanticNegativeVectors=len(labels),negativeLabels=labels,previousHelpersNotReaccepted=True,previousHelperProofs=p['helperPreviousSourceProofs'],onlySyntheticWebRequestIdentityContracts=True,syntheticMockServletAttributesOnly=True,literalRequestUuidFixtures=True,uuidSupplierGeneratedValues=False,systemLoggerFactoryUsed=True,auditRecordInvoked=False,actualAuditRecordsWritten=0,publicSyntheticFixtureCredentialsUsed=False,actualHttpSessionsIssued=0,actualApiAuthenticationGrantsIssued=0,cryptoOrKeyOperationsInvoked=False,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,priorIndependentSpecPath=str(spec_path.relative_to(data.ROOT)),priorIndependentSpecSha256=spec_pin,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=3,semanticNegativeVectors=len(labels),newSourcePrograms=4,incomplete=4)))
if __name__=='__main__':main()
