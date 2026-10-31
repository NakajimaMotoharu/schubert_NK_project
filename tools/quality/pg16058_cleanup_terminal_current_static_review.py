"""Current eight explicit JDBC ownership blocks: manual static purposes, never dynamic PASS."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT = data.BASE / 'PG16058-cleanup-terminal-current-static-review-v1'
PRIOR = data.BASE / 'PG16004-batch-run-current-static-review-v1'
PRIOR_PIN = '2e6c4240a6749477bf58ade99bb44701c382f0d4adb3c8cb0a5b0ad66348976d'
PATH = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/CleanupTerminalRepository.java'
HELPER = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/JdbcResourceFailures.java'
EXTRA_DESIGN = 'documents/300_SS/330_データ・ファイル/331_DB物理・DDL・index・権限設計.md'
DESIGN = 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md'
PINS = {EXTRA_DESIGN: '7f6e0430a38769dad5d94ed8d95faaab124f4bb86246c478feee5b50ffca26d5', PATH: '2baed428e77bb6fee2114ecac7d66d1ee5917d45e1bc9f25beb1ac5ba7eba90d',
        HELPER: 'f4cff9bb43cacfde5be699fd61d4e25526523d5ef5e478aa88dcbb8bdde6928a',
        DESIGN: 'bf35de0b4d24a253eb75808f0280fa92eb3f02f8ba3a988a227f96c7213781a5'}
# alias, primary catch, finally, close catch, closing brace. All eight blocks reviewed individually.
SITES = [
    ('read', 'rows', 190, 206, 209, 213, 217),
    ('read', 'statement', 183, 218, 221, 225, 229),
    ('references', 'rows', 289, 311, 314, 318, 322),
    ('references', 'statement', 281, 323, 326, 330, 334),
    ('progressSeal', 'rows', 376, 381, 384, 388, 391),
    ('progressSeal', 'statement', 367, 392, 395, 399, 402),
    ('readRejected', 'rows', 511, 518, 521, 525, 529),
    ('readRejected', 'statement', 504, 530, 533, 537, 541),
]
REASONS = {
    'CloseResource': 'present is an identity alias or fixed SQLDataException on null, not a new owner. The separately acquired nonnull resource is directly closed once in this exact protected scope; borrowed Connection is not closed.',
    'AvoidCatchingGenericException': 'Closed The explicit SQL[/IOException]/RuntimeException/Error catch records and rethrows the identical primary, or lets direct-close failure replace it only under the existing SS332 SQL/unknown priority. No unknown failure becomes success or fixed normal data.',
    'DoNotThrowExceptionInFinally': 'Conditional throw is required by SS332: cleanup after a successful body or unknown cleanup after SQL primary supersedes the result/SQL. Unknown primary keeps identity with fixed redacted secondary. Plain TWR would not implement this priority.',
}
STATUS = 'MANUAL_PURPOSE_REVIEW_COMPLETE_DYNAMIC_UNQUALIFIED'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def checked_sources():
    result = {}
    for path, digest in PINS.items():
        file = data.ROOT / path
        require(not file.is_symlink() and data.sha(file.read_bytes()) == digest, 'fixed explicitly reviewed public source/design')
        result[path] = file.read_text()
    for path in (DESIGN, EXTRA_DESIGN):
        require(subprocess.check_output(['git', 'show', 'origin/main:' + path], cwd=data.ROOT) == result[path].encode(), 'approved designs main unchanged')
    return result


def review_rows(queue, texts):
    text = texts[PATH]
    lines = text.splitlines()
    require(len(lines) == 626 and 'if (value == null) throw new SQLDataException("Cleanup terminal projection missing");\n    return value;' in text, 'full current source and exact identity alias')
    require(all(token not in text for token in ('connection.close(', 'connection.commit(', 'connection.rollback(', 'connection.setAutoCommit(', 'connection.setReadOnly(')), 'borrowed connection not owned')
    helper = texts[HELPER]
    require('primary == null\n        || (primary instanceof SQLException && !(secondary instanceof SQLException))) return true;' in helper, 'null/SQL cleanup priority')
    require('if (!(primary instanceof SQLException)) primary.addSuppressed(new BatchRepositoryException());\n    return false;' in helper, 'unknown primary fixed nonself secondary')
    require('CleanupTerminalRepository.read/readRejected/references各二owned scope' in texts[DESIGN] and 'SSC200' in texts[EXTRA_DESIGN] and 'SSC201' in texts[EXTRA_DESIGN] and 'maintenance_read_success_progress' in texts[EXTRA_DESIGN], 'six base scopes and explicit original-lookup/progress-seal additions')
    selected = [r for r in queue if r['path'] == PATH]
    require(len(selected) == 48 and Counter(r['rule'] for r in selected) == Counter(CloseResource=8, AvoidCatchingGenericException=32, DoNotThrowExceptionInFinally=8), 'all48 current retained warnings')
    result = []
    seen = set()
    for method, resource, alias, body, final, close, end in SITES:
        primary = 'rowsFailure' if resource == 'rows' else 'statementFailure'
        require(f'present({resource});' in lines[alias - 1], 'exact alias resource')
        require(lines[alias - 2].strip() == 'try {', 'alias protected immediately')
        if method == 'references' and resource == 'statement':
            require(lines[alias - 3].strip() == 'Entry prior;' and lines[alias - 4].strip() == f'@Nullable Throwable {primary} = null;', 'only nonexecuting uninitialized local between primary and try')
        else:
            require(lines[alias - 3].strip() == f'@Nullable Throwable {primary} = null;', 'direct primary declaration')
        body_types = 'SQLException | IOException | RuntimeException | Error' if method == 'references' else 'SQLException | RuntimeException | Error'
        require(lines[body - 1].strip() == '} catch (' + body_types + ' failure) {', 'explicit source-specific body catch set')
        require(lines[close - 1].strip() == '} catch (SQLException | RuntimeException | Error secondary) {', 'explicit cleanup parameter/set')
        require(lines[body].strip() == primary + ' = failure;' and lines[body + 1].strip() == 'throw failure;', 'same primary rethrow')
        fragment = '\n'.join(lines[final - 1:end])
        require(lines[final - 1].strip() == '} finally {' and f'if ({resource} != null)' in fragment and fragment.count(resource + '.close();') == 1, 'exact nullguard and direct close')
        require(f'if (JdbcResourceFailures.replace({primary}, secondary)) throw secondary;' in fragment, 'same primary and cleanup conditional throw')
        rows = [r for r in selected if int(r['attributes']['beginline']) in (alias, body, final, close)]
        require(len(rows) == 6, 'each reviewed scope six diagnostics')
        for row in rows:
            require(row['sourceSha256'] == PINS[PATH] and row['id'] not in seen, 'exact source and unique diagnostic')
            start, stop, value = span(text, row['attributes'])
            if row['rule'] == 'CloseResource':
                require(value in ('query', 'row', 'checked') and int(row['attributes']['beginline']) == alias, 'alias token diagnostic')
            elif row['rule'] == 'AvoidCatchingGenericException':
                require(value in ('RuntimeException', 'Error') and int(row['attributes']['beginline']) in (body, close), 'two exact generic type spans per catch')
            else:
                require(int(row['attributes']['beginline']) == final and int(row['attributes']['endline']) == end and value.startswith('finally {'), 'exact finally extent')
            seen.add(row['id'])
            result.append(dict(**row, method=method, resource=resource, primaryVariable=primary,
                bodyCatchTypes=body_types, cleanupExceptionParameter='secondary', declarationPreludeKind='UNINITIALIZED_LOCAL_ONLY' if method == 'references' and resource == 'statement' else 'DIRECT_PRIMARY', aliasLine=alias, bodyCatchLine=body, finallyLine=final, closeCatchLine=close, endLine=end,
                spanStart=start, spanEndExclusive=stop, spanSha256=data.sha(value.encode()),
                reason=REASONS[row['rule']], status=STATUS, rawRetained=True,
                actualViolation=None, productTestsExecuted=0, currentDynamicQualification=False,
                typeResolutionProven=False, actualCloseCountProven=False, actualSqlPostconditionsProven=False))
    require(seen == {r['id'] for r in selected}, 'no unreviewed or duplicated target diagnostics')
    return sorted(result, key=lambda r: r['id'])


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    previous = data.read_checked(PRIOR / 'manifest.json', PRIOR_PIN)
    queue = data.read_checked(PRIOR / 'remaining-selected-review-queue.json', previous['queueSha256'])
    require(previous['actualExit'] == 0 and len(queue) == 881 and previous['remainingSelectedUnreferenced'] == 881, 'frozen selected queue, not whole unreviewed universe')
    rows = review_rows(queue, checked_sources())
    ids = {r['id'] for r in rows}
    remaining = [r for r in queue if r['id'] not in ids]
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'review.json', dict(source=SOURCE, inputHashes=PINS, rows=rows))
    data.write(OUT / 'remaining-selected-review-queue.json', remaining)
    data.write(OUT / 'manifest.json', dict(actualExit=0, source=SOURCE, invocation=invocation,
        priorManifestSha256=PRIOR_PIN, priorQueueSha256=previous['queueSha256'], inputHashes=PINS,
        reviewSha256=data.sha((OUT / 'review.json').read_bytes()), queueSha256=data.sha((OUT / 'remaining-selected-review-queue.json').read_bytes()),
        priorUnreferenced=881, newlyPurposeReviewed=48, remainingSelectedUnreferenced=len(remaining),
        originalReferenced=562, previousPurposeReviewed=48, combinedPurposeReviewed=48 + len(rows), priorPurposeOrReferenceRows=610, combinedPurposeOrReferenceRows=610 + len(rows), ownershipScopes=8,
        status=STATUS, actualViolationCount=None, rawSuppressed=0, ruleChanged=False,
        productTestsExecuted=0, analyzerReexecuted=False, compilerExecuted=False,
        oldRuntimeTransferred=False, currentEightScopeDynamicQualification=False,
        sourceChanged=False, externalActions=0, actualDatabaseActions=0, actualVmActions=0,
        wholeF03Accepted=False, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, purposeReviewed=len(rows), remaining=len(remaining))))


if __name__ == '__main__':
    main()
