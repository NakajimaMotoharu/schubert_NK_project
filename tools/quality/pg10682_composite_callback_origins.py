"""Two existing source expectations: fixture origin and ordinal property, no target execution."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg10519_constructor_carrier_review_v2 import first_argument
from pg10588_record_constructor_review import record_review

OUT = data.BASE/'PG10682-composite-callback-origins-v1'
TARGETS = {('MorningDatabaseSessionTest','mdb590Scenarios'):'FINITE_COMPOSITE_TEST_INPUT_ORIGIN_STATIC_REVIEWED',
    ('WebNativeRuntimeOwnedComponentTest','verifyOwn'):'CALLBACK_ORDINAL_SUPPLEMENTAL_PROPERTY_NOT_PATH_OWNER_ORACLE'}


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original_path = data.BASE/'PG10646-constructor-literal-inputs-v1/manifest.json'
    original = data.read_checked(original_path,'a2f3823325d625a7d64ac2aad13cfe027a0497a7552ec9d23c61f32060710b55')
    entries = data.read_checked(original_path.parent/'input-reviews.json',original['inputReviewsSha256'])
    normal = data.read_checked(data.BASE/'PG10632-query-semantic-constant-compile-v1/manifest.json',
        '8f29215a400d24a55ecabee90c74fb72a43525b740f129a12ae6053559701f87')
    rows,evidence = [],{}
    for index,entry in enumerate(entries):
        row = entry['original']
        key = (Path(row['path']).stem,row['method'])
        if key not in TARGETS:
            continue
        path = row['path']
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == normal['begin']['inputHashes'][path]
        tokens = first_argument(text,row)
        expression = text[tokens[0][1]:tokens[-1][2]]
        assert data.sha(expression.encode()) == row['expectedExpressionSha256']
        ranges = [(3515,3550),(3681,3748)] if key[0] == 'MorningDatabaseSessionTest' else [(535,546),(380,391),(485,509)]
        lines = text.splitlines(keepends=True)
        evidence[path] = dict(sha256=data.sha(text.encode()),ranges=[dict(first=a,last=b,text=''.join(lines[a-1:b])) for a,b in ranges])
        rows.append(dict(priorEntryIndex=index,priorEntrySha256=data.sha(json.dumps(entry,sort_keys=True,ensure_ascii=False).encode()),
            key={k:row[k] for k in ('path','method','line','expectedExpressionSha256')},sourceSha256=row['sourceSha256'],
            status=TARGETS[key],expression=expression,wholeCaseFixtureQualified=False,productTestsExecuted=0))
    assert len(rows) == 2 and {r['status'] for r in rows} == set(TARGETS.values())
    supplemental = []
    for filename,name,kind in [('BatchStepAttempt.java','BatchStepAttempt','RECORD'),
        ('OwnedTransferDirectory.java','OwnedTransferDirectory','HELD_DESCRIPTOR_PATH_NOT_CONFIGURED_PATH')]:
        path, = [p for p in normal['begin']['inputHashes'] if '/src/main/java/' in p and p.endswith('/'+filename)]
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        review = record_review(text,name) if kind == 'RECORD' else dict(kind=kind)
        if kind == 'RECORD':
            assert review['kind'] == 'VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT'
        supplemental.append(dict(path=path,sha256=data.sha(text.encode()),review=review))
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'origin-reviews.json',rows)
    data.write(OUT/'source-evidence.json',evidence)
    data.write(OUT/'supplemental-contracts.json',supplemental)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=normal['source'],invocation=invocation,
        rowsSha256=data.sha((OUT/'origin-reviews.json').read_bytes()),evidenceSha256=data.sha((OUT/'source-evidence.json').read_bytes()),
        supplementalSha256=data.sha((OUT/'supplemental-contracts.json').read_bytes()),newIndependentInputOriginReviewed=1,
        callbackOrdinalPropertyClassified=1,totalInputProvenanceReviewed=160,previousCorrections=2,newCorrections=0,
        supplementalProperties=6,unclassifiedInputOriginSites=0,wholePathOwnerOracleStillUnproven=True,
        wholeOracleQualified=False,productTestsExecuted=0,targetClassLoaded=False,targetCompilation=False,
        coverage=None,externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
