"""Independent counts/IDs/type/source/design and unchanged failed-entry metadata; Product execution0."""
import json
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG13048-reference-identity-post-v2'

def immutable_observation(row,original):
    assert original['manualPurposeReviewComplete'] is False and row['manualPurposeReviewComplete'] is True
    assert all(row[key] == original[key] for key in original if key != 'manualPurposeReviewComplete')

def main():
    invocation = capture(__file__); assert not OUT.exists()
    p = data.BASE/'PG13044-reference-identity-context-v2'
    m = data.read_checked(p/'manifest.json','f7345a09e4b83152111b83b56a48534a9223f66f6704df8a6d870adefe5e8d06')
    r = data.read_checked(p/'review.json',m['reviewSha256'])
    prior = data.read_checked(data.BASE/'PG13038-throwable-identity-post-v1/review.json','bad4c30a7d5caa009bffbedd9dbf8c94576409920d29673476caf517c1a91f03')
    originals = {row['id']:row for row in prior['typedNonThrowableUnclassified']}
    groups = {
        'REQUEST_SCOPE_BINDING':set('PMD-00007 PMD-00014 PMD-00021 PMD-00036 PMD-00043'.split()),
        'THREAD_OWNER_OR_SELF_JOIN':set('PMD-00093 PMD-00325 PMD-00382 PMD-06167 PMD-06169 PMD-07267 PMD-07307 PMD-07320 PMD-07427'.split()),
        'OPAQUE_ISSUER_AND_BASELINE':set('PMD-02800 PMD-02802 PMD-03021 PMD-03022 PMD-03023 PMD-03024 PMD-03025'.split()),
        'EXACT_TERMINAL_RECEIPT_CONTINUITY':set('PMD-02868 PMD-03114 PMD-03117 PMD-03120'.split()),
        'LEXICAL_SCOPE_STACK':{'PMD-07322'},'CURRENT_SESSION_REPOSITORY_INSTANCE':{'PMD-07429','PMD-07435'}}
    assert m['actualExit'] == 0 and m['source'] == r['source'] == prior['source'] == '2f4290e7e511ea30224d087f78d44964d3488919'
    assert len(r['reviewedRows']) == len(originals) == 28 and set(r['newlyReviewedContextIds']) == set(originals)
    assert len({row['id'] for row in r['reviewedRows']}) == 28
    for category,ids in groups.items(): assert {row['id'] for row in r['reviewedRows'] if row['purposeCategory'] == category} == ids
    for row in r['reviewedRows']:
        original = originals[row['id']]
        immutable_observation(row,original)
        raw = (data.ROOT/row['path']).read_bytes(); assert data.sha(raw) == row['sourceSha256']
        lines = raw.decode().splitlines(); line = row['originalLine']
        assert row['sourceContext'] == [s.strip() for s in lines[max(0,line-3):line+4]]
        assert row['actualViolation'] is None and not row['dynamicExecutionQualificationInferred'] and row['manualPurposeReviewComplete']
        assert row['status'] == 'STATIC_DIAGNOSTIC_CONTEXT_REVIEWED_DYNAMIC_HOLD'
    for path,support in r['sourceSupports'].items():
        raw=(data.ROOT/path).read_bytes();assert data.sha(raw)==support['sourceSha256']
        lines=raw.decode().splitlines()
        assert all(lines[number-1].strip()==text for number,text in support['supportingSourceLines'])
    assert [r[key] for key in ['sourceDerivedRaw','totalPriorCorrections','joinedContextWarnings','sourceReboundCurrentWholePending','noCurrentReferenceInThisJoin']] == [8472,953,3259,941,5213]
    assert all(r[key] == 0 for key in ['productTestsExecuted','productClassesLoaded','newProductClassFiles','newAccepted','globalRawCorrectionsAdded'])
    assert not r['sourceCodeChanged'] and not r['wholeF03Accepted'] and not r['whole451Accepted'] and r['actualViolationCount'] is None
    failed = json.loads((data.BASE/'PG13042-reference-identity-context-v1/failure.safe.json').read_bytes())
    assert failed['actualExit'] == failed['lintExit'] == 1 and not failed['bodyStarted']
    original_entry = (data.ROOT/failed['entry']).read_text()
    assert data.sha(original_entry.encode()) == failed['entrySha256'] == 'fea88a79af50ea4170433ad895dab288e20cd1a7c8bff053f926040ea7b086d6'
    fixed = original_entry.replace('from pathlib import Path\n','').replace('PG13042-reference-identity-context-v1','PG13044-reference-identity-context-v2')
    assert (data.ROOT/'tools/quality/pg13044_reference_identity_context.py').read_text() == fixed
    refs = [('documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md',92),('documents/300_SS/310_アプリケーション/313_画面template・controller・form設計.md',137),('documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md',48),('documents/300_SS/340_batch・基盤/343_設定file・directory・初期data・migration・切戻し設計.md',448),('documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md',93)]
    design = [dict(path=path,sha256=data.sha((data.ROOT/path).read_bytes()),line=line,text=(data.ROOT/path).read_text().splitlines()[line-1]) for path,line in refs]
    negative = []
    original = originals[r['reviewedRows'][0]['id']]; row = r['reviewedRows'][0]
    for key,value in [('sourceSha256','0'*64),('originalLine',0),('leftType','java.lang.Object'),('manualPurposeReviewComplete',False)]:
        bad = dict(row); assert bad[key] != value; bad[key] = value
        try: immutable_observation(bad,original)
        except AssertionError: negative.append(key)
        else: raise AssertionError('changed observation or incomplete review accepted')
    old = data.ROOT/'tools/quality/pg13046_reference_identity_post.py'
    assert data.sha(old.read_bytes()) == '4a640cf9e09a3f9a15a76de04ed05f016090748eef451b2b5b8b0a113f4c0ef0'
    verify(invocation); OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=r['source'],invocation=invocation,reviewManifestSha256=data.sha((p/'manifest.json').read_bytes()),
        reviewSha256=m['reviewSha256'],reviewedRows=28,sourceFiles=r['sourceFiles'],categoryCounts={key:len(ids) for key,ids in groups.items()},
        sourceDerivedRaw=8472,totalPriorCorrections=953,joinedContextWarnings=3259,sourceReboundCurrentWholePending=941,
        designReferences=design,failedEntryUnchanged=True,fixedEntryOnlyImportAndOutputChanged=True,
        metadataNegativeVectors=m['metadataNegativeVectors'],independentImmutableNegativeVectors=negative,oldPostEntryUnchanged=True,productTestsExecuted=0,newAccepted=0,actualViolationCount=None,
        wholeF03Accepted=False,whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__': main()
