"""Independently verify new full-source measurements from registered Mock12, without recounting PT."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15759_registered_mock_helper_measurement as post
import pg14540_mock_servlet_security_whole_twelve_pt as original
PIN='a11c2bc0601ce48308b82bd5573fa8c23183833923ec5308a7d551b4517f6d20'
OUT=data.BASE/'PG15760-registered-mock-helper-independent-v1'
P='dev/codex/schubert/nk/web/'
NAMES={P+'security/ClosedWebAuthentication',P+'session/SessionPrincipal'}
def require(ok,label):
    if not ok:raise ValueError(label)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW,'source/raw')
    require((p['tests'],p['suites'],len(p['cases']),len(p['xmlHashes']))==(12,3,12,3),'existing whole12/3 only')
    require(all(type(p[k]) is int and p[k]==0 for k in ['actualExit','failures','errors','skipped','reruns','newTestIds','newAccepted','crcMismatch','newProductExecutions','newUniqueProductMethods','productMethodsInvokedByCorrection','productTestsReexecutedByPost']),'typed zero new execution roles')
    require(p['singleSession'] is True and p['sessionIdentity']==original.SESSION and p['execSha256']==raw['execSha256'],'one original same-source exec')
    require({(c['classname'],c['name']) for c in p['cases']}=={(c['classname'],c['name']) for c in raw['cases']} and all(c['result']=='PASS' for c in p['cases']),'original cases unchanged')
    require(set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==set(p['executable'])==set(p['fullSourceUnits'])==NAMES and p['completeSourceUnitClosure']=={n:[n] for n in NAMES},'two whole Code sources')
    require(p['metadataClasses']==p['manualCounterExclusions']==[] and p['officialGeneratedFiltersUnchanged'] is True and all(any(v['hasCode'] for v in u['methods']) for u in p['sourcePhysicalInventory'].values()),'no manual/NoCode exclusion')
    require(all(type(v) is int for row in p['executable'].values() for counter in row['counters'].values() for v in counter.values()),'typed counters')
    totals={k:{r:sum(v['counters'][k][r] for v in p['executable'].values()) for r in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH']}
    require(totals==p['totals']=={k:dict(covered=c,missed=m) for k,c,m in [('LINE',27,2),('METHOD',4,1),('CLASS',2,0),('BRANCH',16,12)]},'independent whole missed counters retained')
    for name in NAMES:
        unit=p['fullSourceUnits'][name]
        require(unit['physical']==[name] and unit['totals']==p['executable'][name]['counters'] and unit['four100'] is unit['branchNaturallyZero'] is False,'both incomplete, no acceptance')
    require(p['strictFour100GateExit']==1 and p['targetUnitFour100'] is p['allMeasuredApplicableCountersCovered'] is False,'real gap not gate pass')
    require(p['sameSourcePriorExecAdditionalMeasurement'] is p['originalRegisteredCasesNotRecounted'] is p['registeredSameSourceOriginalRuntimeReferenced'] is p['onlyMockServletSourceMeasurement'] is True and p['priorDifferentSourceProductResultsReused'] is p['oldCoverageTransferred'] is False,'only same-source prior reference, no new Product run')
    require(p['cryptoOrKeyOperationsInvoked'] is p['publicSyntheticFixtureCredentialsUsed'] is True and p['cryptoOperationKind']=='UUID_V4_PUBLIC_REQUEST_EVENT_IDENTIFIERS_ONLY','truthful original UUID/public foreign-token fixtures')
    correction=p['effectDisclosureCorrection']
    require(correction['oldPostSha256']=='843d77fda87ded57728d392717a6e454ba09a8a2f4f904f9e2818a2dcd0c85a7' and correction['oldCryptoInvoked'] is False and correction['effectiveCryptoInvoked'] is True and correction['originalParentEffectFields']=='MISSING_NOT_FALSE' and all(data.sha((data.ROOT/path).read_bytes())==pin for path,pin in correction['sourceHashes'].items()),'old error preserved and effective disclosure source-bound')
    require(all(p[k] is False for k in ['actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','actualFilesOpenedByProduct','actualPrivateFilesOpened','actualBrokerOrListenerStarted','rootMainInvoked','formalUpdated','whole451Accepted','wholeF03Accepted','syntheticCredentialsRenderedOrPersisted','valueBearingWireSaved']),'no actual secrets/authority/IO/formal')
    require(all(p[k]==0 for k in ['actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualBrowserActions','actualBoundSockets','actualJmsConnectionsCreated','actualJmsContextsCreated']) and p['effortPercent'] is None,'no live target operation')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual passive results')
    require(len(p['owners'])==5 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==2 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==3,'two new Main and three already known UNKNOWN Tests')
def main():
    global raw
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    raw=data.read_checked(data.BASE/'PG14540-mock-servlet-security-whole-twelve-pt-v1/manifest.json',post.RAW)
    p=data.read_checked(post.OUT/'manifest.json',PIN);post.assess(raw);assess(p)
    old=data.read_checked(data.BASE/'PG15748-current2023-mq-login-registry-v1/manifest.json','446c25131764958017d939cf9fabb6373a8b144822badccb388d839857ffb932')
    methods={(c['classname'],c['name']) for c in p['cases']}
    require(methods<={(c['classname'],c['name']) for c in old['cases']} and not NAMES&set(old['fullSourceUnits']),'existing cases not recounted; sources first measured')
    previous=data.read_checked(data.BASE/'PG15758-registered-mock-helper-measurement-post-v1/manifest.json','843d77fda87ded57728d392717a6e454ba09a8a2f4f904f9e2818a2dcd0c85a7')
    changed={'invocation','cryptoOrKeyOperationsInvoked','cryptoOperationKind','publicSyntheticFixtureCredentialsUsed'}
    require(all(wire(p[k])==wire(value) for k,value in previous.items() if k not in changed),'correction does not change any original execution or measured counter')
    text=original.TESTS['ClosedServletSecurityFilterTest'].read_text()
    require(all(v in text for v in ['void web138ClosedPrincipalImplementsServletContract','void web139','void web140','void web141','ClosedWebAuthentication.principal(','assertSame(authenticated ? p : null','assertThrows(SessionStoreException.class','UUID::randomUUID']),'original independent Servlet/principal/foreign-denial assertions')
    vectors=[('source','source','OLD'),('raw','originalManifestSha256','0'*64),('tests','tests',13),('suites','suites',4),('cases','cases',[]),('physical','physicalClasses',{}),('units','fullSourceUnits',{}),('executable','executable',{}),('totals','totals',{}),('metadata','metadataClasses',['X']),('exclude','manualCounterExclusions',['X']),('filter','officialGeneratedFiltersUnchanged',False),('new-jvm','newProductExecutions',1),('new-test','newUniqueProductMethods',12),('recount','originalRegisteredCasesNotRecounted',False),('same-source','sameSourcePriorExecAdditionalMeasurement',False),('other-source','priorDifferentSourceProductResultsReused',True),('four','targetUnitFour100',True),('strict','strictFour100GateExit',0),('single','singleSession',False),('crc','crcMismatch',1),('crypto','cryptoOrKeyOperationsInvoked',False),('fixture','publicSyntheticFixtureCredentialsUsed',False),('kind','cryptoOperationKind','NONE_IN_REVIEWED_DOMAIN_BODY'),('keys','actualSecretKeysLoaded',True),('credentials','actualCredentialValuesUsed',True),('auth','actualAuthenticationOrSessionIssued',True),('root','rootMainInvoked',True),('formal','formalUpdated',True),('whole','whole451Accepted',True),('union','oldCoverageTransferred',True),('accepted','newAccepted',1),('bool-zero','newAccepted',False),('effort','effortPercent',100),('owners','owners',{})]
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate '+label);bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false new Source measurement '+label)
    verify(raw['begin']['invocation']);verify(previous['invocation']);verify(p['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,testsReferenced=12,suitesReferenced=3,tests=12,suites=3,newTests=0,newProductExecutions=0,newUniqueMethods=0,sourcePrograms=2,newSourcePrograms=2,physicalClasses=2,executablePhysicalClasses=2,metadataPhysicalClasses=0,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=2,baselineMainOwnerRows=2,unknownTestOwnerRows=3,semanticNegativeVectors=len(labels),negativeLabels=labels,registeredOriginalMethodsReferencedOnly=True,effectDisclosureCorrection=p['effectDisclosureCorrection'],cryptoOrKeyOperationsInvoked=True,cryptoOperationKind=p['cryptoOperationKind'],publicSyntheticFixtureCredentialsUsed=True,actualSecretKeysLoaded=False,actualCredentialValuesUsed=False,actualAuthenticationOrSessionIssued=False,actualFilesOpenedByProduct=False,originalSourceProofsNotReplaced=True,productTestsExecutedByIndependent=0,productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None));print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,semanticNegativeVectors=len(labels),newTests=0,newSourcesMeasured=2,incomplete=2)))
if __name__=='__main__':main()
