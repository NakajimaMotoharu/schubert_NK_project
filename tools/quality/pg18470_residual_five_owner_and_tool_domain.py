"""Five explicit resource responsibilities and one retained noncanonical quality-source trace."""
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
PREV=('PG18454-current3008-latest270-owner-correction-v1','0662e8e2912f48ef1d5619199a22edd1bbef34dcb45c7ef69b278936b7a40d51')
OUT=data.BASE/'PG18470-residual-five-owner-and-tool-domain-v1'
QUALITY='tools/quality/architecture/ProtocolCarrierBoundaryTest.java'
def require(ok,message):
    if not ok:raise ValueError(message)
def main():
    invocation=capture(__file__);require(not OUT.exists(),'new-only')
    current=data.read_checked(data.BASE/PREV[0]/'manifest.json',PREV[1])
    normal=data.read_checked(data.ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
    primary=data.read_checked(data.BASE/'PG13846-snapshot-program-trace-v1/manifest.json','f075dc40f990fb89f449d6da6a58d50dd4a129cb2bc2b619f30d7d3b51d8c107')
    require(current['actualExit']==normal['actualExit']==primary['actualExit']==0 and current['source']==normal['source']==SOURCE,'fixed same current technical source')
    logical={r['path']:r for r in json.loads((data.ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())['artifacts']}
    rows=[]
    for stem in ['log-search-validation','operation-post-submit','question-input-validation','search-speaker-submit']:
        test='src/schubert-nk-web/src/test/javascript/'+stem+'.test.cjs';main='src/schubert-nk-web/src/main/resources/static/js/'+stem+'.js'
        require(logical[main]['owner']==logical[main]['costOwner']=='WBS-P016-25','original shared client asset owner, not guessed screen owner')
        text=(data.ROOT/test).read_text();literal='const script = path.resolve(__dirname, "../../main/resources/static/js/'+stem+'.js");'
        require(literal in text and 'const source = fs.readFileSync(script, "utf8");' in text,'explicit fixed main asset input')
        require(data.sha((data.ROOT/test).read_bytes())==normal['begin']['inputHashes'][test]==current['owners'][test]['sha256'],'current full Test resource bytes')
        require(data.sha((data.ROOT/main).read_bytes())==normal['begin']['inputHashes'][main],'current main asset bytes')
        rows.append(dict(path=test,sha256=current['owners'][test]['sha256'],previousOwner=current['owners'][test],resolvedCandidate=dict(canonicalOwner='WBS-P016-25',canonicalCostOwner='WBS-P016-25',ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='EXACT_FIXED_JS_ASSET_REFERENCE_ORIGINAL_941_P01625'),subject=main,currentSubjectSha256=normal['begin']['inputHashes'][main],originalLogicalSubject=logical[main],scope='PRIMARY_ASSET_REFERENCE_NOT_EXHAUSTIVE_DEPENDENCIES',oldRuntimeTransferred=False))
    fixture='src/schubert-nk-batch/src/test/resources/inspector/unit-golden.txt';consumer='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshotTest.java';main='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot.java'
    original_consumer=next(r for r in primary['sourceRows'] if r['path']==consumer)
    require(original_consumer['canonicalOwner']==original_consumer['canonicalCostOwner']==logical[main]['owner']==logical[main]['costOwner']=='WBS-P004-04','explicit actual consumer/Main responsibility, not UnitStateParser')
    text=(data.ROOT/consumer).read_text();pin='2170fc2e71a4ba50519bc2f123d0bf75fcc46adab033645b7b68b5c513c345f6'
    require('getResourceAsStream("/inspector/unit-golden.txt")' in text and pin in text and 'assertEquals(373, bytes.length)' in text,'independent fixture oracle and fixed resource lookup')
    require(data.sha((data.ROOT/consumer).read_bytes())==normal['begin']['inputHashes'][consumer]==original_consumer['sha256'],'same current consumer bytes')
    blob=(data.ROOT/fixture).read_bytes();require(len(blob)==373 and data.sha(blob)==normal['begin']['inputHashes'][fixture]==current['owners'][fixture]['sha256']==pin,'fixture full byte and independent golden hash')
    rows.append(dict(path=fixture,sha256=pin,previousOwner=current['owners'][fixture],resolvedCandidate=dict(canonicalOwner='WBS-P004-04',canonicalCostOwner='WBS-P004-04',ownershipStatus='NEW_LOGICAL_CANDIDATE_REVIEWED_NOT_ACCEPTED',basis='EXACT_373_BYTE_INSPECTOR_GOLDEN_CONSUMER_AND_ORIGINAL_MAIN_P00404'),subject=main,consumer=consumer,currentConsumerSha256=normal['begin']['inputHashes'][consumer],originalConsumerRecord=original_consumer,originalLogicalSubject=logical[main],scope='FIXED_TEST_GOLDEN_NOT_ACTUAL_UNIT_OBSERVATION',oldRuntimeTransferred=False))
    tool=(data.ROOT/QUALITY).read_bytes();previous=current['owners'][QUALITY]
    require(data.sha(tool)==previous['sha256'] and previous['basis']=='EXACT_NEW_TOOL_PT_NOT_LOGICAL_ARTIFACT_NO_OWNER_INFERENCE' and QUALITY not in normal['begin']['inputHashes'] and QUALITY not in logical,'already explicit noncanonical tool, not a Production scope exclusion')
    text=tool.decode();require('PT-OPS-2789' in text and 'public final class ProtocolCarrierBoundaryTest' in text,'public quality source identity')
    names=re.findall(r'@Test\s+void\s+(\w+)\(',text);binary='dev.codex.schubert.nk.protocol.layout.ProtocolCarrierBoundaryTest';cases=[r for r in current['cases'] if r['classname']==binary]
    require(names and {r['name'] for r in cases}==set(names),'all original quality cases retained')
    quality=dict(path=QUALITY,sha256=previous['sha256'],previousCanonicalTableRow=previous,role='QUALITY_TEST_SOURCE_NOT_LOGICAL_ARTIFACT',canonicalOwner=None,canonicalCostOwner=None,engineeringChangeOwnerForThisCorrection='WBS-G13.07',testId='PT-OPS-2789',existingCases=cases,casesRemoved=0,physicalClassesRemoved=0,coverageExclusionsAdded=0,oldRuntimeTransferred=False)
    require(len(rows)==5 and {r['path'] for r in rows}|{QUALITY}=={p for p,r in current['owners'].items() if r['ownershipStatus']=='UNKNOWN'},'all six accounted')
    verify(current['invocation']);verify(primary['invocation']);verify(invocation);OUT.mkdir()
    data.write(OUT/'resource-owner-candidates.json',rows);data.write(OUT/'noncanonical-quality-source.json',quality)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,previousRegistrySha256=PREV[1],normalManifestSha256='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3',resourceCandidatesSha256=data.sha((OUT/'resource-owner-candidates.json').read_bytes()),qualityTraceSha256=data.sha((OUT/'noncanonical-quality-source.json').read_bytes()),newResourceOwnerCandidates=5,qualityTraceSeparated=1,canonicalOwnerRowsBefore=len(current['owners']),canonicalOwnerRowsAfter=len(current['owners'])-1,allSixTraceRowsRetainedAcrossDomains=True,coverageExclusionsAdded=0,productTestsExecuted=0,nodeTestsExecuted=0,oldRuntimeTransferred=False,actualVmActions=0,actualDatabaseActions=0,actualNetworkActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))
if __name__=='__main__':main()
