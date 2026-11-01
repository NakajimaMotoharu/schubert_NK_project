"""Fixed remaining-UNKNOWN reconciliation; current public content only for selected same-byte candidates."""
import collections
import json
import subprocess
import g07_host_class_provenance_inputs as data
import trace_owner_latest_primary_v4 as resolver
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT=data.BASE/'PG18450-latest-explicit270-owner-preflight-v1'
OLD=data.BASE/'PG13846-snapshot-program-trace-v1/manifest.json'
PREV=('PG18434-current3008-owner24-correction-v1','598adca1e798cc76c586096744efd66337cd9c5c5b6e03382ec78503f3bfa1d3')
def require(ok,message):
    if not ok:raise ValueError(message)
def excluded(path):return any(v in path for v in ['RootFailed','/private/','.private.','SnapshotKeyCloseWitness','pg9892_'])
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    original_blob=OLD.read_bytes();require(data.sha(original_blob)==resolver.REGISTRY_SHA,'exact original registry')
    old=json.loads(original_blob);old_rows={r['path']:r for r in old['sourceRows']}
    wbs=json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    for key in ['currentJavaPathExplicitRegistryMeasurement','currentIncrementalHostOwnership']:
        section=wbs[key];require(section['manifest']==str(OLD.relative_to(data.ROOT)) and section['sha256']==resolver.REGISTRY_SHA and section['source']==old['source'],'exact current WBS primary, not arbitrary ancestor')
    current=data.read_checked(data.BASE/PREV[0]/'manifest.json',PREV[1])
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    require(current['source']==normal['source']==SOURCE and current['actualExit']==normal['actualExit']==0,'same current source')
    selections=[];deferred=[]
    for path,row in sorted(current['owners'].items()):
        if row['ownershipStatus']!='UNKNOWN':continue
        if excluded(path):deferred.append(dict(path=path,reason='HELD_NAME_ONLY_NO_SOURCE_OR_ROW_LOOKUP'));continue
        previous=old_rows.get(path)
        if previous is None:deferred.append(dict(path=path,reason='NOT_IN_FIXED_ORIGINAL_REGISTRY'));continue
        if previous.get('canonicalOwner') is None:deferred.append(dict(path=path,reason='ORIGINAL_OWNER_UNKNOWN'));continue
        if previous['sha256']!=normal['begin']['inputHashes'][path]:
            deferred.append(dict(path=path,reason='ORIGINAL_BYTES_DIFFER_CURRENT_UNKNOWN_RETAINED'));continue
        require(row['sha256']==previous['sha256'],'current owner entry same normal hash')
        tracked=subprocess.check_output(['git','ls-files','--error-unmatch','--',path],cwd=data.ROOT,text=True).strip()
        file=data.ROOT/path;require(tracked==path and not file.is_symlink() and file.is_file(),'exact public tracked regular source')
        require(data.sha(file.read_bytes())==previous['sha256'],'exact selected current public bytes')
        selections.append(dict(path=path,sha256=previous['sha256'],previousUnknownOwner=row,originalExplicitRecord=previous))
    require(len(selections)==270 and len(deferred)==6,'fixed selected24/deferred276 only')
    paths=tuple(r['path'] for r in selections);rules=resolver.from_original_bytes(original_blob,paths)
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    for r in selections:
        resolved=resolver.canonical(r['path'],logical,r['sha256'],rules)
        require(resolved['ownershipStatus']=='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED' and resolved['canonicalOwner']==resolved['canonicalCostOwner']==r['originalExplicitRecord']['canonicalOwner'],'explicit candidate only')
        r['resolvedCandidate']=resolved
    require(sum('/src/main/' in r['path'] for r in selections)==0 and sum('/src/test/java/' in r['path'] for r in selections)==270,'three existing Main, twenty-one Test/fixture paths')
    verify(current['invocation']);verify(old['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'selected-owner-bridges.json',selections);data.write(OUT/'deferred-owner-reasons.json',deferred)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,originalExplicitRegistrySha256=resolver.REGISTRY_SHA,previousTechnicalRegistrySha256=PREV[1],normalManifestSha256='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3',resolverSourceSha256=data.sha((data.ROOT/'tools/quality/trace_owner_latest_primary_v4.py').read_bytes()),selectedBridgesSha256=data.sha((OUT/'selected-owner-bridges.json').read_bytes()),deferredReasonsSha256=data.sha((OUT/'deferred-owner-reasons.json').read_bytes()),selectedCandidates=270,selectedExistingMain=0,selectedTestAndFixture=270,deferredUnknown=6,deferredReasonCounts=dict(collections.Counter(r['reason'] for r in deferred)),selectionHeldNameGuardBeforeIndividualRowLookup=True,wholeParsedOriginalMetadataOtherRowsPresent=True,globalOtherRowUnreadAssurance=False,selectedRootFailedPaths=0,selectedHeldToolPaths=0,originalQualificationFlagUnknownCount=sum(r['originalExplicitRecord'].get('currentSourcePtQualificationInferred') is None for r in selections),qualificationOfThoseRecordsInferred=False,operatorOrProductSourceExecuted=False,productTestsExecuted=0,coverageExecuted=False,oldRuntimeTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
