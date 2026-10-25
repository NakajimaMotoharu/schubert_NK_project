"""Independent literal protocol primary/related oracle; never erase reflection/multiple scopes."""
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
from host_tool_invocation import capture,verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9400-protocol-composite-post-v1'
SUBJECT=BASE/'PG9398-protocol-composite-metadata-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
ORACLE={'AuthenticationErrorProfileTest':'WBS-P002-02','MessageCodecTest':'WBS-P002-03','PayloadGoldenVectorTest':'WBS-P002-02',
 'ScenarioRecordEncodingTest':'WBS-P002-02','HeaderModelTest':'WBS-P001-01','IndependentNamedFieldOracle':'WBS-P001-03',
 'LayoutMetadataTest':'WBS-P001-02','SemanticFieldValueTest':'WBS-P001-03','EnumWireCompatibilityTest':'WBS-P002-01','ProtocolSemanticTypeTest':'WBS-P002-01'}

def sha(raw):return hashlib.sha256(raw).hexdigest()
def validate(rows,expected):
    if rows!=expected:raise ValueError('exact literal primary and full related responsibility required')

def main():
    invocation=capture(Path(__file__));assert not OUT.exists()
    raw=(SUBJECT/'manifest.json').read_bytes();assert sha(raw)=='1f0068d0aaadee207c706383f05daf975c969386598a2a5940d30965545994d0'
    result=json.loads(raw);assert result['actualExit']==0 and result['source']==SOURCE
    catalog=(SUBJECT/'candidates.json').read_bytes();assert sha(catalog)==result['candidatesSha256']=='616faaac9af59f9e9e8556898b752050dc4ae6fba70d0b10a94c43eb5b8e49a1'
    rows=json.loads(catalog);assert len(rows)==10 and {Path(row['path']).stem for row in rows}==set(ORACLE)
    graph_dir=BASE/'PG9386-composite-reference-graph-v3'
    graph_raw=(graph_dir/'manifest.json').read_bytes();assert sha(graph_raw)==result['graphManifestSha256']=='3b092052e7724400870c72d7d92a163e5fdbe9c536eebe2bfe38403d3c187b15'
    graph=json.loads(graph_raw);reference_raw=(graph_dir/'unresolved.json').read_bytes();assert sha(reference_raw)==graph['unresolvedSha256']
    references={row['path']:row for row in json.loads(reference_raw)}
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes());logical={row['path']:row for row in inventory['artifacts']}
    normal_raw=(BASE/'PG9246-web-life-lock-six-compile-v1/manifest.json').read_bytes();assert sha(normal_raw)==result['normalManifestSha256']=='989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46'
    hashes=json.loads(normal_raw)['begin']['inputHashes'];expected=[]
    for row in rows:
        path=row['path'];main=row['subjectMainPath'];primary=ORACLE[Path(path).stem];original=references[path]
        assert hashes[path]==sha((ROOT/path).read_bytes()) and hashes[main]==sha((ROOT/main).read_bytes())
        assert logical[main]['owner']==logical[main]['costOwner']==primary and primary in original['mainOwners']
        expected.append(dict(path=path,sha256=hashes[path],owner=primary,costOwner=primary,subjectMainPath=main,subjectMainSha256=hashes[main],
          relatedOwners=sorted(set(original['mainOwners'])-{primary}),originalReferenceOwners=original['mainOwners'],
          unresolvedRuntimeReasons=original['unresolvedReasons'],targetRuntimeAccepted=False,
          basis='LITERAL_PRIMARY_AND_RELATED_RESPONSIBILITY_1910_ORIGINAL_PT_SPEC_CURRENT_SOURCE_STATIC_ONLY'))
    validate(rows,expected)
    assert all(len(row['relatedOwners'])>=1 for row in rows)
    named=next(row for row in rows if Path(row['path']).stem=='IndependentNamedFieldOracle')
    assert named['unresolvedRuntimeReasons']==['REFLECTION_OR_DYNAMIC_CLASS_RESOLUTION'] and named['targetRuntimeAccepted'] is False
    targets_raw=(SUBJECT/'named-dto-fixture-targets.json').read_bytes();assert sha(targets_raw)==result['namedTargetsSha256']
    targets=json.loads(targets_raw);assert len(targets)==69
    for item in targets.values():
        assert item['owner']==logical[item['path']]['owner']=='WBS-P001-03'
        assert item['sha256']==hashes[item['path']]==sha((ROOT/item['path']).read_bytes())
    for path,digest in (('class-proofs.json',result['classProofsSha256']),):assert sha((SUBJECT/path).read_bytes())==digest
    rejected=[]
    for label,change in (('cost-only',lambda v:v[0].update(costOwner='WBS-G13.07')),('primary-only',lambda v:v[0].update(owner='WBS-G13.07')),
      ('related-erased',lambda v:v[0].update(relatedOwners=[])),('runtime-invented',lambda v:v[0].update(targetRuntimeAccepted=True)),
      ('wrong-hash',lambda v:v[0].update(sha256='0'*64)),('duplicate',lambda v:v.append(copy.deepcopy(v[0]))),('missing',lambda v:v.pop())):
        changed=copy.deepcopy(rows);change(changed)
        if label=='cost-only':assert {k for k in rows[0] if rows[0][k]!=changed[0][k]}=={'costOwner'}
        try:validate(changed,expected)
        except ValueError:rejected.append(label)
        else:raise AssertionError('forged protocol ownership accepted')
    verify(invocation);OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          subjectManifestSha256=sha(raw),catalogSha256=sha(catalog),literalPrimaryOwners=ORACLE,relatedOwnersFullyPreserved=True,
          reflectionReasonRetained=True,namedDtoFixtureTypes=69,positiveBeforeNegatives=True,metadataCounterexamples=rejected,
          productTestsExecuted=0,newAccepted=0,targetRuntimeClassLoading=0,coverage=None,formalUpdated=False),stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps(dict(actualExit=0,primaryOwners=10,relatedSetsPreserved=10,metadataNegatives=len(rejected),manifestSha256=sha((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
