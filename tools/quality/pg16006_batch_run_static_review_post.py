"""Independent line/token reconstruction of current48 purpose review; no Product loading."""
from collections import Counter
import copy
import json
import re
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg16004_batch_run_current_static_review as raw

PIN = '2e6c4240a6749477bf58ade99bb44701c382f0d4adb3c8cb0a5b0ad66348976d'
OUT = data.BASE / 'PG16006-batch-run-static-review-post-v1'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def assess(meta, reviewed, remaining, prior_queue, expected):
    require(meta['actualExit'] == 0 and meta['source'] == raw.SOURCE and meta['inputHashes'] == raw.PINS, 'fixed source and input hashes')
    require((meta['priorUnreferenced'], meta['newlyPurposeReviewed'], meta['remainingSelectedUnreferenced'], meta['priorReferenced'], meta['combinedPurposeOrReferenceRows'], meta['ownershipScopes']) == (929, 48, 881, 562, 610, 8), 'separate old references/new static purposes, not runtime')
    require(meta['status'] == 'MANUAL_PURPOSE_REVIEW_COMPLETE_DYNAMIC_UNQUALIFIED' and meta['actualViolationCount'] is None and meta['effortPercent'] is None, 'unknown dynamic/applicability/effort remains unknown')
    for field in ('ruleChanged', 'analyzerReexecuted', 'compilerExecuted', 'oldRuntimeTransferred', 'currentEightScopeDynamicQualification', 'sourceChanged', 'wholeF03Accepted', 'whole451Accepted', 'formalUpdated'):
        require(meta[field] is False, 'no authority/PASS/source mutation: ' + field)
    for field in ('rawSuppressed', 'productTestsExecuted', 'externalActions', 'actualDatabaseActions', 'actualVmActions', 'newAccepted'):
        require(type(meta[field]) is int and meta[field] == 0, 'exact zero not bool: ' + field)
    require(len(reviewed) == len({r['id'] for r in reviewed}) == 48, 'all distinct reviewed IDs')
    selected = {r['id']: r for r in prior_queue if r['path'] == raw.PATH}
    require(set(selected) == {r['id'] for r in reviewed}, 'complete original target IDs')
    for row in reviewed:
        old = selected[row['id']]
        require(all(row[k] == v for k, v in old.items()), 'all original warning data retained')
        for field, value in expected[row['id']].items():
            require(row[field] == value and type(row[field]) is type(value), 'exact independently reconstructed field: ' + field)
        require(row['reason'] == raw.REASONS[row['rule']] and len(row['reason']) > 100, 'explicit reviewed reason with limitations')
        require(row['status'] == meta['status'] and row['actualViolation'] is None and row['rawRetained'] is True and row['productTestsExecuted'] == 0, 'per-row static/raw boundaries')
        require(all(row[field] is False for field in ('currentDynamicQualification', 'typeResolutionProven', 'actualCloseCountProven', 'actualSqlPostconditionsProven')), 'not actual execution/type resolution')
    require(remaining == [r for r in prior_queue if r['id'] not in selected], 'all other 881 rows byte-structure retained')


def main():
    invocation = capture(__file__)
    require(not OUT.exists(), 'new-only')
    p = data.read_checked(raw.OUT / 'manifest.json', PIN)
    value = data.read_checked(raw.OUT / 'review.json', p['reviewSha256'])
    rows = value['rows']
    remaining = data.read_checked(raw.OUT / 'remaining-selected-review-queue.json', p['queueSha256'])
    prior = data.read_checked(raw.PRIOR / 'manifest.json', raw.PRIOR_PIN)
    queue = data.read_checked(raw.PRIOR / 'remaining-selected-review-queue.json', prior['queueSha256'])
    require(value['source'] == raw.SOURCE and value['inputHashes'] == p['inputHashes'] == raw.PINS, 'review and manifest same source')
    require(p['priorManifestSha256'] == raw.PRIOR_PIN and p['priorQueueSha256'] == prior['queueSha256'], 'original frozen queue')
    for path, digest in raw.PINS.items():
        require(data.sha((data.ROOT / path).read_bytes()) == digest, 'actual reviewed bytes retained')
    text = (data.ROOT / raw.PATH).read_text()
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    method_starts = []
    for method, signature in [('finish', 'public void finish('), ('history', 'private List<History> history('), ('abandon', 'private void abandon('), ('insert', 'private BatchStepAttempt insert('), ('replayed', 'private boolean replayed(')]:
        require(text.count(signature) == 1, 'unique actual reviewed method boundary')
        method_starts.append((text.index(signature), method))
    block_by_line = {}
    close_calls = Counter()
    for match in re.finditer(r'if \(JdbcResourceFailures\.replace\((statementFailure|rowFailure), failure\)\) throw failure;', text):
        number = text[:match.start()].count('\n') + 1
        primary = match.group(1)
        resource = 'rows' if primary == 'rowFailure' else 'statement'
        final = max(i + 1 for i, line in enumerate(lines[:number]) if line.strip() == '} finally {')
        close = number - 1
        body = max(i + 1 for i, line in enumerate(lines[:final - 1]) if line.strip() == '} catch (SQLException | RuntimeException | Error failure) {')
        alias = max(i + 1 for i, line in enumerate(lines[:body - 1]) if f'present({resource});' in line)
        require(lines[body].strip() == primary + ' = failure;' and lines[body + 1].strip() == 'throw failure;', 'same recorded primary identity')
        require(lines[close - 1].strip() == '} catch (SQLException | RuntimeException | Error failure) {' and lines[number - 3].strip() == resource + '.close();', 'actual direct close and exact exception set')
        method = max((position, name) for position, name in method_starts if position < match.start())[1]
        end = number + 3
        info = dict(method=method, resource=resource, primaryVariable=primary, aliasLine=alias, bodyCatchLine=body, finallyLine=final, closeCatchLine=close, endLine=end)
        for line_number in (alias, body, final, close):
            require(line_number not in block_by_line, 'unique diagnostic origin per scope')
            block_by_line[line_number] = info
        close_calls[(method, resource)] += 1
    require(len(close_calls) == sum(close_calls.values()) == 8, 'all eight direct resource close clauses')
    expected = {}
    for row in queue:
        if row['path'] != raw.PATH:
            continue
        a = row['attributes']
        start_line, end_line = int(a['beginline']), int(a['endline'])
        start = offsets[start_line - 1] + int(a['begincolumn']) - 1
        stop = offsets[end_line - 1] + int(a['endcolumn']) - 1
        token = text[start:stop]
        info = block_by_line[start_line]
        if row['rule'] == 'CloseResource':
            require(token == ('row' if info['resource'] == 'rows' else 'query') and start_line == info['aliasLine'], 'exact actual identity alias token')
        elif row['rule'] == 'AvoidCatchingGenericException':
            require(token in ('RuntimeException', 'Error') and start_line in (info['bodyCatchLine'], info['closeCatchLine']), 'generic token tied to recorded body/close')
        else:
            require(row['rule'] == 'DoNotThrowExceptionInFinally' and token.startswith('finally {') and start_line == info['finallyLine'] and end_line == info['endLine'], 'exact protected finally extent')
        expected[row['id']] = dict(**info, spanStart=start, spanEndExclusive=stop, spanSha256=data.sha(token.encode()))
    assess(p, rows, remaining, queue, expected)
    negatives = []
    for field, value in [('source', '0' * 40), ('newlyPurposeReviewed', 929), ('remainingSelectedUnreferenced', 0), ('combinedPurposeOrReferenceRows', 1491), ('productTestsExecuted', 48), ('wholeF03Accepted', True), ('currentEightScopeDynamicQualification', True), ('oldRuntimeTransferred', True), ('actualViolationCount', 0), ('effortPercent', 100), ('rawSuppressed', True)]:
        bad = copy.deepcopy(p)
        bad[field] = value
        try:
            assess(bad, rows, remaining, queue, expected)
        except ValueError:
            negatives.append(field)
        else:
            raise ValueError('unrejected metadata mutation: ' + field)
    for field, value in [('method', 'unreviewed'), ('resource', 'connection'), ('primaryVariable', 'other'), ('sourceSha256', '0' * 64), ('spanSha256', '0' * 64), ('finallyLine', 0), ('rawRetained', False), ('typeResolutionProven', True), ('actualCloseCountProven', True), ('status', 'PASS'), ('reason', 'reviewed')]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        try:
            assess(p, bad, remaining, queue, expected)
        except ValueError:
            negatives.append('row-' + field)
        else:
            raise ValueError('unrejected row mutation: ' + field)
    for label, bad_rows, bad_remaining in [('missing', rows[:-1], remaining), ('duplicate', rows[1:] + [rows[1]], remaining), ('other-queue-erased', rows, remaining[:-1])]:
        try:
            assess(p, bad_rows, bad_remaining, queue, expected)
        except ValueError:
            negatives.append(label)
        else:
            raise ValueError('unrejected structural mutation: ' + label)
    verify(p['invocation'])
    verify(invocation)
    OUT.mkdir()
    data.write(OUT / 'manifest.json', dict(actualExit=0, invocation=invocation, source=raw.SOURCE,
        parentManifestSha256=PIN, reviewSha256=p['reviewSha256'], priorQueueSha256=p['priorQueueSha256'],
        newlyPurposeReviewed=48, ownershipScopes=8, remainingSelectedUnreferenced=881,
        independentMetadataNegativeVectors=len(negatives), negativeLabels=negatives,
        productTestsExecuted=0, currentEightScopeDynamicQualification=False, wholeF03Accepted=False,
        whole451Accepted=False, newAccepted=0, formalUpdated=False, effortPercent=None, externalActions=0))
    print(data.sha((OUT / 'manifest.json').read_bytes()))
    print(json.dumps(dict(actualExit=0, independentMetadataNegativeVectors=len(negatives), reviewed=48)))


if __name__ == '__main__':
    main()
