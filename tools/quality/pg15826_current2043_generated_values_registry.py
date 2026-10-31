"""Add original boundary cases only; keep every existing Source counter/proof and append separate scope evidence."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15810-current2031-web-identity-registry-v1','49c59a5f449b1da48a00abd6461db5deda2ee9e64b98029c03201fd199d9416b')
PREV_POST=('PG15812-current2031-web-identity-registry-post-v1','7a7f06aa34ab97be56ce1572558ef6120abd46ad049c46f5486640ceaf9b3977')
POST=('PG15823-generated-metric-value-twelve-post-v2','d6443771465d6c1e12c31e52fac3eb45987ffe8ae1d25186b4f62d792013f6c9')
INDEPENDENT=('PG15824-generated-metric-value-twelve-independent-v1','3a004391503a0da1b41e8fce95ebc366cd039b8fcedf44a675e9950c96079e81')
OUT=data.BASE/'PG15826-current2043-generated-values-registry-v1'
def require(ok,label):
    if not ok:raise ValueError(label)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old,previous,p,q=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,previous,p,q]) and previous['registryManifestSha256']==PREV[1] and previous['metadataNegativeVectors']==34,'qualified predecessor and current witnesses')
    require(q['postSha256']==POST[1] and (p['tests'],p['suites'],q['tests'],q['semanticNegativeVectors'],q['newSourcePrograms'])==(12,2,12,47,0),'exact independent13')
    require(p['onlyGeneratedMetricValueContracts'] is q['onlyGeneratedMetricValueContracts'] is p['jdkNonCryptographicHashVectorsOnly'] is q['jdkNonCryptographicHashVectorsOnly'] is p['sameExecMeasurementSupplementalOnly'] is q['sameExecMeasurementSupplementalOnly'] is p['previousSourceProofsNotReplaced'] is q['previousSourceProofsNotReplaced'] is True,'same-exec generated semantics only/no Source proof replacement')
    require(p['currentSourceQualificationProofsReplaced'] is p['meterRegistryOrRecorderConstructed'] is q['meterRegistryOrRecorderConstructed'] is p['actualCollectorOrExporterStarted'] is q['actualCollectorOrExporterStarted'] is p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is False and p['noOuterRecorderMethodInvocations'] is q['noOuterRecorderMethodInvocations'] is True,'no recorder/exporter/crypto invocation')
    require(p['singleSession'] is True and p['crcMismatch']==0 and p['strictFour100GateExit']==1 and p['newAccepted']==q['newAccepted']==0,'true runtime, partial supplemental scope not whole-source pass')
    require(set(q['previousSourceProofs'])==set(p['fullSourceUnits'])==set(p['currentTargetPriorSourceProofs']) and wire(q['previousSourceProofs'])==wire(p['currentTargetPriorSourceProofs']) and all(old['fullSourceUnits'][name]==u and u['four100'] is True for name,u in q['previousSourceProofs'].items()),'all five existing four100 Source proofs preserved exactly')
    require(p['metadataClasses']==[] and q['metadataPhysicalClasses']==0 and q['independentHashVectors']==dict(pool=94248,outbox=3040,max4=0,max3=-2147483648,zero=0),'no NoCode reclassification/independent signed hash values')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};new={(c['classname'],c['name']) for c in p['cases']}
    require(len(new)==12 and not new&cases and all(c['result']=='PASS' for c in p['cases']),'new exact whole originals, no confirmation replay');cases|=new
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all current frozen inputs')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(hashes[path]==row['sha256'] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical owners')
        require(path not in result['owners'] or result['owners'][path]==row,'old owner roles kept');result['owners'][path]=copy.deepcopy(row)
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=12,suites=2,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_GENERATED_VALUE12_SUPPLEMENTAL_MEASUREMENT_NO_SOURCE_REPLACEMENT'))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=12,newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='SUPPLEMENTAL_GENERATED_VALUE_CONTRACTS_NOT_SOURCE_QUALIFICATION_REPLACEMENT',existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False))
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+12,uniqueProductMethodDelta=12,newTestIds=12,sourceProgramDelta=0,ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    require((result['tests'],result['suites'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['measuredSourcePrograms'],result['measuredPhysical'],result['four100SourcePrograms'],result['incompleteSourcePrograms'])==(2043,271,116,117,2151,458,615,247,31),'actual supplemental counts, no source inflation')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=373,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=229,UNKNOWN=154),'two new candidate Test rows only, no baseline promotion')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','owners','ownerStatusCounts','unknownOwnerPaths','originalPostReferences','additionalScopeReferences','lastUpdateKind'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and result['fullSourceUnits']==old['fullSourceUnits'] and result['metadataClasses']==old['metadataClasses'] and result['postDisclosureCorrections']==old['postDisclosureCorrections'],'all old counters/proofs/cost/domain/corrections unchanged')
    for v in [old,previous,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
