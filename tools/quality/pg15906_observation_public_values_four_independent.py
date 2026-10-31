"""Independent original public values4 oracle; no complete-Root qualification from nested data probes."""
import copy
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg15902_observation_public_values_four_pt as original
import pg15904_observation_public_values_four_post as post

PIN='19a2db0b39020483931422acc6c5dfd39da5f6ccdf447eb9dcdc5d7cd5b2d064'
OUT=data.BASE/'PG15906-observation-public-values-four-independent-v1'
TOTALS={k:dict(covered=c,missed=m) for k,c,m in [('LINE',24,682),('METHOD',9,112),('CLASS',5,12),('BRANCH',0,284)]}
TRUE=['singleSession','officialGeneratedFiltersUnchanged','onlyReviewedPureValueSuites','onlyPublicObservationValueContracts','lexicalPublicPathsOnly','outerBusinessCodeProbeAbsence','unexecutedCodeIncludedInAllDenominators','previousHelpersNotReaccepted']
FALSE=['targetUnitFour100','allMeasuredApplicableCountersCovered','realRootObjectsOrFactoryCreated','cryptoOrKeyOperationsInvoked','testOwnNewSlotPublicEvidenceWrites','testOwnedTemporaryFileIo','testOwnedTemporaryFixtureWrites','actualJdkFileForceOnOwnTemporaryFiles','actualFilesOpenedByProduct','actualPrivateFilesOpened','actualSecretKeysLoaded','actualCredentialValuesUsed','actualAuthenticationOrSessionIssued','formalUpdated','whole451Accepted','wholeF03Accepted','oldCoverageTransferred','priorProductResultsReused','rootMainInvoked']
def require(ok,message):
    if not ok:raise ValueError(message)
def wire(v):return json.dumps(v,sort_keys=True)
def assess(p):
    require(p['actualExit']==0 and p['source']==original.SOURCE and p['originalManifestSha256']==post.RAW and type(p['tests']) is int and p['tests']==4 and p['suites']==1,'genuine current original four')
    require(all(p[k] is True for k in TRUE) and all(p[k] is False for k in FALSE) and all(type(p[k]) is int and p[k]==0 for k in ['failures','errors','skipped','reruns','newAccepted','actualVmActions','actualDatabaseActions','actualServiceActions','actualNetworkActions','actualJmsConnectionsCreated','actualJmsContextsCreated','actualBoundSockets']) and p['effortPercent'] is None,'memory-only original value effects, no authority or complete quality')
    require(p['strictFour100GateExit']==1 and p['crcMismatch']==0 and p['sessionIdentity']==original.SESSION and p['totals']==TOTALS,'actual partial whole denominator retained')
    expected={n:sorted(group) for n,group in original.CLOSURES.items()};physical={n for group in expected.values() for n in group}
    require(p['completeSourceUnitClosure']==expected and set(p['fullSourceUnits'])==set(expected) and set(p['physicalClasses'])==set(p['sourcePhysicalInventory'])==physical and len(physical)==22,'five complete source families/twenty-two physical')
    require(set(p['metadataClasses'])==original.METADATA and len(p['metadataClasses'])==5 and set(p['executable'])==physical-original.METADATA and len(p['executable'])==17 and p['manualCounterExclusions']==[],'five actual abstract interfaces only, no Code excluded')
    for name,row in p['sourcePhysicalInventory'].items():
        if name in original.METADATA:require(row['flags']==1536 and row['methods'] and not any(m['hasCode'] for m in row['methods']),'real abstract NoCode')
        else:require(any(m['hasCode'] for m in row['methods']),'Code not metadata')
    require(set(p['unexecutedCodeClasses'])==original.UNEXECUTED and len(p['unexecutedCodeClasses'])==12 and set(original.MAIN_UNITS)<=original.UNEXECUTED,'all outer business paths explicitly unexecuted')
    for name in original.UNEXECUTED:
        require(all(c['covered']==0 for c in p['executable'][name]['counters'].values()),'no Root/FFM/database/journal/config outer execution')
    require({n for n,row in p['executable'].items() if row['counters']['CLASS']['covered']==1}==original.EXECUTED,'only five declared nested value classes invoked')
    require(all(type(v) is int for row in p['executable'].values() for c in row['counters'].values() for v in c.values()),'typed real counters')
    require({k:{role:sum(r['counters'][k][role] for r in p['executable'].values()) for role in ['covered','missed']} for k in TOTALS}==TOTALS,'independent whole physical sums')
    for name,u in p['fullSourceUnits'].items():
        require(u['physical']==expected[name] and all(u[k] is False for k in ['four100','metadataOnly','branchNaturallyZero','threeCounter100']),'five incomplete enclosing sources, not five pure value-only source exclusions')
        require(u['totals']=={k:{role:sum(p['executable'][n]['counters'][k][role] for n in u['physical'] if n in p['executable']) for role in ['covered','missed']} for k in TOTALS},'independent per-family sums')
    require(len(p['owners'])==6 and sum(v['ownershipStatus']=='BASELINE_LOGICAL_REFERENCE' for v in p['owners'].values())==5 and sum(v['ownershipStatus']=='UNKNOWN' for v in p['owners'].values())==1,'five original Main owner pairs and unknown original Test')
    require(len(p['helperPreviousSourceProofs'])==2 and p['helperPreviousSourceProofs']['dev/codex/schubert/nk/storage/StorageRootLayout']['four100'] is True,'old helper proofs retained separately')
    require(p['forbiddenProductProbeHits']==0 and len(p['passiveNativeBoundaryAbsence']['rows'])==6 and all(r[3]=='0' for r in p['passiveNativeBoundaryAbsence']['rows']) and all(s['actualExit']==0 and not s['timedOut'] for s in p['stages']),'actual held/native/outer guard terminals, no implied blanket permission')
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    p=data.read_checked(post.OUT/'manifest.json',PIN);raw=data.read_checked(data.BASE/'PG15902-observation-public-values-four-pt-v1/manifest.json',post.RAW);post.assess(raw);assess(p)
    require(p['cases']==raw['cases'] and len({(r['classname'],r['name']) for r in p['cases']})==4,'original four once only')
    previous=data.read_checked(data.BASE/'PG15892-current2060-scenario-stream-registry-v1/manifest.json','c9edd9a200ac7e24583872ed715368439346d9cb5c0243722f164eba6bf60f49')
    require(all(previous['fullSourceUnits'][n]==u for n,u in p['helperPreviousSourceProofs'].items()) and not set(p['fullSourceUnits'])&previous['fullSourceUnits'].keys(),'new source families disjoint and old helper units exactly preserved')
    text=original.TEST.read_text()
    require(text.count('@Test')==4 and all(v in text for v in ['RootServiceFacts[public=<redacted>]','BrokerObservations[actual=<redacted>]','EffectiveConfigurations[non-secret=<redacted>]','BrokerJournalSummary[redacted]','PUBLIC-RECORD-CANARY-ALPHA','PUBLIC-RECORD-CANARY-BETA','missing < 5','new ServiceConfigFiles.Contents(null, serviceYaml)','new ServiceConfigFiles.Contents(commonYaml, null)','List.of(marker, apiDigest, webDigest, journalDigest, commonYaml, serviceYaml)']),'independent fixed diagnostics/seven-null/canary input oracles')
    spec=data.ROOT/'evidence/01_PT/018_NK-OPS-001/2346_公開値診断・null契約二追加_単体テスト仕様書.md';require(data.sha(spec.read_bytes())=='ef2c4434f7345432d54aa8f87d05adc033e5235903177b8ef6e54c8d5ea7aa86','prior independent oracle frozen, not actual old source PT transfer')
    vectors=[('source','source','OLD'),('tests','tests',True),('totals','totals',{}),('closure','completeSourceUnitClosure',{}),('physical','physicalClasses',{}),('units','fullSourceUnits',{}),('inventory','sourcePhysicalInventory',{}),('executable','executable',{}),('metadata','metadataClasses',[]),('exclusions','manualCounterExclusions',['X']),('unexecuted','unexecutedCodeClasses',[]),('strict','strictFour100GateExit',0),('crc','crcMismatch',1),('helpers','helperPreviousSourceProofs',{}),('owners','owners',{}),('effort','effortPercent',100)]
    vectors.extend((k,k,False) for k in TRUE);vectors.extend((k,k,True) for k in FALSE)
    labels=[]
    for label,key,value in vectors:
        require(wire(p[key])!=wire(value),'nondegenerate negative')
        bad=copy.deepcopy(p);bad[key]=value
        try:assess(bad)
        except ValueError:labels.append(label)
        else:raise ValueError('false public-value quality '+label)
    for v in [raw['begin'],p,previous]:verify(v['invocation'])
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,postSha256=PIN,originalManifestSha256=post.RAW,tests=4,suites=1,sourcePrograms=5,newSourcePrograms=5,physicalClasses=22,executablePhysicalClasses=17,metadataPhysicalClasses=5,four100SourcePrograms=0,naturallyBranchZeroSourcePrograms=0,incompleteSourcePrograms=5,semanticNegativeVectors=len(labels),negativeLabels=labels,onlyPublicObservationValueContracts=True,outerBusinessCodeProbeAbsence=True,onlyDeclaredFiveNestedValueClassesInvoked=True,oldHelperProofsPreserved=True,previousHelperProofs=p['helperPreviousSourceProofs'],cryptoOrKeyOperationsInvoked=False,actualFilesOpenedByProduct=False,actualSecretKeysLoaded=False,actualPrivateFilesOpened=False,priorIndependentSpecSha256=data.sha(spec.read_bytes()),productTestsReexecuted=0,newAccepted=0,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()));print(json.dumps(dict(actualExit=0,tests=4,semanticNegativeVectors=len(labels),newSourcePrograms=5,incompleteSourcePrograms=5)))
if __name__=='__main__':main()
