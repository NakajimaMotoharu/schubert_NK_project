"""Current eight explicit JDBC ownership blocks: manual static purposes, never dynamic PASS."""
from collections import Counter
import json
import subprocess
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pmd_source_span_ascii import span

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
OUT = data.BASE / 'PG16004-batch-run-current-static-review-v1'
PRIOR = data.BASE / 'PG15938-f03-saved-schema-supplement-v1'
PRIOR_PIN = 'a907cb510165be0cba32f9700d5efe23248bbe27ba03aa1f0766b75ec69b1218'
PATH = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/BatchRunRepository.java'
HELPER = 'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/repository/JdbcResourceFailures.java'
DESIGN = 'documents/300_SS/330_データ・ファイル/332_SQL・transaction・lock・削除設計.md'
PINS = {PATH: '47d12d03590932d7df11681d0c663cd1a75e59b4b32cff72ee5c7aea8318d876',
        HELPER: 'f4cff9bb43cacfde5be699fd61d4e25526523d5ef5e478aa88dcbb8bdde6928a',
        DESIGN: 'bf35de0b4d24a253eb75808f0280fa92eb3f02f8ba3a988a227f96c7213781a5'}
# alias, primary catch, finally, close catch, closing brace. All eight blocks reviewed individually.
SITES = [
    ('finish', 'statement', 142, 147, 150, 154, 158),
    ('history', 'rows', 245, 280, 283, 287, 291),
    ('history', 'statement', 238, 292, 295, 299, 303),
    ('abandon', 'statement', 314, 323, 326, 330, 334),
    ('insert', 'rows', 368, 377, 380, 384, 388),
    ('insert', 'statement', 354, 389, 392, 396, 400),
    ('replayed', 'rows', 424, 428, 431, 435, 439),
    ('replayed', 'statement', 417, 440, 443, 447, 451),
]
REASONS = {
    'CloseResource': 'present is an identity alias or fixed SQLDataException on null, not a new owner. The separately acquired nonnull resource is directly closed once in this exact protected scope; borrowed Connection is not closed.',
    'AvoidCatchingGenericException': 'Closed SQL/RuntimeException/Error catch records and rethrows the identical primary, or lets direct-close failure replace it only under the existing SS332 SQL/unknown priority. No unknown failure becomes success or fixed normal data.',
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
    require(subprocess.check_output(['git', 'show', 'origin/main:' + DESIGN], cwd=data.ROOT) == result[DESIGN].encode(), 'approved design main unchanged')
    return result


def review_rows(queue, texts):
    text = texts[PATH]
    lines = text.splitlines()
    require(len(lines) == 502 and 'if (value == null) throw new SQLDataException("batch step projection missing");\n    return value;' in text, 'full current source and exact identity alias')
    require(all(token not in text for token in ('connection.close(', 'connection.commit(', 'connection.rollback(', 'connection.setAutoCommit(', 'connection.setReadOnly(')), 'borrowed connection not owned')
    helper = texts[HELPER]
    require('primary == null\n        || (primary instanceof SQLException && !(secondary instanceof SQLException))) return true;' in helper, 'null/SQL cleanup priority')
    require('if (!(primary instanceof SQLException)) primary.addSuppressed(new BatchRepositoryException());\n    return false;' in helper, 'unknown primary fixed nonself secondary')
    require('BatchRunRepositoryのhistory/insert/replayed各Statement/ResultSet、abandon/finish Statement計8scope' in texts[DESIGN], 'explicit eight-scope approved contract')
    selected = [r for r in queue if r['path'] == PATH]
    require(len(selected) == 48 and Counter(r['rule'] for r in selected) == Counter(CloseResource=8, AvoidCatchingGenericException=32, DoNotThrowExceptionInFinally=8), 'all48 current retained warnings')
    result = []
    seen = set()
    for method, resource, alias, body, final, close, end in SITES:
        primary = 'rowFailure' if resource == 'rows' else 'statementFailure'
        require(f'present({resource});' in lines[alias - 1], 'exact alias resource')
        require(lines[alias - 2].strip() == 'try {' and lines[alias - 3].strip() == f'@Nullable Throwable {primary} = null;', 'immediate protected alias')
        for start in (body, close):
            require(lines[start - 1].strip() == '} catch (SQLException | RuntimeException | Error failure) {', 'exact closed catch set')
        require(lines[body].strip() == primary + ' = failure;' and lines[body + 1].strip() == 'throw failure;', 'same primary rethrow')
        fragment = '\n'.join(lines[final - 1:end])
        require(lines[final - 1].strip() == '} finally {' and f'if ({resource} != null)' in fragment and fragment.count(resource + '.close();') == 1, 'exact nullguard and direct close')
        require(f'if (JdbcResourceFailures.replace({primary}, failure)) throw failure;' in fragment, 'same primary and cleanup conditional throw')
        rows = [r for r in selected if int(r['attributes']['beginline']) in (alias, body, final, close)]
        require(len(rows) == 6, 'each reviewed scope six diagnostics')
        for row in rows:
            require(row['sourceSha256'] == PINS[PATH] and row['id'] not in seen, 'exact source and unique diagnostic')
            start, stop, value = span(text, row['attributes'])
            if row['rule'] == 'CloseResource':
                require(value in ('query', 'row') and int(row['attributes']['beginline']) == alias, 'alias token diagnostic')
            elif row['rule'] == 'AvoidCatchingGenericException':
                require(value in ('RuntimeException', 'Error') and int(row['attributes']['beginline']) in (body, close), 'two exact generic type spans per catch')
            else:
                require(int(row['attributes']['beginline']) == final and int(row['attributes']['endline']) == end and value.startswith('finally {'), 'exact finally extent')
            seen.add(row['id'])
            result.append(dict(**row, method=method, resource=resource, primaryVariable=primary,
                aliasLine=alias, bodyCatchLine=body, finallyLine=final, closeCatchLine=close, endLine=end,
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
    require(previous['actualExit'] == 0 and len(queue) == 929 and previous['remainingSelectedUnreferenced'] == 929, 'frozen selected queue, not whole unreviewed universe')
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
        priorUnreferenced=929, newlyPurposeReviewed=48, remainingSelectedUnreferenced=len(remaining),
        priorReferenced=562, combinedPurposeOrReferenceRows=562 + len(rows), ownershipScopes=8,
        status=STATUS, actualViolationCount=None, rawSuppressed=0, ruleChanged=False,
        productTestsExecuted=0, analyzerReexecuted=False, compilerExecuted=False,
        oldRuntimeTransferred=False, currentEightScopeDynamicQualification=False,
        sourceChanged=False, externalActions=0, actualDatabaseActions=0, actualVmActions=0,
        wholeF03Accepted=False, whole451Accepted=False, formalUpdated=False, newAccepted=0, effortPercent=None))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, purposeReviewed=len(rows), remaining=len(remaining))))


if __name__ == '__main__':
    main()
