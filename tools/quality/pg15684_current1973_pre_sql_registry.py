"""Add original boundary cases only; keep every existing Source counter/proof and append separate scope evidence."""
import copy
from collections import Counter
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
from trace_owner_join import canonical
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG15668-current1960-request-bindings-registry-v1','90e8c1a53aba7c30f4ff0fded8bbfb2b8f2ba45056cedc42380b8903eea9aeb7')
PREV_POST=('PG15670-current1960-request-bindings-registry-post-v1','37719bce8dfa26be7d1a66a3f84882143964c5a265a6da1bc1ce3302748f2b90')
POST=('PG15680-pre-sql-thirteen-post-v1','cc5c271d935d29da7f4bf59fc2d9d65e68cb4321b962ca9fe3a2889781655b1b')
INDEPENDENT=('PG15682-pre-sql-thirteen-independent-v1','56cb8b1e4cec877c3343f5b25089fff3a95b4aa1db241371a9c0638d0ed8c7a3')
OUT=data.BASE/'PG15684-current1973-pre-sql-registry-v1'
def require(ok,label):
    if not ok:raise ValueError(label)
def read(pair):return data.read_checked(data.BASE/pair[0]/'manifest.json',pair[1])
def wire(v):return json.dumps(v,sort_keys=True)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new only')
    old,previous,p,q=[read(pair) for pair in [PREV,PREV_POST,POST,INDEPENDENT]]
    require(all(v['actualExit']==0 and v['source']==SOURCE for v in [old,previous,p,q]) and previous['registryManifestSha256']==PREV[1] and previous['metadataNegativeVectors']==34,'qualified predecessor and current witnesses')
    require(q['postSha256']==POST[1] and (p['tests'],p['suites'],q['tests'],q['semanticNegativeVectors'],q['newSourcePrograms'])==(13,3,13,32,0),'exact independent13')
    require(q['independentNpeAssertionCounts']==dict(LogQueryPreSqlBoundaryTest=3,QuestionQueryPreSqlBoundaryTest=12,UserQueryPreSqlBoundaryTest=8) and sum(q['zeroJdbcAssertionCounts'].values())==13,'literal null and zero JDBC')
    require(p['sameExecMeasurementSupplementalOnly'] is q['sameExecMeasurementSupplementalOnly'] is q['previousProofsNotReplaced'] is True and p['currentSourceQualificationProofsReplaced'] is q['currentSourceQualificationProofsReplaced'] is p['actualJdbcBackendConnected'] is q['actualJdbcBackendConnected'] is p['cryptoOrKeyOperationsInvoked'] is q['cryptoOrKeyOperationsInvoked'] is False,'supplemental only/no backend/crypto')
    require(all(p[k]==q[k]==0 for k in ['actualJdbcMethodsInvoked','actualSqlStatementsPreparedOrExecuted','newAccepted']) and p['singleSession'] is True and p['crcMismatch']==0 and p['strictFour100GateExit']==1,'true runtime/no all-source pass')
    require(set(q['previousSourceProofs'])==set(p['fullSourceUnits']) and all(old['fullSourceUnits'][name]==u for name,u in q['previousSourceProofs'].items()),'existing three source proofs preserved exactly')
    require(set(p['metadataClasses'])=={'dev/codex/schubert/nk/api/persistence/QuestionQueryRepository$RowMapper'} and all(name in old['metadataClasses'] and old['metadataClasses'][name]['sha256']==p['sourcePhysicalInventory'][name]['sha256'] for name in p['metadataClasses']),'existing trueNoCode metadata not recreated/recounted')
    result=copy.deepcopy(old);cases={(c['classname'],c['name']) for c in old['cases']};new={(c['classname'],c['name']) for c in p['cases']}
    require(len(new)==13 and not new&cases and all(c['result']=='PASS' for c in p['cases']),'new exact whole originals, no confirmation replay');cases|=new
    normal=read(('PG14216-typed-marker-guard-six-compile-v1',old['normalManifestSha256']));hashes=normal['begin']['inputHashes']
    require(all(data.sha((data.ROOT/path).read_bytes())==h for path,h in hashes.items()),'all current frozen inputs')
    logical={v['path']:v for v in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for path,row in p['owners'].items():
        require(hashes[path]==row['sha256'] and all(row[k]==v for k,v in canonical(path,logical).items()),'actual canonical owners')
        require(path not in result['owners'] or result['owners'][path]==row,'old owner roles kept');result['owners'][path]=copy.deepcopy(row)
    result['originalPostReferences'].append(dict(name=POST[0],sha256=POST[1],tests=13,suites=3,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='ORIGINAL_PRE_SQL13_SUPPLEMENTAL_MEASUREMENT_NO_SOURCE_REPLACEMENT'))
    result['additionalScopeReferences'].append(dict(name=POST[0],sha256=POST[1],independentPost=list(INDEPENDENT),newTests=13,newExecs=1,execSha256=p['execSha256'],sessionIdentity=p['sessionIdentity'],scope='SUPPLEMENTAL_WHOLE_BOUNDARY_MEASUREMENT_NOT_SOURCE_QUALIFICATION_REPLACEMENT',existingSourceNames=sorted(p['fullSourceUnits']),existingSourceQualificationPreserved=True,coverageExecUnion=False))
    result.update(invocation=invocation,previousUniqueRegistryReference=list(PREV),previousRegistryPostReference=list(PREV_POST),cases=[dict(classname=c,name=n) for c,n in sorted(cases)],suiteNames=sorted({c for c,n in cases}),tests=len(cases),suites=len({c for c,n in cases}),originalExecs=old['originalExecs']+1,totalProductExecs=old['totalProductExecs']+1,totalMethodExecutions=old['totalMethodExecutions']+13,uniqueProductMethodDelta=13,newTestIds=13,sourceProgramDelta=0,ownerStatusCounts=dict(Counter(v['ownershipStatus'] for v in result['owners'].values())),unknownOwnerPaths=sum(v['canonicalOwner'] is None for v in result['owners'].values()),lastUpdateKind='CURRENT_SOURCE_ORIGINAL_TEST_ADDITION_WITH_DISCLOSURE_HISTORY_RETAINED')
    require((result['tests'],result['suites'],result['originalExecs'],result['totalProductExecs'],result['totalMethodExecutions'],result['measuredSourcePrograms'],result['measuredPhysical'],result['four100SourcePrograms'],result['incompleteSourcePrograms'])==(1973,256,108,109,2081,438,575,243,17),'actual supplemental counts, no source inflation')
    require(result['ownerStatusCounts']==dict(BASELINE_LOGICAL_REFERENCE=353,NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED=227,UNKNOWN=140),'three new UNKNOWN test rows only')
    changed={'invocation','previousUniqueRegistryReference','previousRegistryPostReference','cases','suiteNames','tests','suites','originalExecs','totalProductExecs','totalMethodExecutions','uniqueProductMethodDelta','newTestIds','sourceProgramDelta','owners','ownerStatusCounts','unknownOwnerPaths','originalPostReferences','additionalScopeReferences','lastUpdateKind'}
    require(all(wire(result[k])==wire(v) for k,v in old.items() if k not in changed) and result['fullSourceUnits']==old['fullSourceUnits'] and result['metadataClasses']==old['metadataClasses'] and result['postDisclosureCorrections']==old['postDisclosureCorrections'],'all old counters/proofs/cost/domain/corrections unchanged')
    for v in [old,previous,p,q]:verify(v['invocation'])
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',result);print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
