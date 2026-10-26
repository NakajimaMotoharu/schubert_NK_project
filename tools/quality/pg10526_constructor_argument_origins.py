"""Bounded manual-review context binding, not execution of the consumer tests."""
from collections import Counter
from pathlib import Path
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10526-constructor-argument-origins-v1'
SOURCE = '6612747b7a5492e5c49647d85cfc2dcbe6d75c9f'
# The source/hash contract is mandatory: these observations are not a generic
# taint analyzer, and may not be reused after any of the bound sources changes.
RULES = {
 ('LogSqlContractTest','*'): ({'PAGE_SIZE'},5,'TEST_LOCAL_PAGE_SIZE_100'),
 ('LogQueryRepositoryTest','adm055PagesAndEveryFilterMatchIndependentRows'): ({'page','pages','total'},1,'LITERAL_TOTAL_REQUESTED_VECTORS_JDK_PAGING_ARITHMETIC'),
 ('UserQueryRepositoryTest','assertPage'): ({'first','last','page','pages','total'},1,'THREE_CALLS_LITERAL_OR_FIXTURE_COUNT_REQUESTED_ARITHMETIC'),
 ('InspectionAttemptTest','matchingSuccessAndWarning'): ({'code'},1,'CODE_FROM_FIXED_INPUT_CARRIER_NOT_RECONCILE_OUTPUT'),
 ('InspectionAttemptTest','countRegressionAndOverflow'): ({'Long','MAX_VALUE'},3,'JDK_LONG_MAX_VALUE_LITERAL_BOUNDARY'),
 ('LogCleanupValueContractTest','summaryUsesFixedDeltasAndCumulativeWarning'): ({'Long','MAX_VALUE'},1,'JDK_LONG_MAX_VALUE_LITERAL_BOUNDARY'),
 ('StepCleanupServiceTest','counterContinuityAndOverflow'): ({'Long','MAX_VALUE'},1,'JDK_LONG_MAX_VALUE_LITERAL_BOUNDARY'),
 ('InspectionAttemptTest','independentConcurrentObservations'): ({'i'},2,'INPUT_INDEX_0_TO_63_FIXED_DIFFERENCES'),
 ('StepCleanupServiceTest','allKindsCompleteAndPersistedCounts'): ({'delta','total','i'},2,'TEST_LOCAL_LITERAL_DELTA_TOTAL_ARRAYS'),
 ('CleanupStepRepositoryTest','actualSevenKindsAndStepTotals'): ({'deltas','totals','i'},3,'TEST_LOCAL_LITERAL_DELTA_TOTAL_ARRAYS'),
 ('CleanupStepValuesTest','concurrentValues'): ({'i'},2,'INPUT_INDEX_0_TO_63_FIXED_DIFFERENCES'),
 ('InspectionSummaryRepositoryTest','realBoundedRead'): ({'InspectionSummary','RUN'},3,'FIXED_INPUT_RUN_COUNTS_AND_COMPLETE_FLAG'),
 ('InspectionSummaryRepositoryTest','historicalUtcIdentity'): ({'InspectionSummary','expected'},1,'INPUT_LITERAL_INSTANTS_NOT_REPOSITORY_OUTPUT'),
 ('InspectionSummaryRepositoryTest','freshVisibilityAndBorrowing'): ({'InspectionSummary','RUN'},1,'FIXED_INPUT_RUN_COUNTS_AND_COMPLETE_FLAG'),
 ('MorningExpirySessionTest','actualFreshThenNormalSkipKeepOriginalAuditAndEachHandoffIsOneShot'): ({'current'},1,'FINAL_CURRENT_FROM_LITERAL_ATTEMPT_LOOP_1_TO_2')}
CONTEXTS = {
 'LogSqlContractTest':['private static final int PAGE_SIZE = 100;'],
 'LogQueryRepositoryTest':['new int[] {0, 1, 100, 101, 201}','new int[] {1, 2, 3, 999999}',
     'int pages = Math.max(1, (total + 99) / 100);','int page = Math.min(requested, pages);'],
 'UserQueryRepositoryTest':['new int[] {0, 1, 50, 51, 101}','int pages = Math.max(1, (count + 49) / 50);',
     'assertPage(actual, page, count, pages, first, last);','assertPage(value, 1, 49_999_950, 999999, 1, 50);',
     'assertPage(result, 2, 51, 2, 51, 51);'],
 'InspectionAttemptTest':['List.of(value(7, 7, 0, true), value(7, 3, 4, true))',
     'int code = after.counts().skipped() == 0 ? 0 : 10;','int index = i;',
     'new CleanupCounts(index + 9, index + 5, 4)','new CleanupCounts(i + 4, i + 3, 1)',
     'new CleanupCounts(i + 9, i + 5, 4)','Long.MAX_VALUE'],
 'LogCleanupValueContractTest':['new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0)'],
 'StepCleanupServiceTest':['long[] delta = {1, 1, 3, 2, 1, 1, 1};','long[] total = {1, 1, 3, 2, 1, 2, 3};',
     'new CleanupCounts(Long.MAX_VALUE, Long.MAX_VALUE, 0)'],
 'CleanupStepRepositoryTest':['long[] deltas = {1, 1, 3, 2, 1, 1, 1};','long[] totals = {1, 1, 3, 2, 1, 2, 3};'],
 'CleanupStepValuesTest':['for (int i = 0; i < 64; i++)','int n = i;',
     'new CleanupCounts(n, n, 0)','Optional.of(new CleanupCounts(100 - i, 100 - i, 0))'],
 'InspectionSummaryRepositoryTest':['new InspectionSummary(RUN, new CleanupCounts(0, 0, 0), false)',
     'new InspectionSummary(RUN, new CleanupCounts(5, 2, 3), false)',
     'new InspectionSummary(RUN, new CleanupCounts(5, 2, 3), true)',
     'var expected = new BatchRun(RUN.id(), Instant.parse(literal));'],
 'MorningExpirySessionTest':['for (int attempt = 1; attempt <= 2; attempt++)','final int current = attempt;']}


def classify(row):
    name = Path(row['path']).stem
    key = (name,'*' if name == 'LogSqlContractTest' else row['method'])
    if key not in RULES:
        raise ValueError('explicit reviewed source/method required')
    names,_,reason = RULES[key]
    if not set(row['unresolvedArgumentNames']) <= names:
        raise ValueError('unknown argument provenance remains pending')
    if not set(row['additionalConstructorTypesNotReviewed']) <= {'InspectionSummary'}:
        raise ValueError('unreviewed nested constructor')
    return key,reason


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original = data.read_checked(data.BASE/'PG10520-constructor-carrier-review-v3/manifest.json',
        'de115abc7337ea95939b3fc80360882f250b5d3b977596b179c815a6590afa23')
    data.read_checked(data.BASE/'PG10522-constructor-carrier-post-v1/manifest.json',
        '7f8c51ea963470e54006b0531d6d2363639876c574ea562748f7ba9422a83565')
    normal = data.read_checked(data.BASE/'PG10508-anm-type-name-compile-v1/manifest.json',
        'bc2c2ee9ff267ab6ea56f33df42b0272636cd928c23cdb3cc9b33bf1db3773c5')
    assert original['source'] == normal['source'] == SOURCE
    assert subprocess.check_output(['git','diff','--name-only',SOURCE,'--','src'],cwd=data.ROOT) == b''
    rows = data.read_checked(data.BASE/'PG10520-constructor-carrier-review-v3/sites.json',original['sitesSha256'])
    selected = [r for r in rows if r['unresolvedArgumentNames']]
    counts = Counter()
    contexts = {}
    output = []
    for row in selected:
        key,reason = classify(row)
        counts[key] += 1
        text = (data.ROOT/row['path']).read_text()
        assert data.sha(text.encode()) == row['sourceSha256'] == normal['begin']['inputHashes'][row['path']]
        assert all(fragment in text for fragment in CONTEXTS[Path(row['path']).stem])
        contexts[row['path']] = dict(sha256=row['sourceSha256'],reviewedFragments=CONTEXTS[Path(row['path']).stem])
        derived = dict(row,inputOriginReview=reason,
            argumentOriginQualification='STATIC_ARGUMENT_ORIGIN_REVIEW_ONLY_NOT_DYNAMIC_OR_WHOLE_CASE_ORACLE_PASS')
        assert all(derived[k] == value for k,value in row.items())
        output.append(derived)
    assert counts == Counter({key:value[1] for key,value in RULES.items()})
    assert len(output) == 28
    assert {Path(p).stem for p in contexts} == set(CONTEXTS) and len(CONTEXTS) == 10
    nested = {}
    for name in ('InspectionSummary','BatchRun'):
        path = f'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/{name}.java'
        text = (data.ROOT/path).read_text()
        assert data.sha(text.encode()) == normal['begin']['inputHashes'][path]
        # Complete constructors manually read: only null/range/precision checks.
        nested[name] = dict(path=path,sha256=data.sha(text.encode()),
            review='VALIDATION_ONLY_NO_COMPONENT_REASSIGNMENT_OR_SUT_OUTPUT_CONVERSION')
    rejected = 0
    for field,value in (('method','__unknown__'),('unresolvedArgumentNames',['unreviewedSutResult']),
                       ('additionalConstructorTypesNotReviewed',['UnreviewedEncoder'])):
        try:
            classify(dict(selected[-1],**{field:value}))
        except ValueError:
            rejected += 1
    assert rejected == 3
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'argument-origins.json',output)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        rowsSha256=data.sha((OUT/'argument-origins.json').read_bytes()),contexts=contexts,nestedInputCarriers=nested,
        variableSyntaxSitesReviewed=28,consumerSources=len(contexts),metadataNegativeVectors=3,
        expectedArgumentsUseSutOutput=False,provenanceScope='EXACT_UNCHANGED_SOURCE_SELECTED_EXPRESSIONS_ONLY',
        fullCaseRequirementsAndFixtureCorrectnessAccepted=False,wholeG03Accepted=False,
        original128ManifestRewritten=False,productTestsExecuted=0,targetCompilation=0,targetClassLoading=0,
        externalActions=0,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
